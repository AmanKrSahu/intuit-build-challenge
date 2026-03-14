import pytest
from datetime import date, timedelta
from src.library_system.models import Book, Member
from src.library_system.library import Library
from src.library_system.exceptions import BookNotFoundError, MemberNotFoundError, RuleViolationError


@pytest.fixture
def library():
    lib = Library()
    # Setup some dummy data
    lib.addBook(Book("111", "Book 1", "Author 1"))
    lib.addBook(Book("222", "Book 2", "Author 2"))
    lib.addBook(Book("333", "Book 3", "Author 3"))
    lib.addBook(Book("444", "Book 4", "Author 4"))

    lib.registerMember(Member("M1", "Alice"))
    lib.registerMember(Member("M2", "Bob"))

    return lib


def test_checkout_book_success(library):
    library.checkoutBook("M1", "111")
    member = library._get_member("M1")
    book = library._get_book("111")

    assert "111" in member.borrowedBooks
    assert not book.isAvailable
    assert len(library.getAvailableBooks()) == 3


def test_max_borrow_limit_violation(library):
    library.checkoutBook("M1", "111")
    library.checkoutBook("M1", "222")
    library.checkoutBook("M1", "333")

    with pytest.raises(RuleViolationError, match="maximum of 3 books"):
        library.checkoutBook("M1", "444")


def test_checkout_unavailable_book(library):
    library.checkoutBook("M1", "111")
    with pytest.raises(RuleViolationError, match="not available"):
        library.checkoutBook("M2", "111")


def test_fine_calculation_and_blockage(library):
    # Checkout using a past date
    past_date = date.today() - timedelta(days=20)  # 6 days overdue
    library.checkoutBook("M1", "111", checkout_date=past_date)

    current_fine = library.calculateFine("M1")
    assert current_fine == 3.0  # 6 days * $0.50

    # Return book
    library.returnBook("M1", "111")
    member = library._get_member("M1")
    assert member.fineBalance == 3.0

    # Manually increment fine to > $10
    member.fineBalance = 12.0

    with pytest.raises(RuleViolationError, match="unpaid fines over"):
        library.checkoutBook("M1", "222")


def test_member_not_found(library):
    with pytest.raises(MemberNotFoundError):
        library.checkoutBook("INVALID_MEMBER", "111")


def test_book_not_found(library):
    with pytest.raises(BookNotFoundError):
        library.checkoutBook("M1", "INVALID_BOOK")


def test_borrowing_history(library):
    library.checkoutBook("M1", "111")
    library.returnBook("M1", "111")

    history = library.getMemberBorrowingHistory("M1")
    assert len(history) == 2
    assert "Checked out" in history[0]
    assert "Returned" in history[1]
