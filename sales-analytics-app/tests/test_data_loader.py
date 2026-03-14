"""
Test Suite for SalesDataLoader and CSV interactions.
Tests string parsing, invalid fields safely, and explicit missing file handling.
"""
import pytest
import os
from tempfile import NamedTemporaryFile
from src.intuit_sales_analytics.data_loader import SalesDataLoader


def test_successful_load():
    """Verify loader reads correct fields to correct datatypes parsing successfully."""
    print("\n--- TEST: Valid Data Parsing ---")
    with NamedTemporaryFile(mode='w', suffix=".csv", delete=False) as tmp:
        tmp.write(
            "transaction_id,date,region,salesperson,product_category,quantity,unit_price\n")
        tmp.write("TX01,2026-01-01,North,Alice,Electronics,2,999.50\n")
        tmp_name = tmp.name

    loader = SalesDataLoader(tmp_name)
    records = loader.load_data()

    assert len(records) == 1
    assert records[0].transactionId == "TX01"
    assert records[0].unitPrice == 999.50
    assert records[0].totalAmount == 1999.0

    os.remove(tmp_name)
    print("✓ PASSED: CSV safely mapped to properties.")


def test_missing_file():
    """Verify aggressive tracking for FileNotFound exceptions during setup execution."""
    print("\n--- TEST: Missing File Exceptions ---")
    loader = SalesDataLoader("does_not_exist_abc.csv")
    with pytest.raises(FileNotFoundError):
        loader.load_data()
    print("✓ PASSED: Expected errors properly bubbled mapping Intuit guidelines.")


def test_malformed_csv_rows(caplog):
    """Ensure malformed string types, empty objects, and negative values safely bubble instead of breaking load parsing."""
    print("\n--- TEST: Invalid Formats Skipping Logic ---")
    with NamedTemporaryFile(mode='w', suffix=".csv", delete=False) as tmp:
        tmp.write(
            "transaction_id,date,region,salesperson,product_category,quantity,unit_price\n")
        tmp.write("TX01,2026-01-01,North,Alice,Electronics,2,100.50\n")
        # Malformed date string bounds
        tmp.write("TX02,bad_date,South,Bob,Clothing,5,20.00\n")
        # Malformed Integer types
        tmp.write("TX03,2026-01-15,North,Alice,Electronics,BAD_QTY,500.00\n")
        tmp.write("TX04,,East,Charlie,Tech,,10.00\n")  # Empty logic
        tmp_name = tmp.name

    loader = SalesDataLoader(tmp_name)
    records = loader.load_data()

    # Only 1 record should be loaded successfully bypassing logic boundaries natively
    assert len(records) == 1
    assert records[0].transactionId == "TX01"

    # Ensure warnings actually flagged into the system streams
    assert "Skipping malformed row" in caplog.text

    os.remove(tmp_name)
    print("✓ PASSED: Corrupted items appropriately flagged safely via logs isolating exceptions inherently.")
