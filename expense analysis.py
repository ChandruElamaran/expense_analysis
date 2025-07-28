import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import matplotlib.pyplot as plt

# --- Database Setup ---
conn = sqlite3.connect('expenses.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT,
        category TEXT,
        amount REAL
    )
''')
conn.commit()

# --- Add Expense ---
def add_expense():
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    try:
        c.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                  (date, category, float(amount)))
        conn.commit()
        messagebox.showinfo("✅ Success", "Expense added successfully!")
        date_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        refresh_table()
    except ValueError:
        messagebox.showerror("❌ Error", "Please enter a valid amount.")

# --- Show Analytics ---
def show_analytics():
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    if not data:
        messagebox.showinfo("📊 No Data", "No expenses to analyze yet.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', colors=plt.cm.Set3.colors)
    plt.title("Spending Distribution", fontsize=14)
    plt.show()

# --- Delete Selected Expense ---
def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("⚠️ No Selection", "Please select a record to delete.")
        return
    confirm = messagebox.askyesno("❗ Confirm Delete", "Are you sure you want to delete the selected record?")
    if confirm:
        for item in selected:
            item_id = tree.item(item)["values"][0]
            c.execute("DELETE FROM expenses WHERE id = ?", (item_id,))
        conn.commit()
        refresh_table()

# --- Refresh Expense Table ---
def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    c.execute("SELECT id, date, category, amount FROM expenses ORDER BY date DESC")
    rows = c.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

# --- GUI Setup ---
app = tk.Tk()
app.title("💰 Smart Expense Tracker")
app.geometry("480x580")
BG_COLOR = "#fef9e7"
TEXT_COLOR = "#4e342e"
BUTTON_COLOR_1 = "#81c784"
BUTTON_COLOR_2 = "#64b5f6"
BUTTON_COLOR_3 = "#e57373"

app.configure(bg=BG_COLOR)

tk.Label(app, text="Track Your Expenses", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

form_frame = tk.Frame(app, bg=BG_COLOR)
form_frame.pack(pady=5)

# --- Date Entry ---
tk.Label(form_frame, text="📅 Date (YYYY-MM-DD)", font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")
date_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
date_entry.grid(row=0, column=1, pady=5)

# --- Category Entry ---
tk.Label(form_frame, text="📂 Category", font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w")
category_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
category_entry.grid(row=1, column=1, pady=5)

# --- Amount Entry ---
tk.Label(form_frame, text="💵 Amount", font=("Arial", 12), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky="w")
amount_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
amount_entry.grid(row=2, column=1, pady=5)

# --- Buttons ---
button_frame = tk.Frame(app, bg=BG_COLOR)
button_frame.pack(pady=10)

tk.Button(button_frame, text="➕ Add Expense", font=("Arial", 11, "bold"),
          bg=BUTTON_COLOR_1, fg="white", width=15, command=add_expense).grid(row=0, column=0, padx=5)

tk.Button(button_frame, text="📊 View Analytics", font=("Arial", 11, "bold"),
          bg=BUTTON_COLOR_2, fg="white", width=15, command=show_analytics).grid(row=0, column=1, padx=5)

# --- Expense Viewer ---
tk.Label(app, text="📋 Expense Records", font=("Arial", 14), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

table_frame = tk.Frame(app)
table_frame.pack(pady=5)

columns = ("ID", "Date", "Category", "Amount")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")
tree.pack()

# --- Delete Button ---
tk.Button(app, text="🗑️ Delete Selected", font=("Arial", 11, "bold"),
          bg=BUTTON_COLOR_3, fg="white", width=18, command=delete_selected).pack(pady=10)

# --- Populate Table Initially ---
refresh_table()

# --- Run App ---
app.mainloop()
conn.close()