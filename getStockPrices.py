import requests
from bs4 import BeautifulSoup
import pyodbc
import tkinter as tk
from tkinter import ttk, simpledialog

def getData(symbol, cursor):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        url = 'https://finance.yahoo.com/quote/' + symbol
        r = requests.get(url, headers=headers)

        print(r.status_code)

        soup = BeautifulSoup(r.text, 'html.parser')
        print(soup.title.text)
        price = soup.find('div', {'class': 'D(ib) Mend(20px)'}).find_all('fin-streamer')[0].text
        change = soup.find('div', {'class': 'D(ib) Mend(20px)'}).find_all('fin-streamer')[1].text
        changePer = soup.find('div', {'class': 'D(ib) Mend(20px)'}).find_all('fin-streamer')[2].text

        # Insert the stock data into the SQL server
        cursor.execute("INSERT INTO StockData (Symbol, Price, Change, ChangePer) VALUES (?, ?, ?, ?)",
                    (symbol, price, change, changePer))

        return {
            'symbol': symbol,
            'price': price,
            'change': change,
            'changePer': changePer
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for symbol {symbol}: {e}")
    except Exception as e:
        print(f"Error processing data for symbol {symbol}: {e}")
    return None

# Function to fetch stock data and update the GUI
def fetch_stock_data():
    selected_table = table_var.get()
    for item in myStocks:
        stock = getData(item, cursor, selected_table)
        if stock:
            stockData.append(stock)
            result_text.insert(tk.END, f"Getting: {item}\n")

root = tk.Tk()
root.title("Stock Data GUI")

# Prompt user for database configuration
db_config = {}
db_config['Driver'] = simpledialog.askstring("Database Configuration", "Enter the ODBC Driver:", parent=root)
db_config['Server'] = simpledialog.askstring("Database Configuration", "Enter the Server name:", parent=root)
db_config['Database'] = simpledialog.askstring("Database Configuration", "Enter the Database name:", parent=root)
db_config['UID'] = simpledialog.askstring("Database Configuration", "Enter the Username:", parent=root)
db_config['PWD'] = simpledialog.askstring("Database Configuration", "Enter the Password:", parent=root)
 
connection = pyodbc.connect(**db_config)
cursor = connection.cursor()

""""
with pyodbc.connect(**db_config) as connection:
    # Create a cursor object using a context manager
    with connection.cursor() as cursor:
        for item in myStocks:
            stock = getData(item, cursor)
            if stock:
                stockData.append(stock)
                print('Getting:', item)
                connection.commit()
                """

myStocks = ['VAST.L', 'ICON.L', 'PREM.L', 'BZT.L']
stockData = []

root.geometry("600x400")

# Styling for the GUI
root.configure(bg="black")  # Set the background color to black

# Create the GUI elements
header_label = ttk.Label(root, text="Stock Data Fetcher", font=("Arial", 24, "bold"), foreground="white", background="black")
header_label.pack(pady=15)

table_label = ttk.Label(root, text="Select Table:", font=("Arial", 16), foreground="white", background="black")
table_label.pack()

table_options = ['Table1', 'Table2', 'Table3']  # Add your table names here
table_var = tk.StringVar(value=table_options[0])

table_menu = ttk.OptionMenu(root, table_var, *table_options)
table_menu.pack(pady=5)

fetch_button = ttk.Button(root, text="Fetch Stock Data", command=fetch_stock_data)
fetch_button.pack(pady=10)

result_text = tk.Text(root, width=50, height=12, font=("Arial", 10), wrap=tk.WORD, foreground="white", background="black")
result_text.pack()

# Start the main event loop
root.mainloop()

root.mainloop()

# Close the cursor and the connection
cursor.close()
connection.close()
