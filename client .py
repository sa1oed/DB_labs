import tkinter as tk
from tkinter import messagebox
import MySQLdb
from serv import connect_to_login, login, connect_current_user
import sys
from tkinter import simpledialog
import datetime
from decimal import Decimal



def show_database_window(db, username, password):
    # Повторное подключение к базе данных с новыми креденшнлс
    
    db = connect_current_user(username, password)
    
    # Создаем новое окно базы данных
    db_window = tk.Tk()
    db_window.title("Database Cafe")

    # Функция для выполнения SQL-запроса и отображения результатов
    def execute_query(query):
        try:
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()  # Добавьте эту строку для фиксации изменений в базе данных
    
            results = cursor.fetchall()
    
            # Отображение результатов в текстовом виджете
            result_text.delete(1.0, tk.END)
    
            # Получение имен столбцов
            column_names = [column[0] for column in cursor.description]
            result_text.insert(tk.END, f"{', '.join(column_names)}\n")
    
            for row in results:
                # Преобразование значений Decimal в float и форматирование дат
                formatted_row = [float(value) if isinstance(value, Decimal) else value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime.datetime) 
                                 else value.strftime('%Y-%m-%d') if isinstance(value, datetime.date) else value for value in row]
                result_text.insert(tk.END, f"{formatted_row}\n")
                
    
            # Закрываем соединение с базой данных
            cursor.close()
    
        except MySQLdb.Error as e:
            messagebox.showerror("Error", f"Error executing query: {e}")
            db.rollback()  # Откатываем изменения в случае ошибки

    # Функция для отображения списка таблиц в базе данных
    def show_tables():
        query = "SHOW TABLES"
        try:
            cursor = db.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
    
            # Отображение результатов в текстовом виджете
            result_text.delete(1.0, tk.END)
            for row in results:
                table_name = row[0]
                result_text.insert(tk.END, f"{table_name}\n")
    
            # Закрываем соединение с базой данных
            cursor.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    # Функция для удаления записи из выбранной таблицы
    def delete_record():
        selected_table = simpledialog.askstring("Table Selection", "Enter table name:")
        if selected_table:
            condition = simpledialog.askstring("Delete Record", "Enter the condition for deletion:")
            if condition:
                query = f"DELETE FROM {selected_table} WHERE {condition}"
                execute_query(query)
                messagebox.showinfo("Success", f"Data successfully deleted from table {selected_table}!")


    # Функция для отображения данных выбранной таблицы
    def show_table_data():
        selected_table = simpledialog.askstring("Table Selection", "Enter table name:")
        if selected_table:
            query = f"SELECT * FROM {selected_table}"
            try:
                cursor = db.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
    
                # Отображение результатов в текстовом виджете
                result_text.delete(3.0, tk.END)
    
                # Получение имен столбцов
                column_names = [column[0] for column in cursor.description]
                result_text.insert(tk.END, f"{', '.join(column_names)}\n")
    
                # Вставка данных в текстовый виджет
                for row in results:
                    formatted_row = [value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime.datetime) else value for value in row]
                    result_text.insert(tk.END, f"{formatted_row}\n")
    
                # Закрываем соединение с базой данных
                cursor.close()
    
            except MySQLdb.Error as e:
                messagebox.showerror("Error", f"Error executing query: {e}")

    # Функция для вставки новой записи в выбранную таблицу
    def insert_record():
        selected_table = simpledialog.askstring("Table Selection", "Enter table name:")
        if selected_table:
            values = simpledialog.askstring("Insert Record", "Enter comma-separated values:")
            if values:
                query = f"INSERT INTO {selected_table} VALUES ({values})"
                execute_query(query)
                messagebox.showinfo("Success", f"Data successfully added to table {selected_table}!")

    def execute_custom_query():
       query = simpledialog.askstring("Custom Query", "Enter your SQL query:")
       if query:
           execute_query(query)
    
           
    def show_total_revenue_for_period():
        # Запрашиваем у пользователя начальную и конечную дату периода
        start_date = simpledialog.askstring("Period Selection", "Enter start date (YYYY-MM-DD):")
        end_date = simpledialog.askstring("Period Selection", "Enter end date (YYYY-MM-DD):")
    
        # Проверяем, что пользователь ввел даты
        if start_date and end_date:
            # Составляем SQL-запрос с использованием введенных дат
            query = f"SELECT DATE(datetime) AS order_date, SUM(services.cost) AS total_revenue " \
                    f"FROM zakaz INNER JOIN services ON zakaz.ID_service = services.ID " \
                    f"WHERE datetime BETWEEN '{start_date}' AND '{end_date}' GROUP BY order_date"
    
            # Выполняем SQL-запрос
            execute_query(query)
    
    def show_frequent_commands_window():
    # Функция для отображения окна с выбором часто используемых команд

        # Создаем новое окно для часто используемых команд
        frequent_commands_window = tk.Tk()
        frequent_commands_window.title("Frequent Commands")
    
        # Список часто используемых команд
        frequent_commands = [
            "Show Top Selling Item",
            "Show Average Ratings of Waiters",
            "Show Total Revenue for a Period",
            "Show Top 3 Waiters with Best Ratings",
            "Show Order Counts for Each Waiter",
            "Show Unordered Items",
            "Show Waiters with Lowest Ratings"
        ]
    
        # Функция для выполнения выбранной команды
        def execute_frequent_command(command_index):
            if command_index == 0:
                execute_query("SELECT services.name, SUM(zakaz.quality) AS total_sold FROM services INNER JOIN zakaz ON services.ID = zakaz.ID_service GROUP BY services.ID ORDER BY total_sold DESC")
            elif command_index == 1:
                execute_query("SELECT workers.FIO, AVG(zakaz.quality) AS average_rating FROM workers INNER JOIN zakaz ON workers.ID = zakaz.ID_worker GROUP BY workers.ID")
            elif command_index == 2:
                show_total_revenue_for_period()
            elif command_index == 3:
                execute_query("SELECT workers.FIO, AVG(zakaz.quality) AS average_rating FROM workers  INNER JOIN zakaz ON workers.ID = zakaz.ID_worker GROUP BY workers.ID ORDER BY average_rating DESC LIMIT 3")
            elif command_index == 4:
                execute_query("SELECT workers.FIO, COUNT(*) AS total_orders FROM workers LEFT JOIN zakaz ON workers.ID = zakaz.ID_worker GROUP BY workers.ID")
            elif command_index == 5:
                execute_query("SELECT services.name FROM services LEFT JOIN zakaz ON services.ID = zakaz.ID_service WHERE zakaz.ID_service IS NULL")
            elif command_index == 6:
                execute_query("SELECT workers.FIO, AVG(zakaz.quality) AS average_rating, COUNT(*) AS order_count FROM workers  INNER JOIN zakaz ON workers.ID = zakaz.ID_worker GROUP BY workers.ID HAVING order_count >= 3 ORDER BY average_rating ASC")
            
    
        # Создаем кнопки для каждой команды
        for i, command in enumerate(frequent_commands):
            button = tk.Button(frequent_commands_window, text=command, command=lambda i=i: execute_frequent_command(i))
            button.pack()
        
        
        btn_exit = tk.Button(frequent_commands_window, text="Exit", command=frequent_commands_window.destroy)
        btn_exit.pack()
        # Запуск главного цикла окна с часто используемыми командами
        frequent_commands_window.mainloop()       
           
           
           
           
           
    # Кнопки для различных действий
    btn_show_tables = tk.Button(db_window, text="Show Tables", command=show_tables)
    btn_show_tables.pack()

    btn_show_data = tk.Button(db_window, text="Show Table Data", command=show_table_data)
    btn_show_data.pack()

    btn_insert_record = tk.Button(db_window, text="Insert Record", command=insert_record)
    btn_insert_record.pack()

    btn_delete_record = tk.Button(db_window, text="Delete Record", command=delete_record)
    btn_delete_record.pack()
    
    # Кнопка для выполнения пользовательского SQL-запроса
    btn_custom_query = tk.Button(db_window, text="Execute Custom Query", command=execute_custom_query)
    btn_custom_query.pack()
    
    # Добавляем кнопку "Show frequent commands"
    btn_frequent_commands = tk.Button(db_window, text="Show Frequent Commands", command=show_frequent_commands_window)
    btn_frequent_commands.pack()

    # Текстовый виджет для отображения результатов запроса
    result_text = tk.Text(db_window, height=10, width=60)
    result_text.pack()

    # Кнопка для выхода из окна базы данных
    btn_exit = tk.Button(db_window, text="Exit", command=lambda: close_window_and_exit(db_window))
    btn_exit.pack()

    # Запуск главного цикла окна базы данных
    db_window.mainloop()

# Функция для закрытия окна и завершения программы
def close_window_and_exit(window):
    messagebox.showinfo("Bye-Bye", "Good luck, bye!")
    window.destroy()
    sys.exit()

db = connect_to_login()

def log():
    username = entry_username.get()
    password = entry_password.get()
    root.destroy()
    user, password = login(db, username, password)
    if user == None: 
        messagebox.showerror("Login Failed", "Invalid username or password")
        sys.exit()

    username = user[1]
    if user:
        
        
        # Показываем окно базы данных
        show_database_window(db, username, password)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        db.close()
        root.destroy()
        sys.exit()
        

# Создание главного окна
root = tk.Tk()
root.title("Login")

# Создание и размещение виджетов
label_username = tk.Label(root, text="Username:")
label_username.grid(row=0, column=0, padx=10, pady=10, sticky="e")

entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = tk.Label(root, text="Password:")
label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=10)

btn_login = tk.Button(root, text="Login", command=log)
btn_login.grid(row=2, column=0, columnspan=2, pady=10)
# Запуск главного цикла
root.mainloop()