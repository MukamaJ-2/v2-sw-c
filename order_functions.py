import pymysql
from prettytable import PrettyTable
import datetime
from config import DB_CONFIG
from logger_config import logger  # Added: centralized logging


# function to add order details to database
def add_order_details_to_database(name, date, total_paid):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "INSERT INTO ORDERS(NAME, DATE, TOTAL_PAID) VALUES (%s, %s, %s)"  # Changed: parameterized (prevents SQL injection)
    try:
        cursor.execute(sql, (name, date, total_paid))
        db.commit()
        logger.info(
            "Order added",
            extra={"name": name, "total_paid": total_paid, "date": date},
        )
        message = "done"
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        db.rollback()
        logger.error(
            "Database error adding order",
            extra={
                "name": name,
                "operation": "add_order",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            },
            exc_info=True,  # Added: stack trace for debugging
        )
        message = "error"
    finally:  # Added: resource cleanup
        db.close()
    return message


# function to get details from database
def get_user_details_from_database(name):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "SELECT DATE, TOTAL_PAID, ID FROM ORDERS WHERE NAME = %s"  # Changed: parameterized (prevents SQL injection)
    try:
        cursor.execute(sql, (name,))
        result = cursor.fetchall()
        if not result:  # Added: handle empty result (was causing UnboundLocalError; also now shows all rows)
            logger.info("No orders found for customer", extra={"name": name})
            print("No orders found for this customer.")
            return

        table = PrettyTable()
        table.field_names = ["Order ID", "Date", "Total"]
        for row in result:  # Fixed: was only showing last row; now iterates all rows
            date = row[0]
            total_price = row[1]
            order_id = row[2]
            table.add_row([order_id, date, total_price])
        print(table)
    except pymysql.Error as e:  # Added: was unhandled; now catches DB errors
        logger.error(
            "Database error fetching orders",
            extra={
                "name": name,
                "operation": "get_orders",
                "error_type": type(e).__name__,
                "error_msg": str(e),
            },
            exc_info=True,
        )
        print("Error: Could not fetch orders. Please try again later.")
    finally:  # Added: resource cleanup
        db.close()
