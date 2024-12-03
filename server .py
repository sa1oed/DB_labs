import MySQLdb
from tkinter import messagebox
import tkinter as tk
import sys
import hashlib


def generate_md5_hash(password):
    md5_hash = hashlib.md5(password.encode()).hexdigest()
    return md5_hash


MAX_LOGIN_ATTEMPTS = 3

def connect_to_login():
    db = MySQLdb.connect(
        host="10.10.10.15",
        user="checker",
        password="zvnxvwXKY1wVNp0",
        database="cafe",
        port=5000
    )
    return db

def connect_current_user(username, password):
    db = MySQLdb.connect(
        host="10.10.10.15",
        user=username,
        password = password,
        database="cafe",
        port=5000
    )
    return db


def login(db, username, password):
    login_attempts = 0

    while login_attempts < MAX_LOGIN_ATTEMPTS:
        try:
            cursor = db.cursor()
            if any(keyword in username or keyword in password for keyword in ['\'', 'OR', '=', '/*', '%']):
                messagebox.showerror("Login Failed", "SQL injection detected. You can't login in this session")
                return None, None
            h_password  = generate_md5_hash(password)
            # Search user in table users
            query = f"SELECT * FROM users WHERE username = '{username}' AND hashed_password = '{h_password}'"
            cursor.execute(query)
            user = cursor.fetchone()

            while not user:
                
                messagebox.showerror("Login Failed", "Invalid username or password. Attempts left: {}".format(MAX_LOGIN_ATTEMPTS - login_attempts))
                
                if login_attempts == 3:
                    messagebox.showerror("Error", "You can't login now. Please try again")
                    return None, None
                else:
                    # Use the ask_for_credentials function to get new login credentials
                    credentials = ask_for_credentials()
                    username = credentials[0]
                    password = credentials[1]
                    login_attempts += 1
                    # Modify the query to use the new credentials
                    query = f"SELECT * FROM users WHERE username = '{username}' AND hashed_password = MD5('{password}')"
                    cursor.execute(query)
                    user = cursor.fetchone()
                    
                
            messagebox.showinfo("Login Successful", f"Welcome, {username}")
            messagebox.showinfo("Login Successful", f"Now you are login like {username}")

            # Close connection
            cursor.close()
            db.close()

            return user, password

        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None, None

    # Если достигнуто максимальное количество попыток, завершаем программу
    messagebox.showerror("Login Failed", "Exceeded maximum login attempts. Exiting.")
    sys.exit()
    return None, None


class LoginDialog(tk.simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Enter your login:").grid(row=0, sticky="w")
        tk.Label(master, text="Enter your password:").grid(row=1, sticky="w")

        self.entry_login = tk.Entry(master)
        self.entry_password = tk.Entry(master, show="*")

        self.entry_login.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        return self.entry_login

    def apply(self):
        username = self.entry_login.get()
        password = self.entry_password.get()
        self.result = (username, password)

def ask_for_credentials():
    root = tk.Tk()
    root.withdraw()  # Close Tkinter window

    login_dialog = LoginDialog(root, title="Login")
    result = login_dialog.result

    # Check data
    while result is None or result[0].strip() == "" or result[1].strip() == "":
        login_dialog = LoginDialog(root, title="Login", prompt="Invalid input. Please enter both username and password.")
        result = login_dialog.result

    return result
