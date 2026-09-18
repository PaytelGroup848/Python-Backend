import asyncio
import logging
import signal
import sys

from app.services.guest_refund_worker import run_refund_worker_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("guest_refund_worker")

SHUTDOWN_EVENT = asyncio.Event()


def handle_exit_signal(sig, frame):
    logger.info(f"Received exit signal {sig}, initiating graceful shutdown...")
    SHUTDOWN_EVENT.set()


async def main():
    logger.info("Starting standalone Guest Refund DLQ Worker process...")

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, handle_exit_signal)
        except (ValueError, AttributeError):
            pass

    try:
        await run_refund_worker_loop(poll_interval=5.0, stop_event=SHUTDOWN_EVENT)
    except asyncio.CancelledError:
        logger.info("Refund worker main loop cancelled.")
    finally:
        logger.info("Guest Refund DLQ Worker shut down cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
