import tkinter as tk
from tkinter import messagebox
import requests
from tkinter import ttk
import threading
import time
import csv
import openpyxl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


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


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
