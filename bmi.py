import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        # Create a database connection and cursor
        self.conn = sqlite3.connect("bmi_data.db")
        self.cursor = self.conn.cursor()

        # Create the BMI data table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                weight REAL,
                height REAL,
                bmi REAL
            )
        ''')
        self.conn.commit()

        # GUI components
        self.weight_label = ttk.Label(root, text="Weight (kg):")
        self.weight_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.weight_entry = ttk.Entry(root)
        self.weight_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.height_label = ttk.Label(root, text="Height (m):")
        self.height_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.height_entry = ttk.Entry(root)
        self.height_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.calculate_button = ttk.Button(root, text="Calculate BMI", command=self.calculate_bmi)
        self.calculate_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.view_history_button = ttk.Button(root, text="View History", command=self.view_history)
        self.view_history_button.grid(row=3, column=0, columnspan=2, pady=10)

    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if weight <= 0 or height <= 0:
                messagebox.showerror("Error", "Weight and height must be greater than 0.")
                return

            bmi = weight / (height ** 2)

            # Save BMI data to the database
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO bmi_data (date, weight, height, bmi) VALUES (?, ?, ?, ?)
            ''', (current_date, weight, height, bmi))
            self.conn.commit()

            messagebox.showinfo("BMI Result", f"Your BMI is: {bmi:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for weight and height.")

    def view_history(self):
        # Retrieve BMI data from the database
        self.cursor.execute("SELECT date, bmi FROM bmi_data")
        data = self.cursor.fetchall()

        if not data:
            messagebox.showinfo("History", "No BMI data available.")
            return

        # Plot BMI trends
        dates, bmis = zip(*data)
        fig, ax = plt.subplots()
        ax.plot(dates, bmis, marker='o', linestyle='-', color='b')
        ax.set_title('BMI Trend Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('BMI')

        # Embed the Matplotlib plot in the Tkinter window
        graph_frame = tk.Toplevel(self.root)
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add a toolbar to the Matplotlib plot
        toolbar = ttk.Frame(graph_frame)
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        ttk.Button(toolbar, text="Close", command=graph_frame.destroy).pack(side=tk.RIGHT)

        graph_frame.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()
