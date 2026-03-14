class LibraryError(Exception):
    """Base exception for the library system."""
    pass


class BookNotFoundError(LibraryError):
    """Raised when a book is not found in the library."""
    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member is not found in the library."""
    pass


class RuleViolationError(LibraryError):
    """Raised when a library rule is violated (e.g., max books borrowed, too many fines)."""
    pass
