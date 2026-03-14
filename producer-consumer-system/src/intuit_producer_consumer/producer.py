import threading
import logging
import time
from typing import List

from .models import Item
from .shared_queue import SharedQueue


class Producer(threading.Thread):
    """
    A thread that consumes items from a source container and enqueues them into a SharedQueue.

    This class supports graceful shutdown via a `threading.Event` flag. In the event the queue 
    is full, the Producer will block according to the SharedQueue's internal wait bounds and 
    periodically re-check the shutdown event.
    """

    def __init__(self, source_container: List[Item], shared_queue: SharedQueue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_container = source_container
        self.shared_queue = shared_queue
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        logging.info(f"{self.name} started.")
        for item in self.source_container:
            if self._stop_event.is_set():
                logging.info(f"{self.name} stopped prematurely.")
                break

            # Simulate work
            time.sleep(0.01)

            # Enqueue with timeout to allow graceful shutdown
            while not self._stop_event.is_set():
                if self.shared_queue.enqueue(item, timeout=0.5):
                    logging.info(f"{self.name} produced {item}")
                    break
        logging.info(f"{self.name} finished.")
