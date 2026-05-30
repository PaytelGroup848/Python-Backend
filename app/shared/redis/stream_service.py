
import json
import logging

from redis.exceptions import (
    ConnectionError
)

from app.shared.redis.client import (
    redis_client
)


logger = logging.getLogger(
    __name__
)


class RedisStreamService:

    # =========================
    # PUBLISH EVENT
    # =========================

    async def publish(

        self,

        stream_name: str,

        data: dict,
    ):

        try:

            await redis_client.xadd(

                stream_name,

                {
                    "data":
                        json.dumps(data)
                }
            )

        except Exception as e:

            logger.exception(
                f"Redis publish failed: {e}"
            )

            raise

    # =========================
    # CONSUME EVENTS
    # =========================

    async def consume(

        self,

        stream_name: str,

        group_name: str,

        consumer_name: str,
    ):

        try:

            # =========================
            # CREATE GROUP IF NOT EXISTS
            # =========================

            try:

                await redis_client.xgroup_create(

                    stream_name,

                    group_name,

                    id="0",

                    mkstream=True,
                )

                logger.info(
                    f"Created stream group: "
                    f"{group_name}"
                )

            except Exception:

                pass

            # =========================
            # READ EVENTS
            # =========================

            response = (
                await redis_client.xreadgroup(

                    group_name,

                    consumer_name,

                    streams={
                        stream_name: ">"
                    },

                    count=1,

                    block=5000,
                )
            )

            return response

        except ConnectionError as e:

            logger.warning(
                f"Redis connection closed: {e}"
            )

            return []

        except Exception as e:

            logger.exception(
                f"Redis consume failed: {e}"
            )

            return []

    # =========================
    # PUBSUB SUBSCRIBE
    # =========================

    async def subscribe(

        self,

        channel: str,
    ):

        try:

            pubsub = (
                redis_client.pubsub()
            )

            await pubsub.subscribe(
                channel
            )

            logger.info(
                f"Subscribed to channel: "
                f"{channel}"
            )

            return pubsub

        except Exception as e:

            logger.exception(
                f"Redis subscribe failed: {e}"
            )

            raise


redis_stream_service = (
    RedisStreamService()
)

