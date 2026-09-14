import asyncio
import json
import logging
import signal
import sys
from typing import Set

from app.shared.redis.stream_service import redis_stream_service
from app.shared.redis.client import redis_client
from app.shared.constants.streams import (
    CHAT_REQUEST_STREAM,
    CHAT_RESPONSE_STREAM,
)
from app.services.agent_service import run_agent
from app.db.database import AsyncSessionLocal
from app.models.message import Message
from app.models.conversation import Conversation
from app.core.queues.queue_service import queue_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chat_request_worker")

GROUP_NAME = "chat_workers"
CONSUMER_NAME = f"chat_worker_{sys.platform}"

# Concurrency & Traffic Control
CONCURRENCY_LIMIT = 50
SEMAPHORE = asyncio.Semaphore(CONCURRENCY_LIMIT)
ACTIVE_TASKS: Set[asyncio.Task] = set()
SHUTDOWN_EVENT = asyncio.Event()


async def handle_single_chat_request(message_id: str, payload: dict):
    """
    Handles a single chat request asynchronously within the bounded concurrency pool.
    Flow:
      1. Acquire semaphore slot
      2. Stream tokens to Redis Pub/Sub (ws:req:{request_id})
      3. Save full response to PostgreSQL DB
      4. XACK Redis Stream message
      5. Emit 'done' event to Redis Pub/Sub
    """
    async with SEMAPHORE:
        request_id = None
        conversation_id = None
        user_id = None

        try:
            raw_data = payload.get("data")
            if not raw_data:
                logger.warning(f"Empty payload for message {message_id}")
                await redis_client.xack(CHAT_REQUEST_STREAM, GROUP_NAME, message_id)
                return

            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            request_id = data.get("request_id")
            user_id = str(data.get("user_id"))
            query = data.get("query") or data.get("message")
            conversation_id = data.get("conversation_id")
            assistant_id = data.get("assistant_id")
            aspect_ratio = data.get("aspect_ratio") or "1024x1024"
            web_search = bool(data.get("web_search", False))

            if not query:
                raise ValueError("Query is required")

            channel_name = f"ws:req:{request_id}"

            # Emit initial 'start' event to Pub/Sub
            try:
                await redis_client.publish(
                    channel_name,
                    json.dumps({
                        "type": "start",
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                    })
                )
            except Exception as start_err:
                logger.warning(f"Failed to publish start event: {start_err}")

            # Check if cancelled before execution begins
            if conversation_id:
                if await redis_client.get(f"chat:stopped:{conversation_id}"):
                    logger.info(f"Chat cancelled before start for conv={conversation_id}")
                    await redis_client.delete(f"chat:stopped:{conversation_id}")
                    await redis_client.xack(CHAT_REQUEST_STREAM, GROUP_NAME, message_id)
                    return

            # Token streaming callback for run_agent
            async def stream_callback(event: dict):
                # Check user cancellation mid-stream
                if conversation_id:
                    if await redis_client.get(f"chat:stopped:{conversation_id}"):
                        raise asyncio.CancelledError(f"User stopped conversation {conversation_id}")

                pub_payload = {
                    "request_id": request_id,
                    "conversation_id": conversation_id,
                    **event
                }
                try:
                    await redis_client.publish(channel_name, json.dumps(pub_payload))
                except Exception as pub_err:
                    logger.warning(f"Pub/sub chunk publish failed: {pub_err}")

            # Run agent with true token streaming callback
            response = await run_agent(
                query=query,
                session_id=str(conversation_id),
                user_id=int(user_id) if user_id and user_id.isdigit() else 1,
                assistant_id=int(assistant_id) if assistant_id is not None else None,
                user_role="employee",
                user_department="general",
                aspect_ratio=aspect_ratio,
                web_search=web_search,
                stream_handler=stream_callback,
            )

            response_text = response["response"] if isinstance(response, dict) else str(response)

            # Check cancellation post-generation
            if conversation_id and await redis_client.get(f"chat:stopped:{conversation_id}"):
                logger.info(f"Generation cancelled post-run for conv={conversation_id}")
                await redis_client.delete(f"chat:stopped:{conversation_id}")
                await redis_client.xack(CHAT_REQUEST_STREAM, GROUP_NAME, message_id)
                await redis_client.publish(
                    channel_name,
                    json.dumps({
                        "type": "stopped",
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                    })
                )
                return

            # STEP 1: Persist assistant message & conversation audit record to PostgreSQL DB
            if conversation_id and response_text:
                try:
                    async with AsyncSessionLocal() as db:
                        assistant_msg = Message(
                            conversation_id=int(conversation_id),
                            role="assistant",
                            content=response_text
                        )
                        db.add(assistant_msg)

                        conv_record = Conversation(
                            user_id=int(user_id) if user_id and str(user_id).isdigit() else None,
                            session_id=str(conversation_id),
                            query=query,
                            response=response_text,
                            model_used=str(assistant_id or "Assistant")
                        )
                        db.add(conv_record)

                        await db.commit()
                        logger.info(f"Persisted response to DB for conv={conversation_id}")
                except Exception as db_err:
                    logger.error(f"Failed to persist response to DB: {db_err}")
                    # If DB persistence fails, we do NOT ACK so job can retry or be inspected
                    raise db_err

            # STEP 2: ACK Redis Stream message ONLY after DB persistence succeeds
            try:
                await redis_client.xack(
                    CHAT_REQUEST_STREAM,
                    GROUP_NAME,
                    message_id
                )
            except Exception as ack_err:
                logger.exception(f"Redis ACK failed for message {message_id}: {ack_err}")

            # STEP 3: Emit final 'done' event to Pub/Sub to close the streaming cycle
            try:
                await redis_client.publish(
                    channel_name,
                    json.dumps({
                        "type": "done",
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                        "response": response_text
                    })
                )
            except Exception as done_err:
                logger.warning(f"Failed to publish done event: {done_err}")

            # Backwards compatibility event to CHAT_RESPONSE_STREAM
            try:
                await redis_stream_service.publish(
                    CHAT_RESPONSE_STREAM,
                    {
                        "request_id": request_id,
                        "conversation_id": conversation_id,
                        "type": "message",
                        "response": response_text
                    }
                )
            except Exception:
                pass

        except asyncio.CancelledError:
            logger.info(f"Chat request {request_id} was cancelled by user.")
            if request_id:
                try:
                    await redis_client.publish(
                        f"ws:req:{request_id}",
                        json.dumps({
                            "type": "stopped",
                            "request_id": request_id,
                            "conversation_id": conversation_id
                        })
                    )
                except Exception:
                    pass
            try:
                await redis_client.xack(CHAT_REQUEST_STREAM, GROUP_NAME, message_id)
            except Exception:
                pass

        except Exception as exc:
            logger.exception(f"Chat request processing failed for {request_id}: {exc}")
            if request_id:
                try:
                    await redis_client.publish(
                        f"ws:req:{request_id}",
                        json.dumps({
                            "type": "error",
                            "request_id": request_id,
                            "conversation_id": conversation_id,
                            "message": str(exc)
                        })
                    )
                except Exception:
                    pass
            # ACK so bad request does not stall the worker queue indefinitely
            try:
                await redis_client.xack(CHAT_REQUEST_STREAM, GROUP_NAME, message_id)
            except Exception:
                pass
        finally:
            if user_id and user_id != "None":
                try:
                    await queue_service.decrement(str(user_id))
                except Exception as dec_err:
                    logger.warning(f"Failed to decrement queue for user {user_id}: {dec_err}")


