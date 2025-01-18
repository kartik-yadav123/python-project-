import tkinter as tk
from tkinter import messagebox
import requests
from tkinter import ttk
import threading
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Store user data
users = {}

def show_register():
    content_frame.tkraise()
    register_frame.tkraise()

def show_login():
    content_frame.tkraise()
    login_frame.tkraise()

def open_currency_converter():
    content_frame.tkraise()
    currency_converter_app = CurrencyConverterApp(content_frame)

def register_user():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not name or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
    elif email in users:
        messagebox.showerror("Error", "User  already exists! Please login.")
    else:
        users[email] = {"name": name, "password": password}
        messagebox.showinfo("Registration", f"Registration successful!\nWelcome, {name}")
        show_login()

def login_user():
    email = login_email_entry.get().strip()
    password = login_password_entry.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "All fields are required!")
    elif email not in users:
        messagebox.showerror("Error", "User  not found! Please register first.")
    elif users[email]["password"] != password:
        messagebox.showerror("Error", "Incorrect password!")
    else:
        messagebox.showinfo("Login", f"Login successful!\nWelcome back, {users[email]['name']}.")
        open_currency_converter()  # Call to open the currency converter


def open_currency_converter():
    # Check if the CurrencyConverterApp is already created, if not, create it.
    if not hasattr(root, 'currency_converter_app'):
        root.currency_converter_app = CurrencyConverterApp(root)
    
    # Raise the content frame to bring the currency converter UI to the front
    content_frame.tkraise()  # Show the currency converter window


