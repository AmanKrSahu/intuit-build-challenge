# Intuit Build Challenge

Welcome to the Technical Assessment Repository! This repository contains implementations for various engineering coding challenges. The goal is to showcase clear, well-structured, and efficient solutions tailored to specific requirements.

## Overview of Sub-Projects

This repository comprises four distinct sub-projects, each designed to test a specific area of software engineering:

1.  **[Library Book Checkout System](./library-checkout-system/README.md)**
    *   **Description:** Robust object-oriented design and deterministic state management for tracking library assets and enforcing patron borrowing rules.
    *   **Key Features:** Decoupled business logic (date calculations, fine enforcement), modern exception handling, and isolated data models.
2.  **[Order Processing and Invoice Summaries](./order-processing-system/README.md)**
    *   **Description:** Pipelined data processing to parse, validate, and aggregate textual data into properly formatted invoice reports.
    *   **Key Features:** Efficient file stream extraction, error logging for malformed rows, and mathematical reduction for dynamic discounts and totals.
3.  **[Producer-Consumer System](./producer-consumer-system/README.md)**
    *   **Description:** Thread synchronization and safe concurrent data transfer between threads.
    *   **Key Features:** Shared queue with strict capacity limits, thread orchestration using modern locking and synchronization techniques (locks, bounded queues).
4.  **[Sales Analytics Application](./sales-analytics-app/README.md)**
    *   **Description:** Functional programming principles and stream processing to analyze large CSV datasets.
    *   **Key Features:** Efficient filtering, grouping, and aggregation across multiple dimensions using `filter()`, `map()`, and `reduce()`.

## Coding Language Used

*   **Python** (Version 3.9+)

## Best Practices Followed

The implementation follows modern engineering principles with an emphasis on production-readiness:

*   **Clean Architecture & Modularity:** Complex tasks are decomposed into manageable, single-responsibility classes.
*   **Defensive Error Handling:** Explicit handling of edge cases (e.g., malformed data, missing files, concurrency interruptions) via custom exceptions.
*   **Robust Data Models:** Use of standard `dataclasses` for immutable pattern matching and strict typing.
*   **Concurrency Management:** Proper thread synchronization avoiding active waiting and race conditions.
*   **Functional Programming:** Efficient data streaming operations for readability and performance.
*   **Virtual Environment & Dependencies:** Isolation using `venv` and package management tools (`pyproject.toml`) for reproducibility.
*   **Comprehensive Testing:** Isolated `pytest` suites bridging edge cases, utilizing ephemeral directories for test data.
*   **Telemetry & Logging:** Safe capture of broken states and traces into local `output/` directories.
*   **Environment Configuration:** Secure decoupling of sensitive information using `.env` files.

## Project Navigation

For detailed setup instructions, execution commands, and testing information for each task, please visit the `README.md` files in their respective directories:

*   ➡ [Library Book Checkout System Setup & Execution](./library-checkout-system/README.md)
*   ➡ [Order Processing Setup & Execution](./order-processing-system/README.md)
*   ➡ [Producer-Consumer System Setup & Execution](./producer-consumer-system/README.md)
*   ➡ [Sales Analytics App Setup & Execution](./sales-analytics-app/README.md)