async def process_chat_requests():
    """
    Continuous consumer loop reading from Redis Stream and dispatching to
    the bounded asyncio task pool. Non-blocking with zero stalling.
    """
    logger.info(f"Chat request worker started. Concurrency limit={CONCURRENCY_LIMIT}")

    # Ensure stream group exists
    try:
        await redis_client.xgroup_create(
            CHAT_REQUEST_STREAM,
            GROUP_NAME,
            id="0",
            mkstream=True
        )
        logger.info(f"Initialized stream group {GROUP_NAME}")
    except Exception:
        pass

    while not SHUTDOWN_EVENT.is_set():
        try:
            # Read up to 10 events at once, non-blocking with 2000ms timeout
            response = await redis_client.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                streams={CHAT_REQUEST_STREAM: ">"},
                count=10,
                block=2000
            )

            if not response:
                await asyncio.sleep(0.05)
                continue

            for stream_entry in response:
                messages = stream_entry[1]
                for message in messages:
                    message_id = message[0]
                    payload = message[1]

                    # Dispatch into bounded task pool without blocking the consumer loop
                    task = asyncio.create_task(
                        handle_single_chat_request(message_id, payload)
                    )
                    ACTIVE_TASKS.add(task)
                    task.add_done_callback(ACTIVE_TASKS.discard)

        except asyncio.CancelledError:
            logger.info("Main worker loop cancelled.")
            break
        except Exception as loop_err:
            logger.exception(f"Worker loop error: {loop_err}")
            await asyncio.sleep(1)

    logger.info(f"Worker shutting down. Awaiting {len(ACTIVE_TASKS)} active tasks...")
    if ACTIVE_TASKS:
        await asyncio.gather(*ACTIVE_TASKS, return_exceptions=True)
    logger.info("All worker tasks completed. Shutdown complete.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda: SHUTDOWN_EVENT.set())
        except (NotImplementedError, AttributeError):
            pass

    try:
        loop.run_until_complete(process_chat_requests())
    except KeyboardInterrupt:
        logger.info("Worker stopped by KeyboardInterrupt.")