class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.configure(bg="#f0f8ff")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.api_url = "https://api.exchangerate-api.com/v4/latest/"

        self.currencies = []
        self.get_currencies()

        tk.Label(root, text="Amount:", bg="#f0f8ff", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = tk.Entry(root, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(root, text="From Currency:", bg="#f0f8ff", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.from_currency = tk.StringVar(root)
        self.from_currency.set("USD")
        self.from_currency_menu = tk.OptionMenu(root, self.from_currency, *self.currencies)
        self.from_currency_menu.config(bg="#d3e0ea", font=("Arial", 10))
        self.from_currency_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        tk.Label(root, text="To Currency:", bg="#f0f8ff", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.to_currency = tk.StringVar(root)
        self.to_currency.set("INR")
        self.to_currency_menu = tk.OptionMenu(root, self.to_currency, *self.currencies)
        self.to_currency_menu.config(bg="#d3e0ea", font=("Arial", 10))
        self.to_currency_menu.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.result_label = tk.Label(root, text="Converted Amount: ", bg="#f0f8ff", font=("Arial", 12, "bold"))
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        self.convert_button = tk.Button(root, text="Convert", command=self.convert_currency, bg="#87cefa", font=("Arial", 10))
        self.convert_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        self.clear_button = tk.Button(root, text="Clear All", command=self.clear_all, bg="#87cefa", font=("Arial", 10))
        self.clear_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        self.history_label = tk.Label(root, text="Conversion History:", bg="#f0f8ff", font=("Arial", 10, "bold"))
        self.history_label.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

        style = ttk.Style()
        style.configure("Treeview", rowheight=25, fieldbackground="#f0f8ff", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#d3e0ea")
        style.map("Treeview", background=[('selected', '#87cefa')])

        self.history_table = ttk.Treeview(root, columns=("Amount", "From", "To", "Result"), show="headings")
        self.history_table.heading("Amount", text="Amount")
        self.history_table.heading("From", text="From Currency")
        self.history_table.heading("To", text="To Currency")
        self.history_table.heading("Result", text="Converted Amount")

        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.history_table.yview)
        self.history_table.config(yscrollcommand=self.scrollbar.set)
        self.history_table.grid(row=7, column=0, columnspan=2, pady=10, sticky="nsew")
        self.scrollbar.grid(row=7, column=2, sticky="ns")

        self.graph_button = tk.Button(root, text="Show Exchange Rate Trends", command=self.show_graph, bg="#87cefa", font=("Arial", 10))
        self.graph_button.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")

        self.save_button = tk.Button(root, text="Save History", command=self.save_history, bg="#87cefa", font=("Arial", 10))
        self.save_button.grid(row=9, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(root, text="Set Rate Notification:", bg="#f0f8ff", font=("Arial", 10, "bold"))
        tk.Label(root, text="From Currency:", bg="#f0f8ff", font=("Arial", 10)).grid(row=10, column=0, padx=10, pady=5, sticky="w")
        self.alert_from_currency = tk.StringVar(root)
        self.alert_from_currency.set("USD")
        tk.OptionMenu(root, self.alert_from_currency, *self.currencies).grid(row=10, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(root, text="To Currency:", bg="#f0f8ff", font=("Arial", 10)).grid(row=11, column=0, padx=10, pady=5, sticky="w")
        self.alert_to_currency = tk.StringVar(root)
        self.alert_to_currency.set("INR")
        tk.OptionMenu(root, self.alert_to_currency, *self.currencies).grid(row=11, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(root, text="Threshold Rate:", bg="#f0f8ff", font=("Arial", 10)).grid(row=12, column=0, padx=10, pady=5, sticky="w")
        self.threshold_entry = tk.Entry(root, font=("Arial", 10))
        self.threshold_entry.grid(row=12, column=1, padx=10, pady=5, sticky="ew")

        self.alert_button = tk.Button(root, text="Set Alert", command=self.set_rate_alert, bg="#87cefa", font=("Arial", 10))
        self.alert_button.grid(row=13, column=0, columnspan=2, pady=10, sticky="ew")

        for i in range(14):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.root.grid_columnconfigure(j, weight=1)

    def get_currencies(self):
        try:
            response = requests.get(self.api_url + "USD")
            data = response.json()
            self.currencies = list(data["rates"].keys())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch currencies: {e}")

    def convert_currency(self):
        def fetch_conversion():
            try:
                amount = float(self.amount_entry.get())
                from_curr = self.from_currency.get()
                to_curr = self.to_currency.get()

                response = requests.get(self.api_url + from_curr)
                data = response.json()

                rate = data["rates"].get(to_curr)
                if not rate:
                    messagebox.showerror("Error", "Invalid currency selection")
                    return

                converted_amount = amount * rate
                self.result_label.config(text=f"Converted Amount: {converted_amount:.2f} {to_curr}")

                self.history_table.insert("", "end", values=(amount, from_curr, to_curr, f"{converted_amount:.2f}"))

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
            except Exception as e:
                messagebox.showerror("Error", f"Conversion failed: {e}")

        threading.Thread(target=fetch_conversion).start()

    def clear_all(self):
        self.amount_entry.delete(0, tk.END)
        self.result_label.config(text="Converted Amount: ")
        for row in self.history_table.get_children():
            self.history_table.delete(row)

    def save_history(self):
        try:
            with open('conversion_history.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Amount", "From Currency", "To Currency", "Converted Amount"])
                for row in self.history_table.get_children():
                    writer.writerow(self.history_table.item(row)["values"])

            messagebox.showinfo("Success", "History saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {e}")

    def set_rate_alert(self):
        try:
            from_curr = self.alert_from_currency.get()
            to_curr = self.alert_to_currency.get()
            threshold = float(self.threshold_entry.get())

            def check_rate():
                response = requests.get(self.api_url + from_curr)
                data = response.json()
                rate = data["rates"].get(to_curr)

                if rate and rate >= threshold:
                    messagebox.showinfo("Rate Alert", f"The exchange rate for {from_curr} to {to_curr} has reached the threshold")

            threading.Thread(target=check_rate).start()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid threshold rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set alert: {e}")

    def show_graph(self):
        def fetch_graph_data():
            try:
                from_curr = self.from_currency.get()
                to_curr = self.to_currency.get()

                # Fetch exchange rates for the past 7 days
                days = 7
                dates = [datetime.now() - timedelta(days=i) for i in range(days)]
                rates = []

                for date in dates:
                    response = requests.get(self.api_url + from_curr)
                    data = response.json()
                    rate = data["rates"].get(to_curr)
                    rates.append(rate)

                # This will now run in the main thread
                def plot_graph():
                    plt.figure(figsize=(10, 5))
                    plt.plot(dates, rates, marker='o')
                    plt.title(f"Exchange Rate Trend ({from_curr} to {to_curr})")
                    plt.xlabel("Date")
                    plt.ylabel("Exchange Rate")
                    plt.xticks(rotation=45)
                    plt.grid(True)
                    plt.tight_layout()
                    plt.show()

                # Use Tkinter's `after()` to call the plotting function in the main thread
                self.root.after(0, plot_graph)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch data for graph: {e}")

        threading.Thread(target=fetch_graph_data).start()

# Main application window
root = tk.Tk()
root.title("Login & Register Form")
root.geometry("700x600")
root.minsize(500, 500)

# Configure grid layout
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Background frame
background_frame = tk.Frame(root, bg="#F7F7F7")  # Soft gray background
background_frame.grid(row=0, column=0, sticky="nsew")

background_frame.grid_rowconfigure(0, weight=1)
background_frame.grid_columnconfigure(0, weight=1)

# Content frame for login/register
content_frame = tk.Frame(background_frame, bg="#FFFFFF", bd=2, relief="ridge")
content_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

# Register frame
register_frame = tk.Frame(content_frame, bg="#FDF6E3")  # Soft cream background
register_frame.place(relwidth=1, relheight=1)

register_label = tk.Label(register_frame, text="Register", font=("Times New Roman", 26, "bold"), bg="#FDF6E3", fg="#333333")
register_label.pack(pady=20)

name_entry = tk.Entry(register_frame, font=("Verdana", 14))
name_entry.insert(0, "Name")


name_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=20)

email_entry = tk.Entry(register_frame, font=("Verdana", 14))
email_entry.insert(0, "Email")
email_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=20)

password_entry = tk.Entry(register_frame, show="*", font=("Verdana", 14))
password_entry.insert(0, "Password")
password_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=20)

register_button = tk.Button(register_frame, text="Register", command=register_user, bg="#4CAF50", fg="white", font=("Verdana", 14))
register_button.pack(pady=20, ipadx=5, ipady=5)

register_toggle = tk.Button(register_frame, text="Already have an account? Login", command=show_login, bg="#FDF6E3", fg="#007BFF", font=("Verdana", 12, "italic"), bd=0)
register_toggle.pack(pady=10)

# Login frame
login_frame = tk.Frame(content_frame, bg="#EAF7F7")  # Soft teal background
login_frame.place(relwidth=1, relheight=1)

login_label = tk.Label(login_frame, text="Login", font=("Times New Roman", 26, "bold"), bg="#EAF7F7", fg="#333333")
login_label.pack(pady=20)

login_email_entry = tk.Entry(login_frame, font=("Verdana", 14))
login_email_entry.insert(0, "Email")
login_email_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=20)

login_password_entry = tk.Entry(login_frame, show="*", font=("Verdana", 14))
login_password_entry.insert(0, "Password")
login_password_entry.pack(pady=10, ipadx=5, ipady=5, fill="x", padx=20)

login_button = tk.Button(login_frame, text="Login", command=login_user, bg="#4CAF50", fg="white", font=("Verdana", 14))
login_button.pack(pady=20, ipadx=5, ipady=5)

login_toggle = tk.Button(login_frame, text="Don't have an account? Register", command=show_register, bg="#EAF7F7", fg="#007BFF", font=("Verdana", 12, "italic"), bd=0)
login_toggle.pack(pady=10)

# Show login by default
show_login()

root.mainloop()