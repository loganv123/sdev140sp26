'''
File: M08_FinalProject_LV.py
Author: Logan Vanhuffel
Date: 3/5/2026

This is a simple inventory management system built with Python's Tkinter library.
It allows users to add, edit, and delete inventory items, which are stored in a local
JSON file for persistence. The app features a clean UI with a table view of items and input validation.
'''
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class InventoryManager:
    """
    Handles loading, saving, and modifying inventory data.
    This class is the data layer of the app.
    All items are stored in a JSON file localy.
    """
    def __init__(self, filename="inventory.json"):
        """
        Initializa the manager.
        filename: path to JSON file for storage.
        Loads any existing data on app launch.
        """
        self.filename = filename
        self.data = [] # List of item dictionaries
        self.load()

    def load(self):
        """
        Load inventory data from the JSON file.
        If the file does not exist, start with an empty list.
        """
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def save(self):
        """
        Save the current inventory list to the JSON file.
        """
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_item(self, item):
        """
        Add a new item to the inventory and saves file.
        item: dictionary with Name, Quantity, Price, Category.
        """
        self.data.append(item)
        self.save()

    def update_item(self, index, item):
        """
        Replace the item at the given index with new data.
        """
        self.data[index] = item
        self.save()

    def delete_item(self, index):
        """
        Remove the item at the given index.
        """
        del self.data[index]
        self.save()



class AddItemWindow:
    """
    Popup window used for both adding and editing items.
    Collects user input and returns it to the main window using a callback.
    """
    def __init__(self, parent, callback, item=None):
        """
        parent: the main Tk window.
        callback: function to call when the user clicks save.
        item: existing item data when editing, or Nine when adding.
        """
        self.parent = parent
        self.callback = callback # Stores callback for later use
        self.item = item         # Used to pre fill fields when editing items.

        # Creates the popup window
        self.window = tk.Toplevel(parent)
        self.window.title("Add Item" if item is None else "Edit Item")
        self.window.geometry("350x300")
        self.window.resizable(False, False)

        self.build_form()

    def build_form(self):
        """
        Build all input fields and buttons inside the popup window.
        Pre fill fields if editing an item.
        """
        options = ["Clothing/Apparel", "Food/Groceries", "Electronics/Technology", "Furniture/Home Goods",
                    "Personal Care/Health", "Cleaning Supplies", "Entertainment/Media"]
        
        # Labels and input fields
        ttk.Label(self.window, text="Name:", font=("Segoe UI", 12)).pack(anchor="center", padx=20, pady=5)
        self.name_entry = ttk.Entry(self.window, width=30)
        self.name_entry.pack(padx=20)

        ttk.Label(self.window, text="Quantity:", font=("Segoe UI", 12)).pack(anchor="center", padx=20, pady=5)
        self.qty_entry = ttk.Entry(self.window, width=30)
        self.qty_entry.pack(padx=20)

        ttk.Label(self.window, text="Price:", font=("Segoe UI", 12)).pack(anchor="center", padx=20, pady=5)
        self.price_entry = ttk.Entry(self.window, width=30)
        self.price_entry.pack(padx=20)

        ttk.Label(self.window, text="Category:", font=("Segoe UI", 12)).pack(anchor="center", padx=20, pady=5)
        self.cat_entry = ttk.Combobox(self.window, values=options, width=30)
        self.cat_entry.pack(padx=20)
        

        # Pre fill fields when editing
        if self.item:
            self.name_entry.insert(0, self.item["Name"])
            self.qty_entry.insert(0, self.item["Quantity"])
            self.price_entry.insert(0, self.item["Price"])
            self.cat_entry.insert(0, self.item["Category"])

        # Buttons for saving data and quiting the window without having to press the X
        ttk.Button(self.window, text="Save", command=self.save).pack(pady=20)
        ttk.Button(self.window, text="Quit", command=self.window.destroy).place(x=250, y=244)


    def save(self):
        """
        Validate user input.
        If valid, build an item dictionary and pass it to the callback.
        Then close the popup window.
        """
        name = self.name_entry.get().strip()
        qty = self.qty_entry.get().strip()
        price = self.price_entry.get().strip()
        category = self.cat_entry.get().strip()

        # Validation rules
        if not name:
            messagebox.showerror("Invalid Input", "Name cannot be empty.")
            self.window.lift()
            return

        if not qty.isdigit(): # Quantity must be a whole number
            messagebox.showerror("Invalid Input", "Quantity must be a whole number.")
            self.window.lift()
            return

        try:
            float(price) # Price must be numeric
        except ValueError:
            messagebox.showerror("Invalid Input", "Price must be a valid number.")
            self.window.lift()
            return

        if not category:
            messagebox.showerror("Invalid Input", "Please select a category.")
            self.window.lift()
            return

        # If all validation passes, build the item dictionary
        item = {
            "Name": name,
            "Quantity": int(qty),
            "Price": float(price),
            "Category": category
        }

        # Call the callback to return data to the main window
        self.callback(item)
        
        # Close the popup
        self.window.destroy()



