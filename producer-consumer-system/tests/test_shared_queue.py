"""
Test Suite for Producer-Consumer SharedQueue.
Tests thread synchronization and blocking behavior gracefully mapped back to Intuit instructions.
"""
import pytest
import threading
import time
from src.intuit_producer_consumer.shared_queue import SharedQueue


def test_queue_initialization():
    """Verify queue is properly initialized with correct capacity bounds."""
    queue = SharedQueue(capacity=5)
    assert queue.capacity == 5
    assert queue.get_status()["size"] == 0
    assert queue.get_status()["is_empty"] is True
    assert queue.get_status()["is_full"] is False


def test_invalid_capacity():
    """Test that capacities <= 0 raise ValueError."""
    with pytest.raises(ValueError):
        SharedQueue(capacity=0)
    with pytest.raises(ValueError):
        SharedQueue(capacity=-5)


def test_enqueue_dequeue_basic():
    """Test standard single-thread sequential put/get."""
    queue = SharedQueue(capacity=2)

    # Enqueue
    assert queue.enqueue("Item1") is True
    assert queue.get_status()["size"] == 1

    # Dequeue
    item = queue.dequeue()
    assert item == "Item1"
    assert queue.get_status()["size"] == 0


def test_fifo_order():
    """Test that queue explicitly maintains FIFO order for inserted items."""
    queue = SharedQueue(capacity=5)
    items = [1, 2, 3, 4, 5]

    for item in items:
        queue.enqueue(item)

    for expected_item in items:
        actual_item = queue.dequeue()
        assert actual_item == expected_item

    assert queue.get_status()["is_empty"] is True


def test_queue_full_blocking():
    """Verify queue accurately blocks and responds to `not_full` bound conditions."""
    queue = SharedQueue(capacity=1)
    queue.enqueue("Hold")
    assert queue.get_status()["is_full"] is True

    # Should timeout because queue is full (capacity=1)
    start_time = time.time()
    success = queue.enqueue("TimeoutItem", timeout=0.1)
    duration = time.time() - start_time

    assert success is False
    assert duration >= 0.1
    assert queue.get_status()["size"] == 1


def test_queue_empty_blocking():
    """Verify getting responds to `not_empty` boundaries."""
    queue = SharedQueue(capacity=5)
    assert queue.get_status()["is_empty"] is True

    # Should timeout because queue is empty
    start_time = time.time()
    item = queue.dequeue(timeout=0.1)
    duration = time.time() - start_time

    assert item is None
    assert duration >= 0.1


def test_concurrent_access():
    """Spin up multiple threads verifying lock orchestration integrity."""
    queue = SharedQueue(capacity=10)
    results = []

    def producer_worker():
        for i in range(50):
            queue.enqueue(i)

    def consumer_worker():
        for _ in range(50):
            item = queue.dequeue(timeout=1.0)
            if item is not None:
                results.append(item)

    prod_thread = threading.Thread(target=producer_worker)
    cons_thread = threading.Thread(target=consumer_worker)

    prod_thread.start()
    cons_thread.start()

    prod_thread.join()
    cons_thread.join()

    assert len(results) == 50
    assert sum(results) == sum(range(50))
    assert queue.get_status()["size"] == 0


def test_wait_notify_mechanism_direct():
    """Test that the implicit wait/notify bounding mechanism natively unlocks threads."""
    queue = SharedQueue(capacity=1)

    # Fill queue
    queue.enqueue("item1")

    put_blocked = threading.Event()
    put_completed = threading.Event()

    def blocking_put():
        put_blocked.set()
        queue.enqueue("item2")  # Will block here
        put_completed.set()

    thread = threading.Thread(target=blocking_put)
    thread.start()

    # Wait for thread to theoretically block
    put_blocked.wait(timeout=1)
    time.sleep(0.1)

    # Verify the thread is currently stopped at enqueue
    assert put_completed.is_set() is False

    # Native unblock by triggering `notify` over condition queue
    queue.dequeue()

    # Verify put completes as condition unlocked
    thread.join(timeout=1)
    assert put_completed.is_set() is True
