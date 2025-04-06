import sqlite3
import json
import os
from werkzeug.security import generate_password_hash , check_password_hash
from cloud_storage import upload_to_s3
class DatabaseDriver:
    """
    Database driver for the Expenses app.
    Handles with reading and writing data with the database.
    """
    def __init__(self):
        self.conn = sqlite3.connect("expenses.db", check_same_thread= False)
        self.create_table_users()
        self.create_table_transactions()
        self.create_table_budgets()
        self.create_table_receipts()

    def create_table_users(self):
        """
        Creates a new db table for the users app
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                );
                """
            )
        except Exception as e:
            print(e)

    def create_table_transactions(self):
        """
        This method creates a transactions table to 
        keep track of the transactions
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """
            )
        except Exception as e:
            print(e)
    def create_table_budgets(self):
        """
        Creates a table to keep track of the budgets
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """
            )
        except Exception as e:
            print(e)
    def create_table_receipts(self):
        """
        Creates a table to handle all receipts information
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                transaction_id INTEGER,
                file_path TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id)
                );
                """
            )
        except Exception as e:
            print(e)
    
    def register_user(self,username, password):
        """
        This function helps to register a new user
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
    
    def login_user(self,username, password):
        """
        handles the user logins
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
    
        if user and check_password_hash(user[1], password):
            return user[0] 
        return None 
    
    def add_transaction(self,user_id, amount, category, description):
        """
        This method adds a transaction to the table +
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (user_id, amount, category, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, category, description))
        conn.commit()
        conn.close()

    def get_transactions(self,user_id):
        """
        Function to get all transactions done by a user
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
        transactions = cur.fetchall()
        conn.close()
        return transactions
    
    def delete_transaction(self,transaction_id):
        """
        Function that deletes a transaction
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        conn.close()   

    def set_budget(self,user_id, category, limit_amount):
        """
        Function that handles setting of budget by a user
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO budgets (user_id, category, limit_amount) VALUES (?, ?, ?)",
                (user_id, category, limit_amount))
        conn.commit()
        conn.close() 
    
    def check_budget_exceeded(user_id, category):
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()

        cur.execute("SELECT SUM(amount) FROM transactions "
        "WHERE user_id = ? AND category = ?", (user_id, category))
        total_spent = cur.fetchone()[0] or 0

        cur.execute("SELECT limit_amount FROM budgets "
        "WHERE user_id = ? AND category = ?", (user_id, category))
        budget_limit = cur.fetchone()

        conn.close()

        if budget_limit and total_spent > budget_limit[0]:
            return True 
        return False 
    
    def store_receipt(self,user_id, transaction_id, file_path):
        """
        This function will help to store receipts
        """
        s3_url = upload_to_s3(file_path, f"receipts/{user_id}/{transaction_id}.png")
        if s3_url:
            conn = sqlite3.connect("expenses.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO receipts (user_id, transaction_id, file_path) VALUES (?, ?, ?)",
                    (user_id, transaction_id, s3_url))
            conn.commit()
            conn.close()


    def get_receipt(self,transaction_id):
        """
        This function allows us to retrieve a receipt from a file path
        """
        conn = sqlite3.connect("expenses.db")
        cur = conn.cursor()
        cur.execute("SELECT file_path FROM receipts WHERE transaction_id = ?", (transaction_id,))
        receipt = cur.fetchone()
        conn.close()
        return receipt[0] if receipt else None
    
