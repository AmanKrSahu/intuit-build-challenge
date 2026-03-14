import threading
import logging
import time
from typing import List

from .models import Item
from .shared_queue import SharedQueue


class Consumer(threading.Thread):
    """
    A thread that dequeues items from a SharedQueue and places them into a destination container.

    Processing loop continues until the destination container reaches `expected_count` or 
    a manual shutdown is requested. If the queue is empty, the Consumer will block according 
    to the SharedQueue's internal bounds and periodically re-check the shutdown flag.
    """

    def __init__(self, shared_queue: SharedQueue, destination_container: List[Item], expected_count: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_queue = shared_queue
        self.destination_container = destination_container
        self.expected_count = expected_count
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        logging.info(f"{self.name} started.")
        while len(self.destination_container) < self.expected_count and not self._stop_event.is_set():
            # Dequeue with timeout to check for stop signal
            item = self.shared_queue.dequeue(timeout=0.5)
            if item is not None:
                # Simulate processing
                time.sleep(0.02)
                self.destination_container.append(item)
                logging.info(f"{self.name} consumed {item}")

        logging.info(f"{self.name} finished.")
