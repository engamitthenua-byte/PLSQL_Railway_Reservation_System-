"""
Reservations History Page View for Smart Railway Reservation System.
Lists, filters, and inspects all ticket bookings from Oracle Database.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

from gui.theme import COLORS, FONTS, create_card
from services.reservation_service import get_all_reservations, get_reservation_by_pnr


class ReservationsPage(tk.Frame):
    """View and filter all system reservations."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.all_records = []
        self.search_entry = None
        self.status_combo = None
        self.tree = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Reservation Records & Master Inquiries",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(side="left")

        refresh_btn = tk.Button(
            header,
            text="↻ Refresh Records",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            relief="flat",
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.load_data
        )
        refresh_btn.pack(side="right")

        # Filter Control Bar
        filter_card_outer = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        filter_card_outer.pack(fill="x", padx=20, pady=(0, 15))

        filter_card = tk.Frame(filter_card_outer, bg=COLORS["bg_card"], padx=16, pady=12)
        filter_card.pack(fill="both", expand=True)

        f_box = tk.Frame(filter_card, bg=COLORS["bg_card"])
        f_box.pack(fill="x")

        tk.Label(f_box, text="Filter / Search:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))
        self.search_entry = ttk.Entry(f_box, font=FONTS["body"], width=28)
        self.search_entry.pack(side="left", padx=(0, 16))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        tk.Label(f_box, text="Status Filter:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 8))
        self.status_combo = ttk.Combobox(f_box, state="readonly", values=["All Statuses", "CONFIRMED", "CANCELLED"], font=FONTS["body"], width=14)
        self.status_combo.set("All Statuses")
        self.status_combo.pack(side="left", padx=(0, 16))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        inspect_btn = tk.Button(
            f_box,
            text="👁 View Full Details",
            font=FONTS["body_bold"],
            bg=COLORS["secondary"],
            fg="#FFFFFF",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.inspect_selected_booking
        )
        inspect_btn.pack(side="right")

        # Treeview Table
        table_outer = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        table_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        table_card = tk.Frame(table_outer, bg=COLORS["bg_card"], padx=14, pady=14)
        table_card.pack(fill="both", expand=True)

        cols = ("pnr", "passenger", "phone", "train", "route", "date", "class", "pax", "fare", "status", "booked_at")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings", height=12)

        self.tree.heading("pnr", text="PNR")
        self.tree.heading("passenger", text="Passenger Name")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("train", text="Train")
        self.tree.heading("route", text="Route")
        self.tree.heading("date", text="Journey Date")
        self.tree.heading("class", text="Class")
        self.tree.heading("pax", text="Pax")
        self.tree.heading("fare", text="Total Fare")
        self.tree.heading("status", text="Status")
        self.tree.heading("booked_at", text="Booking Timestamp")

        self.tree.column("pnr", width=110, anchor="center")
        self.tree.column("passenger", width=160, anchor="w")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("train", width=80, anchor="center")
        self.tree.column("route", width=110, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("class", width=60, anchor="center")
        self.tree.column("pax", width=50, anchor="center")
        self.tree.column("fare", width=95, anchor="e")
        self.tree.column("status", width=95, anchor="center")
        self.tree.column("booked_at", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.inspect_selected_booking())

    def load_data(self):
        """Loads all reservations from Oracle Database."""
        try:
            self.all_records = get_all_reservations(limit=200)
            self.apply_filters()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reservations:\n{e}")

    def apply_filters(self):
        """Filters the treeview based on user search keyword and status selection."""
        kw = self.search_entry.get().strip().lower()
        st_filter = self.status_combo.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in self.all_records:
            status = r["booking_status"]
            if st_filter != "All Statuses" and status != st_filter:
                continue

            # Check keyword match
            match = (
                not kw or
                kw in r["pnr_number"].lower() or
                kw in r["passenger_name"].lower() or
                kw in str(r["train_number"]).lower() or
                kw in r["phone_number"].lower()
            )
            if not match:
                continue

            tag = status.lower()
            route_str = f"{r['from_code']} ➔ {r['to_code']}"
            self.tree.insert(
                "",
                "end",
                values=(
                    r["pnr_number"],
                    r["passenger_name"],
                    r["phone_number"],
                    r["train_number"],
                    route_str,
                    r["journey_date"],
                    r["seat_class"],
                    r["passenger_count"],
                    f"₹ {float(r['total_fare']):.2f}",
                    r["booking_status"],
                    r["booking_time"],
                ),
                tags=(tag,)
            )

        self.tree.tag_configure("confirmed", foreground=COLORS["success"])
        self.tree.tag_configure("cancelled", foreground=COLORS["danger"])

    def inspect_selected_booking(self):
        """Opens a modal popup with full reservation and passenger details."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Record", "Please select a reservation record to inspect.")
            return

        pnr = self.tree.item(selected[0])["values"][0]
        res, passengers, msg = get_reservation_by_pnr(pnr)
        if not res:
            messagebox.showerror("Error", msg or "Could not retrieve details.")
            return

        # Create TopLevel Modal Dialog
        dlg = tk.Toplevel(self)
        dlg.title(f"Reservation Details - PNR: {pnr}")
        dlg.geometry("640x520")
        dlg.configure(bg=COLORS["bg_main"])
        dlg.transient(self)
        dlg.grab_set()

        hdr = tk.Frame(dlg, bg=COLORS["primary"], padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"PNR #{pnr}", font=("Segoe UI", 14, "bold"), bg=COLORS["primary"], fg="#FFFFFF").pack(side="left")
        st_color = COLORS["success"] if res["booking_status"] == "CONFIRMED" else COLORS["danger"]
        tk.Label(hdr, text=res["booking_status"], font=("Segoe UI", 12, "bold"), bg=COLORS["primary"], fg=st_color).pack(side="right")

        body = tk.Frame(dlg, bg=COLORS["bg_main"], padx=16, pady=14)
        body.pack(fill="both", expand=True)

        info_text = (
            f"Train Service   : {res['train_number']} - {res['train_name']} ({res['train_type']})\n"
            f"Route           : {res['from_code']} ({res['from_name']}) ➔ {res['to_code']} ({res['to_name']})\n"
            f"Journey Date    : {str(res['journey_date'])[:10]} | Booking Class: {res['seat_class']}\n"
            f"Booked By       : {res['primary_passenger']} (Phone: {res['phone_number']}, Email: {res['email']})\n"
            f"Total Fare      : ₹ {float(res['total_fare']):.2f} | Passenger Count: {res['passenger_count']}\n"
            f"Booked At       : {res['booking_time']}\n"
        )
        if res.get("refund_amount"):
            info_text += f"\nCancellation Details:\nRefund: ₹ {float(res['refund_amount']):.2f} | Fee: ₹ {float(res['cancellation_charge']):.2f} | Cancelled At: {res.get('cancellation_time')}\n"

        tk.Label(body, text=info_text, font=FONTS["mono"], bg=COLORS["bg_card"], justify="left", padx=12, pady=10, relief="groove", bd=1).pack(fill="x", pady=(0, 10))

        tk.Label(body, text="Passengers in this Reservation:", font=FONTS["body_bold"], bg=COLORS["bg_main"]).pack(anchor="w", pady=(4, 4))

        # Passengers Table in dialog
        d_cols = ("num", "name", "age", "gender", "seat")
        d_tree = ttk.Treeview(body, columns=d_cols, show="headings", height=5)
        d_tree.heading("num", text="#")
        d_tree.heading("name", text="Passenger Name")
        d_tree.heading("age", text="Age")
        d_tree.heading("gender", text="Gender")
        d_tree.heading("seat", text="Seat Assigned")

        d_tree.column("num", width=40, anchor="center")
        d_tree.column("name", width=180, anchor="w")
        d_tree.column("age", width=60, anchor="center")
        d_tree.column("gender", width=80, anchor="center")
        d_tree.column("seat", width=100, anchor="center")
        d_tree.pack(fill="both", expand=True, pady=(0, 12))

        for idx, p in enumerate(passengers, 1):
            d_tree.insert("", "end", values=(idx, p["passenger_name"], p["age"], p["gender"], p["seat_number"]))

        close_btn = tk.Button(body, text="Close", font=FONTS["body_bold"], bg=COLORS["primary"], fg="#FFFFFF", relief="flat", padx=16, pady=6, cursor="hand2", command=dlg.destroy)
        close_btn.pack(anchor="e")
