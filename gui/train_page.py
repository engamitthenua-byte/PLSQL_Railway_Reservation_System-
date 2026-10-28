"""
Train Management Page View for Smart Railway Reservation System.
Implements train fleet administration using Oracle Database & PL/SQL.
- Add new train services (ADD_TRAIN stored procedure)
- View all trains and search by train number or name
- Update train info and operational status (UPDATE_TRAIN stored procedure)
- View intermediate station stops and schedule seating inventory capacity
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from gui.theme import COLORS, FONTS
from services.train_service import (
    add_train,
    update_train,
    get_all_trains,
    search_trains_by_keyword,
    get_train_stops,
    get_train_schedule_inventory
)
from services.station_service import get_all_stations


class TrainPage(tk.Frame):
    """Train fleet administration, stop inspection, and capacity inventory interface."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.stations = []
        self.station_map = {}
        self.trains = []
        self.selected_train_id: Optional[int] = None

        self.t_num_entry = None
        self.t_name_entry = None
        self.t_type_combo = None
        self.src_combo = None
        self.dst_combo = None
        self.cap_entry = None
        self.status_combo = None
        self.search_entry = None

        self.train_tree = None
        self.stops_tree = None
        self.inventory_tree = None
        self.stops_title = None

        self.update_btn = None
        self.add_btn = None
        self.mode_lbl = None

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
            text="Train Fleet & Schedule Inventory Management",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="PL/SQL Stored Procedures: ADD_TRAIN, UPDATE_TRAIN, UPDATE_TRAIN_SCHEDULE | Triggers: TRG_TRAIN_AUDIT",
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w")

        refresh_btn = tk.Button(
            header,
            text="↻ Refresh Fleet",
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

        # Top Registration / Update Form Card
        form_card_outer = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        form_card_outer.pack(fill="x", padx=20, pady=(0, 15))

        form_card = tk.Frame(form_card_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        form_card.pack(fill="both", expand=True)

        form_top = tk.Frame(form_card, bg=COLORS["bg_card"])
        form_top.pack(fill="x", pady=(0, 10))

        self.mode_lbl = tk.Label(
            form_top,
            text="Register New Train Service or Select a Row Below to Modify",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        )
        self.mode_lbl.pack(side="left")

        self.id_badge = tk.Label(
            form_top,
            text="Mode: New Train",
            font=FONTS["small_bold"],
            bg="#F1F5F9",
            fg=COLORS["primary"],
            padx=8,
            pady=2
        )
        self.id_badge.pack(side="right")

        grid = tk.Frame(form_card, bg=COLORS["bg_card"])
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=2)
        grid.columnconfigure(5, weight=1)
        grid.columnconfigure(7, weight=1)

        # Row 0
        tk.Label(grid, text="Train Number:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", pady=4, padx=(0, 4))
        self.t_num_entry = ttk.Entry(grid, font=FONTS["body"])
        self.t_num_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(0, 12))

        tk.Label(grid, text="Train Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=2, sticky="w", pady=4, padx=(0, 4))
        self.t_name_entry = ttk.Entry(grid, font=FONTS["body"])
        self.t_name_entry.grid(row=0, column=3, sticky="ew", pady=4, padx=(0, 12))

        tk.Label(grid, text="Train Type:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=4, sticky="w", pady=4, padx=(0, 4))
        self.t_type_combo = ttk.Combobox(grid, state="readonly", values=["Rajdhani", "Shatabdi", "Superfast", "Express", "Duronto"], font=FONTS["body"])
        self.t_type_combo.set("Superfast")
        self.t_type_combo.grid(row=0, column=5, sticky="ew", pady=4, padx=(0, 12))

        tk.Label(grid, text="Status:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=6, sticky="w", pady=4, padx=(0, 4))
        self.status_combo = ttk.Combobox(grid, state="readonly", values=["ACTIVE", "MAINTENANCE", "CANCELLED"], font=FONTS["body"], width=12)
        self.status_combo.set("ACTIVE")
        self.status_combo.grid(row=0, column=7, sticky="ew", pady=4)

        # Row 1
        tk.Label(grid, text="Origin Station:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=4, padx=(0, 4))
        self.src_combo = ttk.Combobox(grid, state="readonly", font=FONTS["body"])
        self.src_combo.grid(row=1, column=1, sticky="ew", pady=4, padx=(0, 12))

        tk.Label(grid, text="Destination:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=2, sticky="w", pady=4, padx=(0, 4))
        self.dst_combo = ttk.Combobox(grid, state="readonly", font=FONTS["body"])
        self.dst_combo.grid(row=1, column=3, sticky="ew", pady=4, padx=(0, 12))

        tk.Label(grid, text="Seating Capacity:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=4, sticky="w", pady=4, padx=(0, 4))
        self.cap_entry = ttk.Entry(grid, font=FONTS["body"])
        self.cap_entry.insert(0, "720")
        self.cap_entry.grid(row=1, column=5, sticky="ew", pady=4, padx=(0, 12))

        # Actions Row
        btn_bar = tk.Frame(form_card, bg=COLORS["bg_card"])
        btn_bar.pack(fill="x", pady=(10, 0))

        self.add_btn = tk.Button(
            btn_bar,
            text="+ Register Train in Oracle DB",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.submit_add_train
        )
        self.add_btn.pack(side="right", padx=(8, 0))

        self.update_btn = tk.Button(
            btn_bar,
            text="💾 Update Train & Status",
            font=FONTS["body_bold"],
            bg=COLORS["secondary"],
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            state="disabled",
            command=self.submit_update_train
        )
        self.update_btn.pack(side="right", padx=(8, 0))

        clear_btn = tk.Button(
            btn_bar,
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

        # Lower Split Layout (Left: All Trains Table with Search; Right: Notebook for Stops & Capacity)
        split = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        split.pack(fill="both", expand=True, pady=(0, 20))
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)

        # 1. Trains Table (Left)
        t_outer = tk.Frame(split, bg=COLORS["border"], padx=1, pady=1)
        t_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        t_card = tk.Frame(t_outer, bg=COLORS["bg_card"], padx=14, pady=12)
        t_card.pack(fill="both", expand=True)

        t_hdr = tk.Frame(t_card, bg=COLORS["bg_card"])
        t_hdr.pack(fill="x", pady=(0, 8))

        tk.Label(t_hdr, text="Trains in Service (Click to inspect / edit)", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(side="left")

        self.search_entry = ttk.Entry(t_hdr, font=FONTS["body"], width=18)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_trains())

        tk.Label(t_hdr, text="Search (No / Name):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="right", padx=(10, 4))

        cols = ("id", "number", "name", "type", "route", "capacity", "status")
        self.train_tree = ttk.Treeview(t_card, columns=cols, show="headings", height=10)

        self.train_tree.heading("id", text="ID")
        self.train_tree.heading("number", text="Train No")
        self.train_tree.heading("name", text="Train Name")
        self.train_tree.heading("type", text="Type")
        self.train_tree.heading("route", text="Route Terminals")
        self.train_tree.heading("capacity", text="Capacity")
        self.train_tree.heading("status", text="Status")

        self.train_tree.column("id", width=35, anchor="center")
        self.train_tree.column("number", width=75, anchor="center")
        self.train_tree.column("name", width=170, anchor="w")
        self.train_tree.column("type", width=85, anchor="center")
        self.train_tree.column("route", width=115, anchor="center")
        self.train_tree.column("capacity", width=70, anchor="center")
        self.train_tree.column("status", width=85, anchor="center")

        t_scroll = ttk.Scrollbar(t_card, orient="vertical", command=self.train_tree.yview)
        self.train_tree.configure(yscrollcommand=t_scroll.set)

        self.train_tree.pack(side="left", fill="both", expand=True)
        t_scroll.pack(side="right", fill="y")
        self.train_tree.bind("<<TreeviewSelect>>", lambda e: self.on_train_selected())

        # 2. Detail Notebook (Right: Tab 1 = Stops, Tab 2 = Seating Inventory)
        detail_outer = tk.Frame(split, bg=COLORS["border"], padx=1, pady=1)
        detail_outer.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        detail_card = tk.Frame(detail_outer, bg=COLORS["bg_card"], padx=12, pady=10)
        detail_card.pack(fill="both", expand=True)

        self.stops_title = tk.Label(detail_card, text="Train Schedule & Seating Inventory", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"])
        self.stops_title.pack(anchor="w", pady=(0, 6))

        self.notebook = ttk.Notebook(detail_card)
        self.notebook.pack(fill="both", expand=True)

        # TAB 1: Stops
        tab_stops = tk.Frame(self.notebook, bg=COLORS["bg_card"])
        self.notebook.add(tab_stops, text="Intermediate Stops")

        s_cols = ("seq", "code", "city", "arr", "dep", "dist", "day")
        self.stops_tree = ttk.Treeview(tab_stops, columns=s_cols, show="headings", height=8)

        self.stops_tree.heading("seq", text="#")
        self.stops_tree.heading("code", text="Station")
        self.stops_tree.heading("city", text="City")
        self.stops_tree.heading("arr", text="Arr")
        self.stops_tree.heading("dep", text="Dep")
        self.stops_tree.heading("dist", text="Dist (km)")
        self.stops_tree.heading("day", text="Day")

        self.stops_tree.column("seq", width=35, anchor="center")
        self.stops_tree.column("code", width=65, anchor="center")
        self.stops_tree.column("city", width=95, anchor="w")
        self.stops_tree.column("arr", width=55, anchor="center")
        self.stops_tree.column("dep", width=55, anchor="center")
        self.stops_tree.column("dist", width=65, anchor="center")
        self.stops_tree.column("day", width=40, anchor="center")

        s_scroll = ttk.Scrollbar(tab_stops, orient="vertical", command=self.stops_tree.yview)
        self.stops_tree.configure(yscrollcommand=s_scroll.set)
        self.stops_tree.pack(side="left", fill="both", expand=True)
        s_scroll.pack(side="right", fill="y")

        # TAB 2: Seating Capacity Inventory
        tab_inv = tk.Frame(self.notebook, bg=COLORS["bg_card"])
        self.notebook.add(tab_inv, text="Seating Capacity (Inventory)")

        inv_cols = ("date", "class", "total", "booked", "avail")
        self.inventory_tree = ttk.Treeview(tab_inv, columns=inv_cols, show="headings", height=8)

        self.inventory_tree.heading("date", text="Schedule Date")
        self.inventory_tree.heading("class", text="Class")
        self.inventory_tree.heading("total", text="Total Seats")
        self.inventory_tree.heading("booked", text="Booked")
        self.inventory_tree.heading("avail", text="Available")

        self.inventory_tree.column("date", width=95, anchor="center")
        self.inventory_tree.column("class", width=65, anchor="center")
        self.inventory_tree.column("total", width=75, anchor="center")
        self.inventory_tree.column("booked", width=75, anchor="center")
        self.inventory_tree.column("avail", width=75, anchor="center")

        inv_scroll = ttk.Scrollbar(tab_inv, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=inv_scroll.set)
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        inv_scroll.pack(side="right", fill="y")

    def load_data(self):
        """Loads stations and trains from database."""
        try:
            self.stations = get_all_stations()
            options = []
            for s in self.stations:
                disp = f"{s['station_code']} - {s['station_name']}"
                options.append(disp)
                self.station_map[disp] = s["station_id"]

            self.src_combo["values"] = options
            self.dst_combo["values"] = options
            if len(options) >= 2:
                self.src_combo.set(options[0])
                self.dst_combo.set(options[1])

            self.refresh_trains_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load train data: {e}")

    def refresh_trains_table(self):
        """Refreshes the trains treeview."""
        self.trains = get_all_trains()
        self.filter_trains()

    def filter_trains(self):
        """Filters the train table by keyword."""
        kw = self.search_entry.get().strip().lower()
        for item in self.train_tree.get_children():
            self.train_tree.delete(item)

        for t in self.trains:
            if (not kw or
                kw in str(t["train_number"]).lower() or
                kw in t["train_name"].lower() or
                kw in t["train_type"].lower()):
                route_str = f"{t['source_code']} ➔ {t['dest_code']}"
                tag = t["status"].lower()
                self.train_tree.insert(
                    "",
                    "end",
                    values=(
                        t["train_id"],
                        t["train_number"],
                        t["train_name"],
                        t["train_type"],
                        route_str,
                        t["total_capacity"],
                        t["status"]
                    ),
                    tags=(tag,)
                )

        self.train_tree.tag_configure("active", foreground=COLORS["success"])
        self.train_tree.tag_configure("maintenance", foreground=COLORS["warning"])
        self.train_tree.tag_configure("cancelled", foreground=COLORS["danger"])

    def on_train_selected(self):
        """Displays intermediate stops and seating capacity when a train is clicked."""
        selected = self.train_tree.selection()
        if not selected:
            return

        item = self.train_tree.item(selected[0])
        train_id = int(item["values"][0])
        train_no = str(item["values"][1])
        train_name = str(item["values"][2])
        train_type = str(item["values"][3])
        cap = str(item["values"][5])
        status = str(item["values"][6])

        self.selected_train_id = train_id

        # Pre-fill form
        self.t_num_entry.delete(0, "end")
        self.t_num_entry.insert(0, train_no)
        self.t_name_entry.delete(0, "end")
        self.t_name_entry.insert(0, train_name)
        self.t_type_combo.set(train_type)
        self.cap_entry.delete(0, "end")
        self.cap_entry.insert(0, cap)
        self.status_combo.set(status)

        self.id_badge.config(text=f"Selected ID: #{train_id}", fg=COLORS["secondary"])
        self.mode_lbl.config(text=f"Edit Train: {train_no} - {train_name}")
        self.update_btn.config(state="normal")

        self.stops_title.config(text=f"Train {train_no} - {train_name} ({status})")

        # Load stops
        for item in self.stops_tree.get_children():
            self.stops_tree.delete(item)

        stops = get_train_stops(train_id)
        for s in stops:
            self.stops_tree.insert(
                "",
                "end",
                values=(
                    s["stop_sequence"],
                    s["station_code"],
                    s["city"],
                    s["arrival_time"],
                    s["departure_time"],
                    s["distance_from_source_km"],
                    s["day_offset"]
                )
            )

        # Load seating capacity inventory
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        inv = get_train_schedule_inventory(train_id)
        for row in inv:
            self.inventory_tree.insert(
                "",
                "end",
                values=(
                    row["departure_date"],
                    row["seat_class"],
                    row["total_seats"],
                    row["booked_seats"],
                    row["available_seats"]
                )
            )

    def clear_form(self):
        """Resets the form to new train registration mode."""
        self.selected_train_id = None
        self.t_num_entry.delete(0, "end")
        self.t_name_entry.delete(0, "end")
        self.t_type_combo.set("Superfast")
        self.cap_entry.delete(0, "end")
        self.cap_entry.insert(0, "720")
        self.status_combo.set("ACTIVE")

        self.id_badge.config(text="Mode: New Train", fg=COLORS["primary"])
        self.mode_lbl.config(text="Register New Train Service or Select a Row Below to Modify")
        self.update_btn.config(state="disabled")

    def submit_add_train(self):
        """Invokes PL/SQL ADD_TRAIN procedure."""
        t_num = self.t_num_entry.get().strip()
        t_name = self.t_name_entry.get().strip()
        t_type = self.t_type_combo.get()
        src_sel = self.src_combo.get()
        dst_sel = self.dst_combo.get()
        cap_str = self.cap_entry.get().strip()

        if not t_num or not t_name:
            messagebox.showwarning("Missing Details", "Please enter train number and train name.")
            return

        if not src_sel or not dst_sel or src_sel == dst_sel:
            messagebox.showwarning("Invalid Terminals", "Select distinct origin and destination stations.")
            return

        try:
            capacity = int(cap_str)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Capacity", "Capacity must be a positive integer.")
            return

        src_id = self.station_map[src_sel]
        dst_id = self.station_map[dst_sel]

        ok, msg, tid = add_train(t_num, t_name, t_type, src_id, dst_id, capacity)

        if ok and tid:
            messagebox.showinfo("Success", f"Train '{t_name}' registered successfully with ID #{tid}!\nAudit entry recorded.")
            self.clear_form()
            self.refresh_trains_table()
        else:
            messagebox.showerror("Error", msg)

    def submit_update_train(self):
        """Invokes PL/SQL UPDATE_TRAIN procedure to update info and operational status."""
        if not self.selected_train_id:
            messagebox.showwarning("Select Train", "Please select a train service to update.")
            return

        t_name = self.t_name_entry.get().strip()
        t_type = self.t_type_combo.get()
        cap_str = self.cap_entry.get().strip()
        status = self.status_combo.get()

        if not t_name:
            messagebox.showwarning("Missing Name", "Train name cannot be blank.")
            return

        try:
            capacity = int(cap_str)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Capacity", "Capacity must be a positive integer.")
            return

        ok, msg = update_train(self.selected_train_id, t_name, t_type, capacity, status)
        if ok:
            messagebox.showinfo("Success", f"{msg}\nAudit log updated with status and capacity modification.")
            self.refresh_trains_table()
        else:
            messagebox.showerror("Update Error", msg)
