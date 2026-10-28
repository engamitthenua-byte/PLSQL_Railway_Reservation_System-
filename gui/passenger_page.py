"""
Passenger Management Page View for Smart Railway Reservation System.
Implements full CRUD operations for passengers using Oracle Database & PL/SQL.
- Register passenger (REGISTER_PASSENGER stored procedure)
- View and search passengers by ID or name
- Update passenger details (UPDATE_PASSENGER stored procedure)
- Delete passenger (DELETE_PASSENGER stored procedure, enforcing historical retention rules)
- Inspect passenger reservation history
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from gui.theme import COLORS, FONTS
from services.passenger_service import (
    register_passenger,
    update_passenger,
    delete_passenger,
    get_all_passengers,
    search_passengers,
    get_passenger_history
)


class PassengerPage(tk.Frame):
    """Passenger CRUD administration and reservation history interface."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.all_passengers: List[Dict[str, Any]] = []
        self.selected_passenger_id: Optional[int] = None

        self.id_lbl = None
        self.name_entry = None
        self.age_entry = None
        self.gender_combo = None
        self.phone_entry = None
        self.email_entry = None
        self.search_entry = None
        self.pass_tree = None
        self.hist_tree = None
        self.hist_title = None

        self.update_btn = None
        self.delete_btn = None
        self.submit_btn = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=COLORS["bg_main"])
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text="Passenger Management (Oracle Database CRUD)",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="PL/SQL Stored Procedures: REGISTER_PASSENGER, UPDATE_PASSENGER, DELETE_PASSENGER",
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w")

        refresh_btn = tk.Button(
            header,
            text="↻ Refresh Records",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.load_data
        )
        refresh_btn.pack(side="right")

        # Top Registration / Edit Form Card
        form_card_outer = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        form_card_outer.pack(fill="x", padx=20, pady=(0, 15))

        form_card = tk.Frame(form_card_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        form_card.pack(fill="both", expand=True)

        form_hdr = tk.Frame(form_card, bg=COLORS["bg_card"])
        form_hdr.pack(fill="x", pady=(0, 10))

        self.form_mode_lbl = tk.Label(
            form_hdr,
            text="Register New Passenger or Select Row Below to Edit / Delete",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        )
        self.form_mode_lbl.pack(side="left")

        self.id_lbl = tk.Label(
            form_hdr,
            text="Mode: New Registration",
            font=FONTS["small_bold"],
            bg="#F1F5F9",
            fg=COLORS["primary"],
            padx=8,
            pady=2
        )
        self.id_lbl.pack(side="right")

        grid = tk.Frame(form_card, bg=COLORS["bg_card"])
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=2)
        grid.columnconfigure(3, weight=1)
        grid.columnconfigure(5, weight=1)
        grid.columnconfigure(7, weight=2)
        grid.columnconfigure(9, weight=2)

        # Fields row
        tk.Label(grid, text="Full Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.name_entry = ttk.Entry(grid, font=FONTS["body"])
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        tk.Label(grid, text="Age:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.age_entry = ttk.Entry(grid, font=FONTS["body"], width=6)
        self.age_entry.grid(row=0, column=3, sticky="ew", padx=(0, 10))

        tk.Label(grid, text="Gender:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=4, sticky="w", padx=(0, 4))
        self.gender_combo = ttk.Combobox(grid, state="readonly", values=["Male", "Female", "Other"], width=8, font=FONTS["body"])
        self.gender_combo.set("Male")
        self.gender_combo.grid(row=0, column=5, sticky="ew", padx=(0, 10))

        tk.Label(grid, text="Phone:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=6, sticky="w", padx=(0, 4))
        self.phone_entry = ttk.Entry(grid, font=FONTS["body"])
        self.phone_entry.grid(row=0, column=7, sticky="ew", padx=(0, 10))

        tk.Label(grid, text="Email:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=8, sticky="w", padx=(0, 4))
        self.email_entry = ttk.Entry(grid, font=FONTS["body"])
        self.email_entry.grid(row=0, column=9, sticky="ew")

        # Action Buttons
        btn_box = tk.Frame(form_card, bg=COLORS["bg_card"])
        btn_box.pack(fill="x", pady=(12, 0))

        self.submit_btn = tk.Button(
            btn_box,
            text="+ Register Passenger",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.submit_register
        )
        self.submit_btn.pack(side="right", padx=(8, 0))

        self.update_btn = tk.Button(
            btn_box,
            text="💾 Update Passenger",
            font=FONTS["body_bold"],
            bg=COLORS["secondary"],
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            state="disabled",
            command=self.submit_update
        )
        self.update_btn.pack(side="right", padx=(8, 0))

        self.delete_btn = tk.Button(
            btn_box,
            text="🗑 Delete Passenger",
            font=FONTS["body_bold"],
            bg=COLORS["danger"],
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            state="disabled",
            command=self.submit_delete
        )
        self.delete_btn.pack(side="right", padx=(8, 0))

        clear_btn = tk.Button(
            btn_box,
            text="Clear Form",
            font=FONTS["small_bold"],
            bg="#E2E8F0",
            fg=COLORS["text_dark"],
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.clear_form
        )
        clear_btn.pack(side="left")

        # Lower Split Layout (Left: Passengers Table; Right: Passenger History)
        split = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        split.pack(fill="both", expand=True, pady=(0, 20))
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)

        # 1. Passengers Table (Left)
        p_outer = tk.Frame(split, bg=COLORS["border"], padx=1, pady=1)
        p_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        p_card = tk.Frame(p_outer, bg=COLORS["bg_card"], padx=14, pady=12)
        p_card.pack(fill="both", expand=True)

        hdr_p = tk.Frame(p_card, bg=COLORS["bg_card"])
        hdr_p.pack(fill="x", pady=(0, 8))

        tk.Label(hdr_p, text="Registered Passengers in Oracle DB", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(side="left")

        self.search_entry = ttk.Entry(hdr_p, font=FONTS["body"], width=20)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_passengers())

        tk.Label(hdr_p, text="Search (ID / Name):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="right", padx=(10, 4))

        cols = ("id", "name", "age", "gender", "phone", "email", "reg_date")
        self.pass_tree = ttk.Treeview(p_card, columns=cols, show="headings", height=10)

        self.pass_tree.heading("id", text="ID")
        self.pass_tree.heading("name", text="Full Name")
        self.pass_tree.heading("age", text="Age")
        self.pass_tree.heading("gender", text="Gender")
        self.pass_tree.heading("phone", text="Phone Number")
        self.pass_tree.heading("email", text="Email Address")
        self.pass_tree.heading("reg_date", text="Registered")

        self.pass_tree.column("id", width=45, anchor="center")
        self.pass_tree.column("name", width=140, anchor="w")
        self.pass_tree.column("age", width=45, anchor="center")
        self.pass_tree.column("gender", width=60, anchor="center")
        self.pass_tree.column("phone", width=105, anchor="center")
        self.pass_tree.column("email", width=155, anchor="w")
        self.pass_tree.column("reg_date", width=110, anchor="center")

        p_scroll = ttk.Scrollbar(p_card, orient="vertical", command=self.pass_tree.yview)
        self.pass_tree.configure(yscrollcommand=p_scroll.set)

        self.pass_tree.pack(side="left", fill="both", expand=True)
        p_scroll.pack(side="right", fill="y")
        self.pass_tree.bind("<<TreeviewSelect>>", lambda e: self.on_passenger_selected())

        # 2. History Table (Right)
        h_outer = tk.Frame(split, bg=COLORS["border"], padx=1, pady=1)
        h_outer.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        h_card = tk.Frame(h_outer, bg=COLORS["bg_card"], padx=14, pady=12)
        h_card.pack(fill="both", expand=True)

        self.hist_title = tk.Label(h_card, text="Reservation History", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"])
        self.hist_title.pack(anchor="w", pady=(0, 8))

        h_cols = ("pnr", "train", "route", "date", "class", "fare", "status")
        self.hist_tree = ttk.Treeview(h_card, columns=h_cols, show="headings", height=10)

        self.hist_tree.heading("pnr", text="PNR")
        self.hist_tree.heading("train", text="Train")
        self.hist_tree.heading("route", text="Route")
        self.hist_tree.heading("date", text="Date")
        self.hist_tree.heading("class", text="Class")
        self.hist_tree.heading("fare", text="Fare")
        self.hist_tree.heading("status", text="Status")

        self.hist_tree.column("pnr", width=95, anchor="center")
        self.hist_tree.column("train", width=65, anchor="center")
        self.hist_tree.column("route", width=90, anchor="center")
        self.hist_tree.column("date", width=80, anchor="center")
        self.hist_tree.column("class", width=45, anchor="center")
        self.hist_tree.column("fare", width=70, anchor="e")
        self.hist_tree.column("status", width=80, anchor="center")

        h_scroll = ttk.Scrollbar(h_card, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=h_scroll.set)

        self.hist_tree.pack(side="left", fill="both", expand=True)
        h_scroll.pack(side="right", fill="y")

    def load_data(self):
        """Loads all passengers from Oracle database."""
        try:
            self.all_passengers = get_all_passengers()
            self.filter_passengers()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load passengers:\n{e}")

    def filter_passengers(self):
        """Filters passenger table by keyword."""
        kw = self.search_entry.get().strip().lower()
        for item in self.pass_tree.get_children():
            self.pass_tree.delete(item)

        for p in self.all_passengers:
            if (not kw or
                kw in str(p["passenger_id"]).lower() or
                kw in p["full_name"].lower() or
                kw in p["phone_number"].lower() or
                kw in p["email"].lower()):
                self.pass_tree.insert(
                    "",
                    "end",
                    values=(
                        p["passenger_id"],
                        p["full_name"],
                        p["age"],
                        p["gender"],
                        p["phone_number"],
                        p["email"],
                        p["reg_date"]
                    )
                )

    def on_passenger_selected(self):
        """Populates the form and loads history when a passenger row is selected."""
        selected = self.pass_tree.selection()
        if not selected:
            return

        item = self.pass_tree.item(selected[0])
        pid = int(item["values"][0])
        pname = item["values"][1]
        page = item["values"][2]
        pgender = item["values"][3]
        pphone = str(item["values"][4])
        pemail = item["values"][5]

        self.selected_passenger_id = pid

        # Pre-fill editing fields
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, pname)

        self.age_entry.delete(0, "end")
        self.age_entry.insert(0, str(page))

        self.gender_combo.set(pgender)

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, pphone)

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, pemail)

        # Update mode status and button states
        self.id_lbl.config(text=f"Selected ID: #{pid}", fg=COLORS["secondary"])
        self.form_mode_lbl.config(text=f"Edit Passenger: #{pid} - {pname}")
        self.update_btn.config(state="normal")
        self.delete_btn.config(state="normal")

        # Load reservation history for this passenger
        self.hist_title.config(text=f"Reservation History: #{pid} ({pname})")
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)

        history = get_passenger_history(pid)
        for h in history:
            tag = h["booking_status"].lower()
            route_str = f"{h['from_code']}➔{h['to_code']}"
            self.hist_tree.insert(
                "",
                "end",
                values=(
                    h["pnr_number"],
                    h["train_number"],
                    route_str,
                    str(h["journey_date"])[:10],
                    h["seat_class"],
                    f"₹{float(h['total_fare']):.0f}",
                    h["booking_status"]
                ),
                tags=(tag,)
            )

        self.hist_tree.tag_configure("confirmed", foreground=COLORS["success"])
        self.hist_tree.tag_configure("cancelled", foreground=COLORS["danger"])

    def clear_form(self):
        """Resets the form to new passenger registration mode."""
        self.selected_passenger_id = None
        self.name_entry.delete(0, "end")
        self.age_entry.delete(0, "end")
        self.gender_combo.set("Male")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")

        self.id_lbl.config(text="Mode: New Registration", fg=COLORS["primary"])
        self.form_mode_lbl.config(text="Register New Passenger or Select Row Below to Edit / Delete")
        self.update_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")

    def submit_register(self):
        """Invokes PL/SQL REGISTER_PASSENGER stored procedure."""
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_combo.get()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not age_str or not phone or not email:
            messagebox.showwarning("Incomplete Form", "Please fill in all passenger fields.")
            return

        try:
            age = int(age_str)
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Age", "Age must be an integer between 1 and 120.")
            return

        ok, msg, pid = register_passenger(name, age, gender, phone, email)
        if ok and pid:
            messagebox.showinfo("Success", f"Passenger registered successfully with ID #{pid}!")
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", msg)

    def submit_update(self):
        """Invokes PL/SQL UPDATE_PASSENGER stored procedure."""
        if not self.selected_passenger_id:
            messagebox.showwarning("Select Record", "Please select a passenger from the table to update.")
            return

        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_combo.get()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not age_str or not phone or not email:
            messagebox.showwarning("Incomplete Form", "Please fill in all passenger fields.")
            return

        try:
            age = int(age_str)
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Age", "Age must be an integer between 1 and 120.")
            return

        ok, msg = update_passenger(self.selected_passenger_id, name, age, gender, phone, email)
        if ok:
            messagebox.showinfo("Success", msg)
            self.load_data()
        else:
            messagebox.showerror("Update Error", msg)

    def submit_delete(self):
        """Invokes PL/SQL DELETE_PASSENGER stored procedure with integrity checks."""
        if not self.selected_passenger_id:
            messagebox.showwarning("Select Record", "Please select a passenger from the table to delete.")
            return

        name = self.name_entry.get().strip()
        confirm = messagebox.askyesno(
            "Confirm Passenger Deletion",
            f"Are you sure you want to delete passenger #{self.selected_passenger_id} ({name})?\n\n"
            f"Note: Oracle Database will reject deletion if this passenger has active or historical reservations."
        )
        if not confirm:
            return

        ok, msg = delete_passenger(self.selected_passenger_id)
        if ok:
            messagebox.showinfo("Deleted", msg)
            self.clear_form()
            self.load_data()
            for item in self.hist_tree.get_children():
                self.hist_tree.delete(item)
            self.hist_title.config(text="Reservation History")
        else:
            messagebox.showerror("Integrity Error", msg)
