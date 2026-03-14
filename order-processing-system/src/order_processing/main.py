import logging
import sys
import os
from src.order_processing.processor import OrderProcessor
from src.order_processing.report import ReportGenerator


def configure_logging():
    os.makedirs("output", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("output/application.log",
                                mode="w", encoding="utf-8")
        ]
    )


def main():
    configure_logging()
    logging.info("Starting Assignment 2: Order Processing System.")

    input_file = "data/orders.txt"
    error_log = "output/error.log"
    report_file = "output/summary_report.txt"

    # Process
    processor = OrderProcessor(error_log_path=error_log)
    logging.info(f"Parsing input file: {input_file}")

    orders = processor.parse_file(input_file)
    logging.info(f"Successfully parsed {len(orders)} valid order records.")

    logging.info("Generating customer summaries...")
    summaries = processor.generate_summaries(orders)

    logging.info(f"Writing summary report to: {report_file}")
    generator = ReportGenerator(output_path=report_file)
    generator.write_report(summaries)

    logging.info(
        "Order processing pipeline completed successfully. Please check the 'output' directory.")


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(
        description="Assignment 2: Order Processing")
    parser.add_argument("--run-tests", action="store_true",
                        help="Execute the pytest suite instead of the main application")
    args = parser.parse_args()

    if args.run_tests:
        print("Starting Automated Test Suite Execution...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/"])
    else:
        main()
