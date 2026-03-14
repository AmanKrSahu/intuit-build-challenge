import logging
import sys
import os
from datetime import date, timedelta
from src.library_system.models import Book, Member
from src.library_system.library import Library
from src.library_system.exceptions import LibraryError


def configure_logging():
    os.makedirs("output", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("output/error.log", mode="w", encoding="utf-8")
        ]
    )


def main():
    configure_logging()
    logging.info("Starting Library Book Checkout System demonstration.")

    # Initialize library
    library = Library()

    # Add books
    b1 = Book(isbn="111", title="Python Crash Course", author="Eric Matthes")
    b2 = Book(isbn="222", title="Clean Code", author="Robert C. Martin")
    b3 = Book(isbn="333", title="Design Patterns", author="Erich Gamma")
    b4 = Book(isbn="444", title="Refactoring", author="Martin Fowler")

    for b in [b1, b2, b3, b4]:
        library.addBook(b)

    # Register members
    m1 = Member(memberId="M01", name="Alice")
    m2 = Member(memberId="M02", name="Bob")

    for m in [m1, m2]:
        library.registerMember(m)

    logging.info(
        f"Available books: {[b.title for b in library.getAvailableBooks()]}")

    # Standard checkout
    logging.info("Checking out 'Clean Code' to Alice...")
    library.checkoutBook("M01", "222")

    logging.info(
        "Checking out 'Design Patterns' and 'Refactoring' to Alice...")
    library.checkoutBook("M01", "333")
    library.checkoutBook("M01", "444")

    # Attempt to borrow more than 3 books
    logging.info(
        "Alice attempts to borrow a 4th book (Python Crash Course)...")
    try:
        library.checkoutBook("M01", "111")
    except LibraryError as e:
        logging.error(f"Error: {e}")

    # Simulate overdue fine
    today = date.today()
    # 20 days ago (6 days over the 14 day limit)
    past_date = today - timedelta(days=20)

    # Alice checks out 'Python Crash Course' retroactively (simulate she returned one and took another)
    # First let's return 'Clean Code'
    logging.info("Alice returns 'Clean Code'...")
    library.returnBook("M01", "222")

    logging.info(
        f"Alice's current fine balance: ${library.calculateFine('M01'):.2f}")

    logging.info(
        f"Checking out 'Python Crash Course' to Alice using a past date ({past_date})...")
    library.checkoutBook("M01", "111", checkout_date=past_date)

    # Now calculate fine
    current_fine = library.calculateFine("M01", current_date=today)
    logging.info(
        f"Calculated fine for Alice (6 days overdue) is: ${current_fine:.2f}")

    # Returning overdue book
    logging.info("Alice returns overdue 'Python Crash Course'...")
    library.returnBook("M01", "111", return_date=today)

    final_fine = library.calculateFine("M01")
    logging.info(f"Alice's fine balance is now: ${final_fine:.2f}")

    # Force a large fine to trigger rule violation
    m1.fineBalance = 15.00
    logging.info(
        "Manually increased Alice's fine balance to $15.00 to demonstrate blockage.")
    logging.info("Alice attempts to borrow 'Python Crash Course'...")
    try:
        library.checkoutBook("M01", "111")
    except LibraryError as e:
        logging.error(f"Error: {e}")

    # Borrowing history
    logging.info("Alice's Borrowing History:")
    for h in library.getMemberBorrowingHistory("M01"):
        logging.info(f" - {h}")

    logging.info("Demonstration completed.")


if __name__ == "__main__":
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(
        description="Assignment 1: Library System")
    parser.add_argument("--run-tests", action="store_true",
                        help="Execute the pytest suite instead of the main application")
    args = parser.parse_args()

    if args.run_tests:
        print("Starting Automated Test Suite Execution...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/"])
    else:
        main()
