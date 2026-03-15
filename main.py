import pymysql
from prettytable import PrettyTable
import datetime
from config import DB_CONFIG
from logger_config import logger  # Added: centralized logging instead of print() for errors
from menu_functions import (
    add_menu_to_database,
    edit_menu_item_in_database,
    delete_menu_item_from_database,
)
from order_functions import add_order_details_to_database, get_user_details_from_database


# function to get current date
def date_now():
    now = datetime.datetime.now()
    date_format = now.strftime("%d-%m-%Y")
    return date_format


# function to get current time
def time_now():
    now = datetime.datetime.now()
    time_format = now.strftime("%I:%M %p")
    return time_format


# function for admin account
def admin_account():
    print("Command List => Press '1' for add dish to menu,")
    print("\t\tPress '2' for edit price,")
    print("\t\tPress '3' for delete item from menu")
    print("\t\tPress 'q' to exit")

    admin_input = input("Enter command : ")

    if admin_input == "1":
        dish = input("Enter new dish : ").strip()
        if not dish:  # Added: input validation - reject empty dish names
            print("Error: Dish name cannot be empty.")
            return
        try:  # Added: catch ValueError when user enters non-numeric price
            price = int(input("Enter price for new dish : "))
            if price < 0:  # Added: reject negative prices
                print("Error: Price cannot be negative.")
                return
        except ValueError:
            print("Error: Please enter a valid number for the price.")
            logger.warning("Invalid price input in admin add", extra={"dish": dish})
            return
        result = add_menu_to_database(dish, price)
        if result == "done":  # Added: check return value instead of ignoring it
            print("Dish added successfully.")
        else:
            print("Error: Could not add dish. It may already exist.")

    elif admin_input == "2":
        dish = input("Enter dish name for which you want to change price : ").strip()
        if not dish:  # Added: input validation
            print("Error: Dish name cannot be empty.")
            return
        try:  # Added: catch ValueError for non-numeric price
            price = int(input("Enter new price for dish : "))
            if price < 0:
                print("Error: Price cannot be negative.")
                return
        except ValueError:
            print("Error: Please enter a valid number for the price.")
            return
        result = edit_menu_item_in_database(dish, price)
        if result == "done":  # Added: check return value
            print("Price updated successfully.")
        else:
            print("Error: Could not update. Dish may not exist.")

    elif admin_input == "3":
        dish = input("Enter dish name which you want to delete : ").strip()
        if not dish:  # Added: input validation
            print("Error: Dish name cannot be empty.")
            return
        result = delete_menu_item_from_database(dish)
        if result == "done":  # Added: check return value
            print("Dish deleted successfully.")
        else:
            print("Error: Could not delete. Dish may not exist.")

    elif admin_input == "q":
        return


# function to take user input
def select_input(my_input):
    if my_input == "1":
        output = view_menu()
    elif my_input == "2":
        output = add_order()
    elif my_input == "3":
        name = input("Enter name of the person : ").strip()
        if not name:  # Added: input validation
            print("Error: Name cannot be empty.")
            return "Error : Please Enter Correct Command"
        print()
        output = get_user_details_from_database(name)
    else:
        output = "Error : Please Enter Correct Command"
    return output


# function for adding order details
def add_order():
    name = input("Name of the person : ").strip()
    if not name:  # Added: input validation
        print("Error: Name cannot be empty.")
        return

    date = date_now()
    time = time_now()
    total_price = get_total_price()
    if total_price is None:  # Added: handle empty order or invalid dish names
        print("Error: Could not calculate total. Please check dish names and try again.")
        return

    bill = f"-----------------\nYour Bill {name}\n------------------\nTotal = {total_price}\nDate : {date}\nTime : {time}\n\n"
    date_time = f"{date}, {time}"

    result = add_order_details_to_database(name, date_time, total_price)
    if result == "done":  # Added: check return value before showing bill
        print(bill)
    else:
        print("Error: Could not save order. Please try again.")


# function to view menu
def view_menu():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    table2 = PrettyTable()
    table2.field_names = ["Dish", "Price"]
    sql = "SELECT * FROM PRICE_LIST"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            dish = row[0]
            price = row[1]
            table2.add_row([dish, price])
        print(table2)
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        logger.error(
            "Database error viewing menu",
            extra={"operation": "view_menu", "error_type": type(e).__name__, "error_msg": str(e)},
            exc_info=True,  # Added: include stack trace for debugging
        )
        print("Error: Can't show menu. Please try again later.")
    finally:  # Added: ensure connection closed even on error (resource cleanup)
        db.close()


# function to get price from database
def get_price_from_database(dish):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = "SELECT PRICE FROM PRICE_LIST WHERE DISHES = %s"  # Changed: parameterized query (prevents SQL injection)
    try:
        cursor.execute(sql, (dish,))
        result = cursor.fetchall()
        if not result:  # Added: handle empty result (was causing UnboundLocalError)
            logger.info("Dish not found in menu", extra={"dish": dish})
            return None
        return result[0][0]
    except pymysql.Error as e:  # Changed: bare except -> specific pymysql.Error
        logger.error(
            "Database error fetching price",
            extra={"dish": dish, "operation": "get_price", "error_type": type(e).__name__, "error_msg": str(e)},
            exc_info=True,
        )
        return None
    finally:  # Added: resource cleanup
        db.close()


# function to add total price
def get_total_price():
    price_list = []
    print()
    dish = input("What you want to eat ? : ").strip()

    while dish:
        dish_price = get_price_from_database(dish)
        if dish_price is None:  # Added: handle invalid dish (skip, don't crash)
            print(f"'{dish}' is not on the menu. Please enter a valid dish name.")
            dish = input("Anything else ? : ").strip()
            continue
        price_list.append(dish_price)
        print()
        dish = input("Anything else ? : ").strip()
        print()

    if not price_list:  # Added: handle empty order (no dishes entered)
        return None
    return sum(price_list)


if __name__ == "__main__":
    logger.info("Cafeteria Management System starting")  # Added: startup logging
    print("---------------------------------------------------------------------CAFETERIA MANAGEMENT SYSTEM---------------------------------------------------------------------")
    print()
    print("===============================================")
    print("Command List => Press '0' for admin,")
    print("\t\tPress '1' for menu,")
    print("\t\tPress '2' to add order,")
    print("\t\tPress '3' to view order")
    print("\t\tPress 'q' to exit")
    print("===============================================")
    print()

    command = input("Enter command : ")
    print()

    while command != "q":
        if command == "0":
            admin_account()
        elif command in ("1", "2", "3"):  # Fixed: was "command == '1' or '2' or '3'" (always truthy)
            select_input(command)
        else:
            print("Error : Please enter correct command")

        print("------------------------------------------------------------------------------------------------------")
        print()
        command = input("Enter command : ")

    logger.info("Cafeteria Management System exiting")  # Added: shutdown logging
    print("Thank you for using this project | This project is created by => Shashwat Dubey, Subrat Rathore")
