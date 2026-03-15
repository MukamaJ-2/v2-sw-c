# Cafeteria Management System

A Python-based cafeteria management system for viewing menus, placing orders, and managing dishes (admin).

## Setup

1. **Install dependencies** (using the project's virtual environment):
   ```bash
   cd Cafeteria_Management_System_Python-main
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

2. **Configure MySQL** – Create a `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=DISHES_PRICES
   ```

3. **Create the database** – Run this SQL in MySQL:
   ```sql
   CREATE DATABASE IF NOT EXISTS DISHES_PRICES;
   USE DISHES_PRICES;

   CREATE TABLE IF NOT EXISTS PRICE_LIST (
       DISHES VARCHAR(255) NOT NULL,
       PRICE DECIMAL(10, 2) NOT NULL,
       PRIMARY KEY (DISHES)
   );

   CREATE TABLE IF NOT EXISTS ORDERS (
       ID INT AUTO_INCREMENT PRIMARY KEY,
       NAME VARCHAR(255) NOT NULL,
       DATE VARCHAR(100) NOT NULL,
       TOTAL_PAID DECIMAL(10, 2) NOT NULL
   );
   ```

4. **Run the app**:
   ```bash
   python main.py
   ```

## How to Use

### Main Menu

| Command | Action |
|---------|--------|
| **0** | Admin mode – add, edit, or delete menu items |
| **1** | View the menu (list of dishes and prices) |
| **2** | Add an order |
| **3** | View orders for a customer by name |
| **q** | Exit the system |

### Admin Mode (press 0)

| Command | Action |
|---------|--------|
| **1** | Add a new dish to the menu |
| **2** | Edit the price of an existing dish |
| **3** | Delete a dish from the menu |
| **q** | Return to main menu |

### Adding an Order (press 2)

1. Enter the customer's name.
2. Enter dish names one by one (exactly as they appear on the menu).
3. Press **Enter** with no input when finished.
4. A bill is printed and the order is saved.

### Viewing Orders (press 3)

Enter the customer's name to see their order history (Order ID, date, total).

---

## Recent Changes (Error Handling & Logging Improvements)

The following improvements were made based on error-handling analysis, exception strategy refinement, logging implementation, and a comparison of AI-generated vs human-style logging.

### 1. Error Handling Analysis

Poorly written patterns were identified and documented in `ERROR_HANDLING_ANALYSIS.md`:

- **Bare `except:` blocks** – Caught all exceptions (including `KeyboardInterrupt`), provided no debugging info
- **Unhandled empty results** – `get_price_from_database()` and `get_user_details_from_database()` caused `UnboundLocalError` when queries returned no rows
- **Ignored return values** – Admin functions returned `"done"`/`"error"` but callers never checked
- **SQL injection** – All queries used f-strings with user input
- **Logic bug** – `command == '1' or '2' or '3'` was always truthy
- **Resource leaks** – DB connections not closed on exception

### 2. Exception Strategy Improvements

| Fix | Implementation |
|-----|----------------|
| Specific exceptions | Replaced bare `except:` with `pymysql.Error` and `pymysql.IntegrityError` |
| Empty results | `get_price_from_database()` returns `None` when dish not found; `get_user_details_from_database()` handles no rows and shows all order rows |
| Return value handling | Admin and order functions now check `"done"` vs `"error"` and inform the user |
| Input validation | `try/except ValueError` for `int(input())`, empty string checks, negative price rejection |
| SQL injection | Parameterized queries: `cursor.execute(sql, (dish,))` instead of f-strings |
| Logic bug | Fixed to `command in ('1', '2', '3')` |
| Resource cleanup | `try/finally` with `db.close()` in all database functions |

### 3. Logging Implementation

- **`logger_config.py`** – Centralized logger with timestamps, levels, and stderr output
- **INFO** – Menu add/edit/delete, order add, app start/stop, dish not found, no orders for customer
- **WARNING** – Duplicate dish, invalid price input, non-existent dish on edit/delete
- **ERROR** – Database failures with `exc_info=True` for stack traces
- **Structured context** – `extra={}` with dish, price, operation, error_type for debugging

### 4. AI vs Human Logging Comparison

Documented in `ERROR_HANDLING_ANALYSIS.md` (Section 4):

- **AI-style** – Often uses `except Exception`, logs only `{e}`, no stack trace, always ERROR level
- **Human-style** – Specific exceptions (`IntegrityError` vs `pymysql.Error`), rich context (dish, price, operation), `exc_info=True`, WARNING for duplicates vs ERROR for DB failures, sanitized context (no raw SQL)

See `ERROR_HANDLING_ANALYSIS.md` for the full analysis and comparison.