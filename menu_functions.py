import pymysql
import datetime
from prettytable import PrettyTable
from config import DB_CONFIG
from logger_config import logger  # Added: centralized logging


# function to add new dish to menu
def add_menu_to_database(dish, price):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "INSERT INTO PRICE_LIST(DISHES, PRICE) VALUES (%s, %s)"  # Changed: parameterized (prevents SQL injection)
    try:
        cursor.execute(sql, (dish, price))
        db.commit()
        logger.info("Menu item added", extra={"dish": dish, "price": price})
        message = "done"
    except pymysql.IntegrityError as e:  # Changed: bare except -> specific (duplicate dish = WARNING not ERROR)
        db.rollback()
        logger.warning(
            "Duplicate dish or constraint violation",
            extra={"dish": dish, "operation": "add_menu", "db_error": str(e)},
        )
        message = "error"
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        db.rollback()
        logger.error(
            "Database error adding menu",
            extra={
                "dish": dish,
                "price": price,
                "operation": "add_menu",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            },
            exc_info=True,  # Added: stack trace for debugging
        )
        message = "error"
    finally:  # Added: ensure connection closed (resource cleanup)
        db.close()
    return message


# function to edit menu item
def edit_menu_item_in_database(dish, price):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "UPDATE PRICE_LIST SET PRICE = %s WHERE DISHES = %s"  # Changed: parameterized (prevents SQL injection)
    try:
        cursor.execute(sql, (price, dish))
        db.commit()
        if cursor.rowcount == 0:  # Added: handle non-existent dish (UPDATE affected 0 rows)
            logger.warning("No dish found to edit", extra={"dish": dish})
            message = "error"
        else:
            logger.info("Menu item updated", extra={"dish": dish, "price": price})
            message = "done"
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        db.rollback()
        logger.error(
            "Database error editing menu",
            extra={
                "dish": dish,
                "price": price,
                "operation": "edit_menu",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            },
            exc_info=True,
        )
        message = "error"
    finally:  # Added: resource cleanup
        db.close()
    return message


# function to delete menu item
def delete_menu_item_from_database(dish):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "DELETE FROM PRICE_LIST WHERE DISHES = %s"  # Changed: parameterized (prevents SQL injection)
    try:
        cursor.execute(sql, (dish,))
        db.commit()
        if cursor.rowcount == 0:  # Added: handle non-existent dish (DELETE affected 0 rows)
            logger.warning("No dish found to delete", extra={"dish": dish})
            message = "error"
        else:
            logger.info("Menu item deleted", extra={"dish": dish})
            message = "done"
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        db.rollback()
        logger.error(
            "Database error deleting menu",
            extra={
                "dish": dish,
                "operation": "delete_menu",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            },
            exc_info=True,
        )
        message = "error"
    finally:  # Added: resource cleanup
        db.close()
    return message
