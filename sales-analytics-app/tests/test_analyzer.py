"""
Test Suite for SalesAnalyzer functional methods.
Tests data analytics queries, handling of empty datasets, and sorting configurations.
"""
import pytest
from datetime import date
from src.intuit_sales_analytics.models import SaleRecord
from src.intuit_sales_analytics.analyzer import SalesAnalyzer


@pytest.fixture
def sample_records():
    return [
        SaleRecord("T1", date(2026, 1, 1), "North",
                   "Alice", "Tech", 2, 100.0, 200.0),
        SaleRecord("T2", date(2026, 1, 15), "South",
                   "Bob", "Tech", 1, 300.0, 300.0),
        SaleRecord("T3", date(2026, 2, 10), "North",
                   "Alice", "Home", 4, 25.0, 100.0),
        SaleRecord("T4", date(2026, 2, 20), "East",
                   "Charlie", "Tech", 10, 10.0, 100.0),
    ]


@pytest.fixture
def analyzer(sample_records):
    return SalesAnalyzer(sample_records)


def test_get_total_sales_by_region(analyzer):
    """Verify aggregation mapping calculates accurate regional subsets safely."""
    print("\n--- TEST: Total Sales By Region ---")
    result = dict(analyzer.get_total_sales_by_region())

    assert len(result) == 3
    assert result["North"] == 300.0  # T1 + T3
    assert result["South"] == 300.0  # T2
    assert result["East"] == 100.0  # T4
    print("✓ PASSED: Valid grouping and reduction.")


def test_get_average_sale_by_category(analyzer):
    """Verify average is computed by dividing grouped subtotals against subset item counts."""
    print("\n--- TEST: Average Sale By Category ---")
    result = dict(analyzer.get_average_sale_by_category())

    assert len(result) == 2
    assert result["Tech"] == 200.0  # (200 + 300 + 100) / 3
    assert result["Home"] == 100.0  # 100 / 1
    print("✓ PASSED: Average calculation works gracefully.")


def test_get_top_salespersons(analyzer):
    """Verify lambda-driven sorting successfully reverses standard totals to rank highest bounds."""
    print("\n--- TEST: Top N Salespersons ---")
    result = analyzer.get_top_salespersons(2)

    assert len(result) == 2
    assert result[0] == ("Alice", 300.0)  # Alice is #1
    assert result[1] == ("Bob", 300.0)
    print("✓ PASSED: Top bounded sorting works.")


def test_get_monthly_sales_trend(analyzer):
    """Verify YYYY-MM parsing functions across complex iteration strings."""
    print("\n--- TEST: Monthly Sales Trend ---")
    result = dict(analyzer.get_monthly_sales_trend())

    assert len(result) == 2
    assert result["2026-01"] == 500.0  # T1 + T2
    assert result["2026-02"] == 200.0  # T3 + T4
    print("✓ PASSED: Monthly reductions processed accurately.")


def test_get_sales_by_date_range(analyzer):
    """Verify temporal bounds successfully filter target data classes mapping identically to inclusive operators."""
    print("\n--- TEST: Sales By Date Range ---")

    # Test entire Jan
    jan_sales = analyzer.get_sales_by_date_range(
        date(2026, 1, 1), date(2026, 1, 31))
    assert len(jan_sales) == 2
    assert jan_sales[0].transactionId == "T1"

    # Test exactly one day boundaries inclusive
    specific_day = analyzer.get_sales_by_date_range(
        date(2026, 1, 15), date(2026, 1, 15))
    assert len(specific_day) == 1
    assert specific_day[0].transactionId == "T2"
    print("✓ PASSED: Bounding filters match ranges exactly.")


def test_generate_summary_report(analyzer):
    """Check macro-reduction operations compile cleanly across whole properties without bounds."""
    print("\n--- TEST: Complex Summary Reporting ---")
    summary = analyzer.generate_summary_report()

    assert summary["total_records"] == 4
    assert summary["total_sales"] == 700.0
    assert summary["total_quantity"] == 17
    assert summary["average_sale"] == 175.0
    assert summary["min_sale_amount"] == 100.0
    assert summary["max_sale_amount"] == 300.0
    print("✓ PASSED: Statistics mapped via reduce cleanly.")


def test_empty_data_handling():
    """Test functions aggressively with empty dataset to ensure no reduction IndexErrors or ZeroDivisionError pop."""
    print("\n--- TEST: Empty Data Handling ---")
    empty_analyzer = SalesAnalyzer([])

    assert empty_analyzer.generate_summary_report() == {}
    assert empty_analyzer.get_total_sales_by_region() == []
    assert empty_analyzer.get_average_sale_by_category() == []
    assert empty_analyzer.get_top_salespersons(5) == []
    assert empty_analyzer.get_monthly_sales_trend() == []
    print("✓ PASSED: Empty arrays properly routed safely passing empty boundaries.")
