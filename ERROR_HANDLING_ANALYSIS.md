# Error Handling Analysis & Improvement Report

## 1. Analysis of Poorly Written Error Handling Code

### 1.1 Bare `except:` Blocks (Critical)

**Location:** `menu_functions.py` (lines 22–24, 40–47, 63–71), `order_functions.py` (16–23), `main.py` (111–122)

**Problem:**
```python
try:
    cursor.execute(sql)
    db.commit()
    message = "done"
except:
    db.rollback()
    message = "error"
```

**Why it's bad:**
- Catches **all** exceptions including `KeyboardInterrupt`, `SystemExit`, `MemoryError`
- No visibility into *what* failed (connection? syntax? constraint?)
- Swallows the exception—no traceback, no debugging info
- Makes production debugging nearly impossible

---

### 1.2 Unhandled Empty Results (Critical)

**Location:** `main.py` `get_price_from_database()` (lines 129–144), `order_functions.py` `get_user_details_from_database()` (36–52)

**Problem:**
```python
for row in result:
    price = row[0]
return price  # UnboundLocalError if result is empty!
```

**Why it's bad:**
- Empty `result` → `price` never assigned → `UnboundLocalError` at runtime
- User enters non-existent dish → crash instead of friendly message
- No rows for customer name → same crash

---

### 1.3 Ignored Return Values (High)

**Location:** `main.py` `admin_account()` (lines 40–52)

**Problem:** `add_menu_to_database()`, `edit_menu_item_in_database()`, `delete_menu_item_from_database()` return `"done"` or `"error"`, but callers never check:

```python
add_menu_to_database(dish, price)  # User never knows if it failed
```

---

### 1.4 No Input Validation (High)

**Location:** `main.py` `admin_account()`, `get_total_price()`

**Problem:**
- `int(input())` → `ValueError` on non-numeric input (unhandled)
- Empty dish names accepted
- Negative prices accepted

---

### 1.5 SQL Injection (Critical)

**Location:** All DB functions

**Problem:**
```python
sql = f"SELECT PRICE FROM PRICE_LIST WHERE DISHES = '{dish}'"
```

User input is interpolated directly. Malicious input: `'; DROP TABLE PRICE_LIST; --`

---

### 1.6 Logic Bug in Main Loop (High)

**Location:** `main.py` line 199

**Problem:**
```python
elif command == '1' or '2' or '3':  # Always truthy! '2' and '3' are non-empty strings
```

Should be: `elif command in ('1', '2', '3'):`

---

### 1.7 Resource Leaks (Medium)

**Problem:** `view_menu()` and `get_price_from_database()` don't use `try/finally` or context managers. If an exception occurs, `db.close()` may never run.

---

## 2. Improved Exception Strategies (Targeted Fixes)

| Issue | Fix |
|-------|-----|
| Bare `except:` | Catch `pymysql.Error` (or `Exception` with re-raise for unexpected) |
| Empty results | Check `if not result:` and return `None` or raise `ValueError` |
| Ignored returns | Check return value and `print()` success/failure to user |
| Input validation | Wrap `int(input())` in try/except `ValueError` |
| SQL injection | Use parameterized queries: `cursor.execute(sql, (dish,))` |
| Logic bug | Use `command in ('1', '2', '3')` |
| Resource leaks | Use `with` or `try/finally` for DB connections |

---

## 3. Meaningful Logging Strategy

### 3.1 Log Levels

| Level | Use Case |
|-------|----------|
| `DEBUG` | SQL queries, variable values during development |
| `INFO` | User actions (order placed, menu updated), app startup |
| `WARNING` | Recoverable issues (empty result, invalid input retry) |
| `ERROR` | DB failures, unhandled exceptions |
| `CRITICAL` | System-level failures |

### 3.2 What to Log

- **On DB error:** Exception type, message, SQL (sanitized), operation name
- **On empty result:** Operation, parameters (e.g. dish name, customer name)
- **On user action:** Action type, key params (no passwords)
- **On startup:** DB connection success/failure

---

## 4. AI-Generated vs Human Reasoning: Logging Comparison

### Scenario: Database insert fails in `add_menu_to_database()`

#### AI-Generated Suggestion (typical)

```python
except Exception as e:
    logger.error(f"Error adding menu: {e}")
    db.rollback()
    message = "error"
```

**Pros:** Simple, logs the error message  
**Cons:**
- `Exception` is still broad (though better than bare `except`)
- No context: which dish? which price?
- No exception type—hard to filter in log aggregation
- No stack trace for debugging

---

#### Human Reasoning Approach

A human might consider:

1. **Operational needs:** "When this fails at 2am, what do I need to fix it?"
   - Dish name and price (to check for duplicates, invalid data)
   - Exact DB error (constraint violation vs connection timeout)
   - Stack trace for unexpected errors

2. **Security:** Don't log full SQL with user input in production (could contain PII or injection attempts)

3. **Noise:** Don't log at ERROR for expected cases (e.g. duplicate dish—that's a user mistake, maybe WARNING)

4. **Structured logging:** Use dict/JSON for log aggregation (e.g. ELK, Splunk)

**Improved human-style logging:**

```python
except pymysql.IntegrityError as e:
    logger.warning("Duplicate dish or constraint violation", extra={
        "dish": dish,
        "operation": "add_menu",
        "db_error": str(e)
    })
    db.rollback()
    message = "error"
except pymysql.Error as e:
    logger.error("Database error adding menu", extra={
        "dish": dish,
        "price": price,
        "operation": "add_menu",
        "error_type": type(e).__name__,
        "error_msg": str(e)
    }, exc_info=True)  # Include stack trace
    db.rollback()
    message = "error"
```

**Key differences:**

| Aspect | AI suggestion | Human reasoning |
|--------|---------------|-----------------|
| Exception specificity | `Exception` | `pymysql.IntegrityError` vs `pymysql.Error` |
| Context | Just `{e}` | dish, price, operation |
| Stack trace | No | `exc_info=True` for unexpected errors |
| Log level | Always ERROR | WARNING for duplicates, ERROR for DB failures |
| Security | May log raw SQL | Sanitized context only |

---

### Summary: When to Prefer Human Reasoning

- **Context matters:** Log enough to reproduce the issue
- **Level matters:** Not everything is ERROR
- **Structure matters:** Machine-parseable logs scale better
- **Security matters:** Avoid logging raw user input in production
