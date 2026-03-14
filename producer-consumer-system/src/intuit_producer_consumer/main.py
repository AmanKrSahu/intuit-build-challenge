import os
import logging
import sys
from dotenv import load_dotenv

from src.intuit_producer_consumer.models import Item
from src.intuit_producer_consumer.manager import DataTransferManager


def configure_logging():
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("output/application.log",
                                mode="w", encoding="utf-8")
        ]
    )


def main():
    # Load environment variables from .env
    load_dotenv()
    configure_logging()

    # 1. Prepare sample items
    try:
        NUM_ITEMS = int(os.getenv("NUM_ITEMS", 20))
    except (TypeError, ValueError):
        NUM_ITEMS = 20

    source_items = [Item(id=i, data=f"Payload {i}")
                    for i in range(1, NUM_ITEMS + 1)]
    destination_items = []

    # 2. Initialize manager
    try:
        QUEUE_CAPACITY = int(os.getenv("QUEUE_CAPACITY", 5))
    except (TypeError, ValueError):
        QUEUE_CAPACITY = 5

    manager = DataTransferManager(
        source_container=source_items,
        destination_container=destination_items,
        capacity=QUEUE_CAPACITY
    )

    # 3. Start Transfer
    manager.start_transfer()

    # Optional: Periodic status output
    while manager.producer.is_alive() or manager.consumer.is_alive():
        status = manager.get_queue_status()
        logging.info(
            f"MainThread - Queue Status: {status['size']}/{status['capacity']} items")
        manager.wait_for_completion(timeout=0.2)

    # Wait to ensure final shutdown
    success = manager.wait_for_completion(timeout=5.0)

    if not success:
        logging.error("Transfer timed out. Issuing stop command.")
        manager.stop_transfer()
    else:
        logging.info("Transfer completed successfully.")

    logging.info(
        f"Total items transferred: {len(destination_items)} / {NUM_ITEMS}")


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(
        description="Producer-Consumer Data Transfer Challenge")
    parser.add_argument("--run-tests", action="store_true",
                        help="Execute the pytest suite instead of the main application")
    args = parser.parse_args()

    if args.run_tests:
        print("Starting Automated Test Suite Execution...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/"])
    else:
        main()