class InventoryApp:
    """
    Main application window.
    Displays the inventory table and provides buttons for actions.
    Corrdinates between the UI and the Inventory Manager.
    """
    def __init__(self, root):
        """
        Initialize the main window and build all UI components.
        """
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x500")

        self.manager = InventoryManager() # Handles data storage

        self.build_layout()
        self.build_table()
        self.build_buttons()
        self.refresh_table()

    def build_layout(self):
        """
        Create the main layout frames for the table and buttons.
        """
        self.table_frame = ttk.Frame(self.root, padding=10)
        self.table_frame.pack(fill="both", expand=True)

        self.button_frame = ttk.Frame(self.root, padding=10)
        self.button_frame.pack(fill="x")

    def build_table(self):
        """
        Create the treeview table that displays inventory items.
        """
        columns = ("Name", "Quantity", "Price", "Category")

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        # Set up column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def build_buttons(self):
        """
        Create all action buttons.
        """
        ttk.Button(self.button_frame, text="Add Item", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Edit Item", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Delete Item", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Refresh", command=self.refresh_table).pack(side="left", padx=5)
        ttk.Button(self.button_frame, text="Quit", command=self.root.destroy).pack(side="right", padx=5)


    # BUTTON ACTIONS
    def add_item(self):
        """
        Open the AddItemWindow for creating a new item.
        Pass add_item_callback so the popup can return the new item.
        """
        AddItemWindow(self.root, self.add_item_callback)

    def add_item_callback(self, item):
        """
        Called by AddItemWindow when the user saves a new item.
        Add the item to the inventory and refreshes the table.
        """
        self.manager.add_item(item)
        self.refresh_table()

    def edit_item(self):
        """
        Open the AddItemWindow with existing data for editing.
        Uses a lambda callback to pass both index and updated item.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select an item to edit")
            return

        index = self.tree.index(selected[0])
        item = self.manager.data[index]

        AddItemWindow(self.root, lambda new_item: self.edit_item_callback(index, new_item), item)

    def edit_item_callback(self, index, item):
        """
        Update the item at the given index and refresh the table.
        """
        self.manager.update_item(index, item)
        self.refresh_table()

    def delete_item(self):
        """
        Delete the selected item after confirmation.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select an item to delete")
            return

        if not messagebox.askyesno("Delete?", "Are you sure you want to delete this item?"):
            return

        index = self.tree.index(selected[0])
        self.manager.delete_item(index)
        self.refresh_table()

    def refresh_table(self):
        """
        Clear the table and repopulate it with current inventory data.
        """

        # Remove all existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert updated rows
        for item in self.manager.data:
            self.tree.insert("", "end", values=(item["Name"], item["Quantity"], item["Price"], item["Category"]))



# RUN APP
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()

