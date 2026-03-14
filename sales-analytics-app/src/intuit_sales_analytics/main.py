import os
import sys
import logging
from datetime import date
from dotenv import load_dotenv

from src.intuit_sales_analytics.data_loader import SalesDataLoader
from src.intuit_sales_analytics.analyzer import SalesAnalyzer


def configure_logging():
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("output/application.log",
                                mode="w", encoding="utf-8")
        ]
    )


def create_sample_csv(file_path: str):
    """
    Creates a sample payload for testing if missing. The designated directory
    for this file is the project-level 'data/' folder.
    """
    # Create absolute base directory relative to the project root
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        return

    csv_content = """
        transaction_id,date,region,salesperson,product_category,quantity,unit_price
        TX01,2026-01-01,North,Alice,Electronics,2,100.50
        TX02,2026-01-05,South,Bob,Clothing,5,20.00
        TX03,2026-01-15,North,Alice,Electronics,1,500.00
        TX04,2026-02-10,East,Charlie,Home,3,50.00
        TX05,2026-02-25,South,Bob,Electronics,1,250.00
        TX06,2026-03-01,East,Charlie,Clothing,10,15.50
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_content)


def main():
    """Main execution function driving the Sales Analytics Challenge."""
    # Load environment variables
    load_dotenv()
    configure_logging()

    # 1. Prepare sample data (Map back to project root directory)
    project_root = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", ".."))

    env_csv_path = os.getenv("CSV_FILE_PATH", "data/sample_sales.csv")

    # Allow relative paths to resolve against project root
    if not os.path.isabs(env_csv_path):
        sample_csv = os.path.join(project_root, env_csv_path)
    else:
        sample_csv = env_csv_path

    create_sample_csv(sample_csv)

    # 2. Load data
    loader = SalesDataLoader(sample_csv)
    records = loader.load_data()

    if not records:
        logging.error("No valid records found. Exiting.")
        return

    # 3. Analyze data
    analyzer = SalesAnalyzer(records)

    logging.info("\n--- Sales Analytics Report ---")

    logging.info("\n1. Total Sales By Region:")
    for region, total in analyzer.get_total_sales_by_region():
        logging.info(f"   {region}: ${total:.2f}")

    logging.info("\n2. Average Sale By Category:")
    for cat, avg in analyzer.get_average_sale_by_category():
        logging.info(f"   {cat}: ${avg:.2f}")

    logging.info("\n3. Top 2 Salespersons:")
    for person, total in analyzer.get_top_salespersons(2):
        logging.info(f"   {person}: ${total:.2f}")

    logging.info("\n4. Monthly Sales Trend:")
    for month, total in analyzer.get_monthly_sales_trend():
        logging.info(f"   {month}: ${total:.2f}")

    logging.info("\n5. Sales By Date Range (2026-01-01 to 2026-01-31):")
    early_sales = analyzer.get_sales_by_date_range(
        date(2026, 1, 1), date(2026, 1, 31))
    logging.info(f"   Count: {len(early_sales)} transactions")

    logging.info("\n6. Summary Report:")
    summary = analyzer.generate_summary_report()
    for key, value in summary.items():
        if "amount" in key or "sales" in key and key != "total_records":
            logging.info(f"   {key}: ${value:.2f}")
        else:
            logging.info(f"   {key}: {value}")

    logging.info("\n------------------------------")


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Sales Analytics Challenge")
    parser.add_argument("--run-tests", action="store_true",
                        help="Execute the pytest suite instead of the main application")
    args = parser.parse_args()

    if args.run_tests:
        print("Starting Automated Test Suite Execution...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/"])
    else:
        main()
