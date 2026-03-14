import threading
from collections import deque
from typing import Any
import logging


class SharedQueue:
    """
    A thread-safe bounded queue demonstrating the wait/notify mechanism.

    This class uses a `collections.deque` for underlying storage to provide O(1) 
    appends and pops. Concurrency is managed via a single `threading.Lock` and 
    two associated `threading.Condition` objects (`not_empty` and `not_full`) to 
    efficiently block when capacity limits are hit without busy-waiting.
    """

    def __init__(self, capacity: int = 10):
        if capacity <= 0:
            raise ValueError("Queue capacity must be positive.")
        self.capacity = capacity
        self.queue = deque()
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def enqueue(self, item: Any, timeout: float = None) -> bool:
        """
        Put an item into the queue. Blocks if queue is full.
        Returns True if successful, False if timed out.
        """
        with self.not_full:
            while len(self.queue) >= self.capacity:
                logging.debug(
                    f"Queue is full ({self.capacity}). Waiting to enqueue...")
                # Wait until not full, or timeout
                if not self.not_full.wait(timeout):
                    return False
            self.queue.append(item)
            self.not_empty.notify()
            return True

    def dequeue(self, timeout: float = None) -> Any:
        """
        Get an item from the queue. Blocks if queue is empty.
        Returns item if successful, None if timed out.
        """
        with self.not_empty:
            while len(self.queue) == 0:
                logging.debug("Queue is empty. Waiting to dequeue...")
                if not self.not_empty.wait(timeout):
                    return None
            item = self.queue.popleft()
            self.not_full.notify()
            return item

    def get_status(self) -> dict:
        with self.lock:
            return {
                "size": len(self.queue),
                "capacity": self.capacity,
                "is_full": len(self.queue) >= self.capacity,
                "is_empty": len(self.queue) == 0,
            }
