import logging
import time
from typing import List

from .models import Item
from .shared_queue import SharedQueue
from .producer import Producer
from .consumer import Consumer


class DataTransferManager:
    """
    Manages the lifecycle of producer and consumer threads.
    """

    def __init__(self, source_container: List[Item], destination_container: List[Item], capacity: int = 10):
        self.source_container = source_container
        self.destination_container = destination_container
        self.shared_queue = SharedQueue(capacity=capacity)

        self.producer = Producer(
            source_container=self.source_container,
            shared_queue=self.shared_queue,
            name="ProducerThread"
        )
        self.consumer = Consumer(
            shared_queue=self.shared_queue,
            destination_container=self.destination_container,
            expected_count=len(self.source_container),
            name="ConsumerThread"
        )

    def start_transfer(self):
        logging.info("Starting Data Transfer...")
        self.producer.start()
        self.consumer.start()

    def stop_transfer(self):
        logging.info("Stopping Data Transfer prematurely...")
        self.producer.stop()
        self.consumer.stop()

        # Wait up to 2 seconds for threads to stop gracefully
        self.producer.join(timeout=2.0)
        self.consumer.join(timeout=2.0)

    def get_queue_status(self) -> dict:
        return self.shared_queue.get_status()

    def wait_for_completion(self, timeout: float = None) -> bool:
        """
        Wait for both threads to finish.
        Returns True if successful, False if timed out.
        """
        start_time = time.time()

        self.producer.join(timeout)
        if self.producer.is_alive():
            return False

        remaining_timeout = timeout - \
            (time.time() - start_time) if timeout else None
        if remaining_timeout is not None and remaining_timeout < 0:
            return False

        self.consumer.join(remaining_timeout)
        if self.consumer.is_alive():
            return False

        return True
