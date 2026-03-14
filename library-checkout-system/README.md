# Library Book Checkout System

## Overview

This application simulates a library book checkout and return system governed by robust business rules. The architecture focuses on cleanly separated dataclass models representing domain entities (`Book`, `Member`), governed by a central state `Library` orchestrator executing discrete lending bounds and overdue fine calculations.

The core implementation validates member checkout capacity (maximum 3 books) and enforces strict account limits (preventing checkouts for members accumulating >$10.00 in fines). Fines are calculated deterministically at $0.50 per day overdue (books are strictly due back 14 days after checkout).

## Architecture Component Definitions

- **Book (`models.py`)**: Dataclass representing the physical library asset (`isbn`, `title`, `author`, `isAvailable`).
- **Member (`models.py`)**: Dataclass tracking library patron status (`memberId`, `name`, `borrowedBooks`, `fineBalance`).
- **Library (`library.py`)**: State manager and rule engine. Exposes top-level API operations like `checkoutBook()`, `returnBook()`, and dynamic `calculateFine()`.
- **Exceptions (`exceptions.py`)**: Custom hierarchy defining constraints (e.g. `RuleViolationError`, `BookNotFoundError`) used to block unauthorized operations cleanly.
- **Main Engine (`main.py`)**: Entrypoint demonstrating standard user lifecycles, logging state changes natively into `output/error.log`.

## Setup & Configuration

**All module and testing dependencies are managed gracefully and listed within the `pyproject.toml` definition file.** Ensure Python `^3.9` is actively installed locally prior to usage.

### Installation

1. Create a logical Virtual Environment within the `.intuit/Assignment_1` project directory:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/macOS
   # On Windows typically: .\venv\Scripts\activate
   ```

2. Install the necessary development and runtime dependencies parsed from `.toml`:

   ```bash
   pip install -e .
   ```

## Execution Interfaces

The executable `library_system` module has been explicitly tied to the `main.py` entrypoint. Application logs natively cascade.

**Standard Simulation Run**
To execute the application orchestrator showcasing standard logic pathways (including error blockage):

```bash
python -m src.library_system.main
```

**Automated Test Integration Check**
To natively run the complete functional edge tests directly through the main entry proxy using Argparse hooks without relying on direct pytest invocation:

```bash
python -m src.library_system.main --run-tests
```

_Note: Granular test outputs automatically generate specific local files under `output/<module_name>.log` thanks to custom `conftest.py` bindings._

## Test Coverage

The application features a comprehensive `pytest` suite simulating rigorous edge-cases and boundary conditions natively. Key test coverage includes:

1. **Borrow Limit Bounds**: Validates members cannot checkout > 3 books simultaneously.
2. **Dynamic Fine Calculation**: Confirms past-due books accrue accurate $0.50/day penalties logic when tracking dates retroactively.
3. **Debt Limit Bounds**: Asserts the engine correctly halts lending when a user fine capacity crosses $10.00.
4. **Availability Collisions**: Ensures an exception is correctly raised when attempting to sign out an already checked out book.

## Key Demonstrated Concepts

- **Dataclass Pattern**: Entities mapped robustly without redundant boilerplate initialization code.
- **Fail-Fast Defense Structures**: Functions raise explicit custom exceptions immediately upon failing precondition verification checks rather than failing silently later.
- **State encapsulation**: `Library` methods operate as the only valid mutations interface over underlying `books` and `members` dictionaries.
