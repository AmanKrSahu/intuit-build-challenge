"""
Test Suite for DataTransferManager and Thread Orchestration.
Tests integration across all layers checking data immutability and precise stopping heuristics based on Intuit references.
"""
import pytest
import time
from src.intuit_producer_consumer.models import Item
from src.intuit_producer_consumer.manager import DataTransferManager


def test_successful_transfer():
    """Verify standard end-to-end execution of a complete thread pool transfer payload."""
    source = [Item(id=i, data=f"Data {i}") for i in range(10)]
    destination = []

    manager = DataTransferManager(
        source_container=source,
        destination_container=destination,
        capacity=3
    )

    manager.start_transfer()
    success = manager.wait_for_completion(timeout=5.0)

    assert success is True
    assert len(destination) == 10

    # Check data integrity is identical after transfer
    for i in range(10):
        assert destination[i].id == source[i].id
        assert destination[i].data == source[i].data


def test_premature_stop():
    """Verify threads gracefully react and shutdown safely when interrupted prematurely during massive loads."""
    source = [Item(id=i, data=f"Data {i}") for i in range(1000)]
    destination = []

    manager = DataTransferManager(
        source_container=source,
        destination_container=destination,
        capacity=5
    )

    manager.start_transfer()
    # Immediately stop via orchestrated `.stop_transfer()` trigger
    manager.stop_transfer()

    # Wait for natural thread breakdown
    manager.wait_for_completion(timeout=2.0)

    # Should not have processed all items due to premature stop
    assert len(destination) < 1000
    assert not manager.producer.is_alive()
    assert not manager.consumer.is_alive()


def test_timeout_on_completion():
    """Verify the manager accurately responds and flags a timeout warning if threads are deadlocked or infinite."""
    source = [Item(id=i, data=f"Data {i}") for i in range(1000)]
    destination = []

    # Low latency capacity + huge payload sizes will definitely delay processing times >0.05 seconds natively
    manager = DataTransferManager(
        source_container=source,
        destination_container=destination,
        capacity=1
    )

    manager.start_transfer()
    # Expect false on wait due to strictly constrained timeouts forcing native `join` yields
    success = manager.wait_for_completion(timeout=0.01)

    assert success is False

    # Cleanup execution cleanly
    manager.stop_transfer()
    manager.wait_for_completion(timeout=2.0)


def test_empty_source_handling():
    """Verify that an explicitly empty source container safely processes without hanging or throwing errors."""
    print("\n--- TEST: Empty Source Container ---")
    source = []
    destination = []

    manager = DataTransferManager(
        source_container=source,
        destination_container=destination,
        capacity=5
    )

    manager.start_transfer()
    success = manager.wait_for_completion(timeout=2.0)

    assert success is True
    assert len(destination) == 0
    assert not manager.producer.is_alive()
    assert not manager.consumer.is_alive()
    print("✓ PASSED: Empty source resolves immediately.")


def test_thread_naming():
    """Verify threads spawned by Manager are accurately named for profiling metrics."""
    print("\n--- TEST: Thread Naming ---")
    source = [Item(id=i, data=f"Data {i}") for i in range(5)]
    destination = []

    manager = DataTransferManager(
        source_container=source,
        destination_container=destination,
        capacity=3
    )

    # Validate names BEFORE starting (usually set during Thread initialization)
    assert manager.producer.name == "ProducerThread"
    assert manager.consumer.name == "ConsumerThread"
    print("✓ PASSED: Thread naming properly tagged.")
