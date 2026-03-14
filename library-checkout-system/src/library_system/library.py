from typing import List, Dict, Optional
from datetime import date, timedelta
from src.library_system.models import Book, Member
from src.library_system.exceptions import BookNotFoundError, MemberNotFoundError, RuleViolationError


class Library:
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        # Simple history log for members: memberId -> list of string messages
        self.history: Dict[str, List[str]] = {}

    def addBook(self, book: Book) -> None:
        self.books[book.isbn] = book

    def registerMember(self, member: Member) -> None:
        self.members[member.memberId] = member
        self.history[member.memberId] = []

    def _get_member(self, memberId: str) -> Member:
        if memberId not in self.members:
            raise MemberNotFoundError(
                f"Member with ID '{memberId}' not found.")
        return self.members[memberId]

    def _get_book(self, isbn: str) -> Book:
        if isbn not in self.books:
            raise BookNotFoundError(f"Book with ISBN '{isbn}' not found.")
        return self.books[isbn]

    def checkoutBook(self, memberId: str, isbn: str, checkout_date: Optional[date] = None) -> None:
        if checkout_date is None:
            checkout_date = date.today()

        member = self._get_member(memberId)
        book = self._get_book(isbn)

        if not book.isAvailable:
            raise RuleViolationError(
                f"Book '{book.title}' is currently not available.")

        if len(member.borrowedBooks) >= 3:
            raise RuleViolationError(
                f"Member '{member.name}' has already borrowed the maximum of 3 books.")

        if member.fineBalance > 10.0:
            raise RuleViolationError(
                f"Member '{member.name}' has unpaid fines over $10 (${member.fineBalance:.2f}). Cannot borrow new books.")

        # Perform checkout
        book.isAvailable = False
        member.borrowedBooks[isbn] = checkout_date
        self.history[memberId].append(
            f"Checked out '{book.title}' on {checkout_date}")

    def calculateFine(self, memberId: str, current_date: Optional[date] = None) -> float:
        """
        Calculates and updates fine for all currently borrowed books and returns the updated fine balance.
        Fine is $0.50 per day for books kept past 14 days.
        """
        if current_date is None:
            current_date = date.today()

        member = self._get_member(memberId)

        # Calculate fine dynamically for overdue books currently held
        new_fine = 0.0
        for isbn, checkout_date in member.borrowedBooks.items():
            days_held = (current_date - checkout_date).days
            if days_held > 14:
                overdue_days = days_held - 14
                new_fine += overdue_days * 0.50

        # This will add up over time if we don't clear it.
        # For simplicity, calculateFine calculates the current fine on borrowed books and adds to existing.
        # However, to avoid double charging on successive calls, we only charge upon return or we maintain "last_calculated_date".
        # Let's adjust logic: calculateFine calculates the total fine for the member *including* currently overdue items,
        # but actual balance modification happens upon return.

        # We will just return the hypothetical total balance if returned today.
        current_held_fines = 0.0
        for isbn, checkout_date in member.borrowedBooks.items():
            days_held = (current_date - checkout_date).days
            if days_held > 14:
                overdue_days = days_held - 14
                current_held_fines += overdue_days * 0.50

        # Assuming member.fineBalance holds fines from previously returned overdue books
        return member.fineBalance + current_held_fines

    def returnBook(self, memberId: str, isbn: str, return_date: Optional[date] = None) -> None:
        if return_date is None:
            return_date = date.today()

        member = self._get_member(memberId)
        book = self._get_book(isbn)

        if isbn not in member.borrowedBooks:
            raise RuleViolationError(
                f"Member '{member.name}' did not borrow book '{book.title}'.")

        checkout_date = member.borrowedBooks[isbn]

        # Calculate fine
        days_held = (return_date - checkout_date).days
        if days_held > 14:
            overdue_days = days_held - 14
            fine_amount = overdue_days * 0.50
            member.fineBalance += fine_amount
            self.history[memberId].append(
                f"Returned '{book.title}' on {return_date}. Overdue fine: ${fine_amount:.2f}")
        else:
            self.history[memberId].append(
                f"Returned '{book.title}' on {return_date}. No fine.")

        # Perform return
        del member.borrowedBooks[isbn]
        book.isAvailable = True

    def getAvailableBooks(self) -> List[Book]:
        return [book for book in self.books.values() if book.isAvailable]

    def getMemberBorrowingHistory(self, memberId: str) -> List[str]:
        member = self._get_member(memberId)  # validate member exists
        return self.history.get(memberId, [])
