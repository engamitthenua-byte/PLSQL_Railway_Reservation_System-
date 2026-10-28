"""
Ticket Booking Page View for Smart Railway Reservation System.
Coordinates user input validation, passenger party entry, dynamic fare calculation,
and transaction-safe booking via Oracle PL/SQL.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from gui.theme import COLORS, FONTS, create_card
from services.passenger_service import get_all_passengers, register_passenger
from services.station_service import get_all_stations
from services.train_service import get_all_trains, search_trains
from services.reservation_service import book_ticket
from database.db_connection import execute_query, call_function
import oracledb


class BookingPage(tk.Frame):
    """Complete ticket reservation interface."""

    def __init__(self, parent, on_booking_success: Optional[Any] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.on_success = on_booking_success

        self.passengers = []
        self.passenger_map = {}
        self.stations = []
        self.station_map = {}
        self.trains = []

        self.party = []  # List of dicts: [{'name': '...', 'age': 25, 'gender': 'Male'}]
        self.current_schedule_id = None
        self.current_train_type = "Superfast"
        self.current_distance_km = 1000.0

        self.build_ui()
        self.load_reference_data()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Railway Ticket Reservation (Oracle PL/SQL Transaction)",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(side="left")

        # Main Layout: Two Columns (Left: Journey & Train Details; Right: Passengers & Payment)
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        container.pack(fill="both", expand=True, pady=(0, 20))
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # ------------------ LEFT COLUMN: JOURNEY & TRAIN ------------------
        left_outer = tk.Frame(container, bg=COLORS["border"], padx=1, pady=1)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        left_card = tk.Frame(left_outer, bg=COLORS["bg_card"], padx=16, pady=16)
        left_card.pack(fill="both", expand=True)

        tk.Label(left_card, text="1. Journey & Train Configuration", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 12))

        grid_l = tk.Frame(left_card, bg=COLORS["bg_card"])
        grid_l.pack(fill="x")
        grid_l.columnconfigure(1, weight=1)

        # Primary Passenger Selector
        tk.Label(grid_l, text="Primary Passenger:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w", pady=6)
        self.pass_combo = ttk.Combobox(grid_l, state="readonly", font=FONTS["body"])
        self.pass_combo.grid(row=0, column=1, sticky="ew", pady=6, padx=(8, 0))

        # Origin & Destination
        tk.Label(grid_l, text="Boarding Station:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w", pady=6)
        self.src_combo = ttk.Combobox(grid_l, state="readonly", font=FONTS["body"])
        self.src_combo.grid(row=1, column=1, sticky="ew", pady=6, padx=(8, 0))
        self.src_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_available_schedules())

        tk.Label(grid_l, text="Destination Station:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=6)
        self.dst_combo = ttk.Combobox(grid_l, state="readonly", font=FONTS["body"])
        self.dst_combo.grid(row=2, column=1, sticky="ew", pady=6, padx=(8, 0))
        self.dst_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_available_schedules())

        # Journey Date
        tk.Label(grid_l, text="Journey Date (YYYY-MM-DD):", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=3, column=0, sticky="w", pady=6)
        self.date_entry = ttk.Entry(grid_l, font=FONTS["body"])
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1, sticky="ew", pady=6, padx=(8, 0))

        # Train Schedule Selector
        tk.Label(grid_l, text="Select Train & Service:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=4, column=0, sticky="w", pady=6)
        self.train_combo = ttk.Combobox(grid_l, state="readonly", font=FONTS["body"])
        self.train_combo.grid(row=4, column=1, sticky="ew", pady=6, padx=(8, 0))
        self.train_combo.bind("<<ComboboxSelected>>", lambda e: self.on_train_selected())

        # Travel Class
        tk.Label(grid_l, text="Travel Class:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).grid(row=5, column=0, sticky="w", pady=6)
        self.class_combo = ttk.Combobox(grid_l, state="readonly", values=["SL - Sleeper", "3A - AC 3 Tier", "2A - AC 2 Tier", "1A - AC First Class"], font=FONTS["body"])
        self.class_combo.set("3A - AC 3 Tier")
        self.class_combo.grid(row=5, column=1, sticky="ew", pady=6, padx=(8, 0))
        self.class_combo.bind("<<ComboboxSelected>>", lambda e: self.update_fare_preview())

        # Availability & Distance Info Box
        self.info_box = tk.Label(
            left_card,
            text="Please select Boarding and Destination stations to check available train schedules.",
            font=FONTS["small_bold"],
            bg="#F1F5F9",
            fg=COLORS["text_body"],
            padx=12,
            pady=10,
            relief="groove",
            bd=1,
            justify="left",
            anchor="w"
        )
        self.info_box.pack(fill="x", pady=(14, 0))

        # Quick New Passenger Registration Section
        quick_reg_frame = tk.LabelFrame(left_card, text="Quick Register New Passenger", bg=COLORS["bg_card"], font=FONTS["small_bold"], padx=10, pady=8)
        quick_reg_frame.pack(fill="x", pady=(16, 0))

        q_grid = tk.Frame(quick_reg_frame, bg=COLORS["bg_card"])
        q_grid.pack(fill="x")
        q_grid.columnconfigure(1, weight=1)

        tk.Label(q_grid, text="Name:", font=FONTS["small"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w")
        self.q_name = ttk.Entry(q_grid, font=FONTS["small"])
        self.q_name.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(q_grid, text="Age:", font=FONTS["small"], bg=COLORS["bg_card"]).grid(row=0, column=2, sticky="w")
        self.q_age = ttk.Entry(q_grid, font=FONTS["small"], width=5)
        self.q_age.grid(row=0, column=3, sticky="w", padx=4, pady=2)

        tk.Label(q_grid, text="Phone:", font=FONTS["small"], bg=COLORS["bg_card"]).grid(row=1, column=0, sticky="w")
        self.q_phone = ttk.Entry(q_grid, font=FONTS["small"])
        self.q_phone.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        tk.Label(q_grid, text="Gender:", font=FONTS["small"], bg=COLORS["bg_card"]).grid(row=1, column=2, sticky="w")
        self.q_gender = ttk.Combobox(q_grid, values=["Male", "Female", "Other"], state="readonly", width=8, font=FONTS["small"])
        self.q_gender.set("Male")
        self.q_gender.grid(row=1, column=3, sticky="w", padx=4, pady=2)

        reg_btn = tk.Button(
            quick_reg_frame,
            text="+ Add to System",
            font=FONTS["small_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self.quick_register_passenger
        )
        reg_btn.pack(anchor="e", pady=(6, 0))

        # ------------------ RIGHT COLUMN: PASSENGERS & PAYMENT ------------------
        right_outer = tk.Frame(container, bg=COLORS["border"], padx=1, pady=1)
        right_outer.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        right_card = tk.Frame(right_outer, bg=COLORS["bg_card"], padx=16, pady=16)
        right_card.pack(fill="both", expand=True)

        tk.Label(right_card, text="2. Passenger Party & Fare Calculation", font=FONTS["h2"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 10))

        # Add Passenger input line
        add_pass_box = tk.Frame(right_card, bg="#F8FAFC", padx=10, pady=8, relief="groove", bd=1)
        add_pass_box.pack(fill="x", pady=(0, 10))

        tk.Label(add_pass_box, text="Name:", font=FONTS["small_bold"], bg="#F8FAFC").pack(side="left", padx=(0, 4))
        self.p_name_entry = ttk.Entry(add_pass_box, font=FONTS["small"], width=14)
        self.p_name_entry.pack(side="left", padx=(0, 8))

        tk.Label(add_pass_box, text="Age:", font=FONTS["small_bold"], bg="#F8FAFC").pack(side="left", padx=(0, 4))
        self.p_age_entry = ttk.Entry(add_pass_box, font=FONTS["small"], width=5)
        self.p_age_entry.pack(side="left", padx=(0, 8))

        tk.Label(add_pass_box, text="Gender:", font=FONTS["small_bold"], bg="#F8FAFC").pack(side="left", padx=(0, 4))
        self.p_gender_combo = ttk.Combobox(add_pass_box, values=["Male", "Female", "Other"], state="readonly", width=8, font=FONTS["small"])
        self.p_gender_combo.set("Male")
        self.p_gender_combo.pack(side="left", padx=(0, 8))

        add_p_btn = tk.Button(
            add_pass_box,
            text="+ Add Passenger",
            font=FONTS["small_bold"],
            bg=COLORS["secondary"],
            fg="#FFFFFF",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self.add_passenger_to_party
        )
        add_p_btn.pack(side="left")

        # Passenger Table
        cols = ("idx", "name", "age", "gender")
        self.party_tree = ttk.Treeview(right_card, columns=cols, show="headings", height=5)
        self.party_tree.heading("idx", text="#")
        self.party_tree.heading("name", text="Passenger Name")
        self.party_tree.heading("age", text="Age")
        self.party_tree.heading("gender", text="Gender")

        self.party_tree.column("idx", width=40, anchor="center")
        self.party_tree.column("name", width=180, anchor="w")
        self.party_tree.column("age", width=60, anchor="center")
        self.party_tree.column("gender", width=80, anchor="center")
        self.party_tree.pack(fill="x", pady=(0, 6))

        # Remove Passenger button
        rm_btn = tk.Button(
            right_card,
            text="Remove Selected Passenger",
            font=FONTS["small"],
            bg="#EF4444",
            fg="#FFFFFF",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.remove_selected_passenger
        )
        rm_btn.pack(anchor="e", pady=(0, 10))

        # Payment Method & Fare Summary
        pay_box = tk.Frame(right_card, bg=COLORS["bg_card"])
        pay_box.pack(fill="x", pady=6)

        tk.Label(pay_box, text="Payment Method:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 10))
        self.pay_combo = ttk.Combobox(pay_box, state="readonly", values=["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash"], font=FONTS["body"])
        self.pay_combo.set("UPI")
        self.pay_combo.pack(side="left")

        # Total Fare Card Frame
        fare_card = tk.Frame(right_card, bg="#F0FDF4", padx=14, pady=12, relief="groove", bd=1)
        fare_card.pack(fill="x", pady=(10, 15))

        f_top = tk.Frame(fare_card, bg="#F0FDF4")
        f_top.pack(fill="x")

        tk.Label(f_top, text="TOTAL CALCULATED FARE", font=("Segoe UI", 9, "bold"), bg="#F0FDF4", fg="#15803D").pack(side="left")
        self.fare_lbl = tk.Label(f_top, text="₹ 0.00", font=("Segoe UI", 20, "bold"), bg="#F0FDF4", fg="#16A34A")
        self.fare_lbl.pack(side="right")

        self.fare_breakdown_lbl = tk.Label(
            fare_card,
            text="Add passengers to calculate ticket fare.",
            font=FONTS["small"],
            bg="#F0FDF4",
            fg="#166534",
            anchor="w"
        )
        self.fare_breakdown_lbl.pack(fill="x", pady=(4, 0))

        # Confirm & Book Button
        book_btn = tk.Button(
            right_card,
            text="✓ CONFIRM & BOOK TICKET VIA PL/SQL",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["success"],
            fg="#FFFFFF",
            activebackground="#15803D",
            activeforeground="#FFFFFF",
            relief="flat",
            pady=12,
            cursor="hand2",
            command=self.execute_booking
        )
        book_btn.pack(fill="x")

    def load_reference_data(self):
        """Loads stations and registered passengers."""
        try:
            self.stations = get_all_stations()
            stn_options = []
            for s in self.stations:
                disp = f"{s['station_code']} - {s['station_name']}"
                stn_options.append(disp)
                self.station_map[disp] = s["station_id"]

            self.src_combo["values"] = stn_options
            self.dst_combo["values"] = stn_options

            # Default: MMCT -> NDLS
            mmct_opt = next((o for o in stn_options if "MMCT" in o), stn_options[1] if len(stn_options) > 1 else "")
            ndls_opt = next((o for o in stn_options if "NDLS" in o), stn_options[0] if stn_options else "")
            self.src_combo.set(mmct_opt)
            self.dst_combo.set(ndls_opt)

            self.refresh_passengers_dropdown()
            self.refresh_available_schedules()

        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to load reference data: {e}")

    def refresh_passengers_dropdown(self, select_id: Optional[int] = None):
        """Refreshes the primary passenger list."""
        self.passengers = get_all_passengers()
        pass_options = []
        for p in self.passengers:
            disp = f"#{p['passenger_id']} - {p['full_name']} (Phone: {p['phone_number']})"
            pass_options.append(disp)
            self.passenger_map[disp] = p["passenger_id"]

        self.pass_combo["values"] = pass_options
        if pass_options:
            if select_id:
                target_opt = next((o for o, pid in self.passenger_map.items() if pid == select_id), pass_options[0])
                self.pass_combo.set(target_opt)
            else:
                self.pass_combo.set(pass_options[0])

    def refresh_available_schedules(self):
        """Fetches active train schedules connecting the selected source and destination."""
        src_sel = self.src_combo.get()
        dst_sel = self.dst_combo.get()

        if not src_sel or not dst_sel or src_sel == dst_sel:
            self.train_combo["values"] = []
            self.train_combo.set("")
            return

        src_id = self.station_map[src_sel]
        dst_id = self.station_map[dst_sel]
        date_str = self.date_entry.get().strip()

        try:
            results, _ = search_trains(src_id, dst_id, journey_date=date_str if date_str else None)
            options = []
            self.schedule_results = results

            for r in results:
                avail_sl = r.get("seat_availability", {}).get("SL", 0)
                disp = f"{r['train_number']} - {r['train_name']} (Dep: {r['departure_time']}, {r['segment_distance_km']} km) [Sched #{r['schedule_id']}]"
                options.append(disp)

            self.train_combo["values"] = options
            if options:
                self.train_combo.set(options[0])
                self.on_train_selected()
            else:
                self.train_combo.set("No scheduled trains found for this route")
                self.info_box.config(
                    text="No direct trains available connecting these stations on this date.",
                    fg=COLORS["danger"]
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to check train schedules: {e}")

    def on_train_selected(self):
        """Updates internal schedule ID and distance based on selected train."""
        sel = self.train_combo.get()
        matched = next((r for r in getattr(self, "schedule_results", []) if f"Sched #{r['schedule_id']}" in sel), None)
        if matched:
            self.current_schedule_id = matched["schedule_id"]
            self.current_train_type = matched["train_type"]
            self.current_distance_km = float(matched["segment_distance_km"])

            avail = matched.get("seat_availability", {})
            info_text = (
                f"Train: {matched['train_number']} {matched['train_name']} ({matched['train_type']})\n"
                f"Distance: {self.current_distance_km} km | Dep: {matched['departure_time']} ➔ Arr: {matched['dest_arrival_time']}\n"
                f"Available Seats: SL={avail.get('SL',0)} | 3A={avail.get('3A',0)} | 2A={avail.get('2A',0)} | 1A={avail.get('1A',0)}"
            )
            self.info_box.config(text=info_text, fg=COLORS["primary"])
            self.update_fare_preview()

    def update_fare_preview(self):
        """Calls PL/SQL CALCULATE_FARE to show live pricing."""
        party_size = len(self.party)
        class_code = self.class_combo.get().split(" - ")[0].strip()

        if party_size == 0:
            self.fare_lbl.config(text="₹ 0.00")
            self.fare_breakdown_lbl.config(text="Add passengers to calculate ticket fare.")
            return

        fare, _ = call_function(
            "CALCULATE_FARE",
            oracledb.NUMBER,
            [self.current_distance_km, self.current_train_type, class_code, party_size]
        )
        total_fare = float(fare or 0.0)
        per_person = total_fare / party_size if party_size > 0 else 0.0

        self.fare_lbl.config(text=f"₹ {total_fare:,.2f}")
        self.fare_breakdown_lbl.config(
            text=f"{party_size} Passenger(s) in {class_code} | ~ ₹ {per_person:,.2f} per ticket | Distance: {self.current_distance_km} km"
        )

    def add_passenger_to_party(self):
        """Adds a passenger to the reservation party."""
        name = self.p_name_entry.get().strip()
        age_str = self.p_age_entry.get().strip()
        gender = self.p_gender_combo.get()

        if not name:
            messagebox.showwarning("Missing Information", "Please enter the passenger's name.")
            return

        try:
            age = int(age_str)
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Age", "Please enter a valid age between 1 and 120.")
            return

        self.party.append({"name": name, "age": age, "gender": gender})
        self.p_name_entry.delete(0, "end")
        self.p_age_entry.delete(0, "end")

        self._refresh_party_tree()
        self.update_fare_preview()

    def remove_selected_passenger(self):
        """Removes the selected passenger from the reservation party."""
        selected = self.party_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a passenger row to remove.")
            return

        idx = int(self.party_tree.item(selected[0])["values"][0]) - 1
        if 0 <= idx < len(self.party):
            self.party.pop(idx)
            self._refresh_party_tree()
            self.update_fare_preview()

    def _refresh_party_tree(self):
        for item in self.party_tree.get_children():
            self.party_tree.delete(item)

        for i, p in enumerate(self.party, 1):
            self.party_tree.insert("", "end", values=(i, p["name"], p["age"], p["gender"]))

    def quick_register_passenger(self):
        """Quick registers a new passenger in PASSENGERS table via PL/SQL."""
        name = self.q_name.get().strip()
        age_str = self.q_age.get().strip()
        phone = self.q_phone.get().strip()
        gender = self.q_gender.get()

        if not name or not age_str or not phone:
            messagebox.showwarning("Missing Details", "Please fill name, age, and phone number.")
            return

        try:
            age = int(age_str)
        except ValueError:
            messagebox.showwarning("Invalid Age", "Age must be an integer.")
            return

        email = f"{name.lower().replace(' ', '.')}_{phone[-4:]}@railway.ac.in"
        ok, msg, pid = register_passenger(name, age, gender, phone, email)

        if ok and pid:
            messagebox.showinfo("Success", f"Passenger registered successfully with ID #{pid}!")
            self.refresh_passengers_dropdown(select_id=pid)
            # Pre-add to party
            self.party.append({"name": name, "age": age, "gender": gender})
            self._refresh_party_tree()
            self.update_fare_preview()
            self.q_name.delete(0, "end")
            self.q_age.delete(0, "end")
            self.q_phone.delete(0, "end")
        else:
            messagebox.showerror("Registration Error", msg)

    def prefill_train(self, train_data: Dict[str, Any]):
        """Prefills form fields when navigating from Train Search page."""
        # Find matching source and destination
        for opt, sid in self.station_map.items():
            if sid == train_data.get("from_station_id") or train_data.get("from_code", "") in opt:
                self.src_combo.set(opt)
            if sid == train_data.get("to_station_id") or train_data.get("to_code", "") in opt:
                self.dst_combo.set(opt)

        if train_data.get("departure_date"):
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, train_data["departure_date"])

        self.refresh_available_schedules()

    def execute_booking(self):
        """Executes transaction-safe ticket reservation via Oracle PL/SQL BOOK_TICKET."""
        pass_sel = self.pass_combo.get()
        if not pass_sel:
            messagebox.showwarning("Missing Booker", "Please select or register a primary passenger.")
            return
        primary_pass_id = self.passenger_map[pass_sel]

        if not self.current_schedule_id:
            messagebox.showwarning("Schedule Missing", "Please select a valid train schedule.")
            return

        if len(self.party) == 0:
            messagebox.showwarning("No Passengers", "Please add at least one passenger to the party.")
            return

        src_id = self.station_map[self.src_combo.get()]
        dst_id = self.station_map[self.dst_combo.get()]
        journey_date_str = self.date_entry.get().strip()
        seat_class = self.class_combo.get().split(" - ")[0].strip()
        payment_method = self.pay_combo.get()

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Reservation",
            f"Are you sure you want to confirm this booking?\n\n"
            f"• Route: {self.src_combo.get().split(' - ')[0]} ➔ {self.dst_combo.get().split(' - ')[0]}\n"
            f"• Journey Date: {journey_date_str}\n"
            f"• Travel Class: {seat_class}\n"
            f"• Passengers: {len(self.party)}\n"
            f"• Fare: {self.fare_lbl.cget('text')}\n"
            f"• Payment: {payment_method}\n\n"
            f"Click Yes to execute the Oracle PL/SQL booking transaction."
        )
        if not confirm:
            return

        # Extract calculated fare value
        fare_text = self.fare_lbl.cget("text").replace("₹", "").replace(",", "").strip()
        try:
            total_fare = float(fare_text)
        except ValueError:
            total_fare = 0.0

        # Execute booking via service
        ok, pnr, res_id, msg = book_ticket(
            passenger_id=primary_pass_id,
            schedule_id=self.current_schedule_id,
            from_station_id=src_id,
            to_station_id=dst_id,
            journey_date_str=journey_date_str,
            seat_class=seat_class,
            passenger_list=self.party,
            payment_method=payment_method
        )

        if ok:
            # Extract detailed booking parameters for confirmation screen
            train_display = self.train_combo.get().split(" [Sched")[0]
            train_num = train_display.split(" - ")[0] if " - " in train_display else ""
            train_name = train_display.split(" - ")[1].split(" (")[0] if " - " in train_display else train_display
            src_display = self.src_combo.get()
            dst_display = self.dst_combo.get()
            primary_name = pass_sel.split(" - ")[1].split(" (")[0] if " - " in pass_sel else pass_sel

            confirmation_data = {
                "pnr_number": pnr,
                "reservation_id": res_id,
                "passenger_name": primary_name,
                "party": list(self.party),
                "train_number": train_num,
                "train_name": train_name,
                "source_station": src_display,
                "destination_station": dst_display,
                "journey_date": journey_date_str,
                "passenger_count": len(self.party),
                "seat_class": seat_class,
                "total_fare": total_fare,
                "booking_status": "CONFIRMED",
                "payment_method": payment_method
            }

            # Reset party and refresh schedules
            self.party = []
            self._refresh_party_tree()
            self.update_fare_preview()
            self.refresh_available_schedules()

            # Display rich booking confirmation dialog with Copy PNR functionality
            BookingConfirmationDialog(self, confirmation_data)

            if self.on_success:
                self.on_success(pnr)
        else:
            messagebox.showerror("Booking Failed", f"Booking could not be completed:\n\n{msg}")


class BookingConfirmationDialog(tk.Toplevel):
    """
    Modern modal dialog displayed upon successful ticket booking.
    Presents all booking details and provides a 'Copy PNR' button with clipboard handling.
    """

    def __init__(self, parent, booking_info: Dict[str, Any]):
        super().__init__(parent)
        self.title("Booking Confirmation - Ticket Reserved")
        self.geometry("640x560")
        self.minsize(600, 520)
        self.configure(bg=COLORS["bg_main"])
        self.transient(parent)
        self.grab_set()

        self.booking_info = booking_info
        self.pnr = str(booking_info.get("pnr_number", "")).strip()
        self.copy_status_lbl = None

        self._build_ui()

    def _build_ui(self):
        # Header Banner
        hdr = tk.Frame(self, bg=COLORS["success"], padx=18, pady=12)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="🎉 Booking Confirmed Successfully!",
            font=("Segoe UI", 13, "bold"),
            bg=COLORS["success"],
            fg="#FFFFFF"
        ).pack(side="left")

        tk.Label(
            hdr,
            text="STATUS: CONFIRMED",
            font=("Segoe UI", 9, "bold"),
            bg="#15803D",
            fg="#FFFFFF",
            padx=8,
            pady=3
        ).pack(side="right")

        # Main Body
        body = tk.Frame(self, bg=COLORS["bg_main"], padx=18, pady=14)
        body.pack(fill="both", expand=True)

        # 1. PNR Box with Copy PNR Button
        pnr_card_outer = tk.Frame(body, bg="#86EFAC", padx=1, pady=1)
        pnr_card_outer.pack(fill="x", pady=(0, 14))

        pnr_card = tk.Frame(pnr_card_outer, bg="#F0FDF4", padx=14, pady=12)
        pnr_card.pack(fill="both", expand=True)

        pnr_top = tk.Frame(pnr_card, bg="#F0FDF4")
        pnr_top.pack(fill="x")

        tk.Label(
            pnr_top,
            text="RESERVATION PNR NUMBER",
            font=("Segoe UI", 9, "bold"),
            bg="#F0FDF4",
            fg="#166534"
        ).pack(side="left")

        # PNR Row (Selectable Entry + Copy PNR Button)
        pnr_row = tk.Frame(pnr_card, bg="#F0FDF4")
        pnr_row.pack(fill="x", pady=(6, 2))

        # Selectable Entry for PNR so user can also select/copy manually
        pnr_entry = tk.Entry(
            pnr_row,
            font=("Consolas", 16, "bold"),
            fg="#15803D",
            bg="#FFFFFF",
            relief="solid",
            bd=1,
            width=18,
            justify="center"
        )
        pnr_entry.insert(0, self.pnr)
        pnr_entry.config(state="readonly")
        pnr_entry.pack(side="left", padx=(0, 10))

        # Copy PNR Button
        copy_btn = tk.Button(
            pnr_row,
            text="📋 Copy PNR",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_light"],
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.copy_pnr_to_clipboard
        )
        copy_btn.pack(side="left")

        # Copy Feedback Label
        self.copy_status_lbl = tk.Label(
            pnr_card,
            text="Click 'Copy PNR' to copy the number to your clipboard for cancellation or inquiries.",
            font=("Segoe UI", 8),
            bg="#F0FDF4",
            fg="#166534",
            anchor="w"
        )
        self.copy_status_lbl.pack(fill="x", pady=(4, 0))

        # 2. Complete Booking Details Card
        info_outer = tk.Frame(body, bg=COLORS["border"], padx=1, pady=1)
        info_outer.pack(fill="both", expand=True, pady=(0, 14))

        info_card = tk.Frame(info_outer, bg=COLORS["bg_card"], padx=14, pady=12)
        info_card.pack(fill="both", expand=True)

        tk.Label(
            info_card,
            text="Reservation Summary Details",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 8))

        grid = tk.Frame(info_card, bg=COLORS["bg_card"])
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        details = [
            ("PNR Number:", self.pnr),
            ("Booking Status:", self.booking_info.get("booking_status", "CONFIRMED")),
            ("Primary Passenger:", self.booking_info.get("passenger_name", "")),
            ("Travel Class:", self.booking_info.get("seat_class", "")),
            ("Train Details:", f"{self.booking_info.get('train_number', '')} - {self.booking_info.get('train_name', '')}"),
            ("Number of Passengers:", f"{self.booking_info.get('passenger_count', '')} passenger(s)"),
            ("Source Station:", self.booking_info.get("source_station", "")),
            ("Destination Station:", self.booking_info.get("destination_station", "")),
            ("Journey Date:", self.booking_info.get("journey_date", "")),
            ("Total Fare Paid:", f"₹ {float(self.booking_info.get('total_fare', 0)):,.2f}"),
        ]

        for i, (k, v) in enumerate(details):
            r = i // 2
            c = (i % 2) * 2
            tk.Label(grid, text=k, font=FONTS["small_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=r, column=c, sticky="w", pady=4, padx=(0, 4))
            val_fg = COLORS["success"] if "CONFIRMED" in str(v) else COLORS["text_dark"]
            tk.Label(grid, text=str(v), font=FONTS["body_bold" if "Fare" in k or "Status" in k or "PNR" in k else "body"], bg=COLORS["bg_card"], fg=val_fg).grid(row=r, column=c+1, sticky="w", pady=4, padx=(0, 14))

        # Bottom Action Bar
        btn_bar = tk.Frame(body, bg=COLORS["bg_main"])
        btn_bar.pack(fill="x")

        close_btn = tk.Button(
            btn_bar,
            text="✓ Done",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        close_btn.pack(side="right")

    def copy_pnr_to_clipboard(self):
        """
        Copies the complete PNR number to the system clipboard.
        Ensures the copied value contains only the PNR number without extra spaces or labels.
        """
        clean_pnr = self.pnr.strip()
        try:
            self.clipboard_clear()
            self.clipboard_append(clean_pnr)
            self.update()  # Keeps clipboard on Windows even if window closes
            self.copy_status_lbl.config(
                text="✓ PNR copied to clipboard successfully!",
                font=("Segoe UI", 9, "bold"),
                fg="#16A34A"
            )
        except Exception as e:
            self.copy_status_lbl.config(
                text=f"Clipboard error: {e}",
                font=("Segoe UI", 8),
                fg="#DC2626"
            )

