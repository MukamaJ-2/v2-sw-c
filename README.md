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