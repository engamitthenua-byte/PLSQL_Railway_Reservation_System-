"""
Ticket Cancellation Page View for Smart Railway Reservation System.
Searches reservations by PNR with autocomplete dropdown recommendations,
calculates cancellation charges & refund amounts, and executes atomic cancellation via PL/SQL.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from gui.theme import COLORS, FONTS, create_card
from services.reservation_service import get_reservation_by_pnr, cancel_ticket, get_suggested_pnrs


class CancellationPage(tk.Frame):
    """Ticket cancellation and refund processing interface with PNR recommendations."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.current_res = None
        self.current_pnr = None
        self.all_active_pnrs: List[str] = []

        self.pnr_combo = None
        self.refresh_btn = None
        self.search_btn = None
        self.details_text = None
        self.pass_tree = None
        self.orig_fare_lbl = None
        self.charge_lbl = None
        self.refund_lbl = None
        self.status_note_lbl = None
        self.reason_entry = None
        self.cancel_btn = None
        self.pnr_status_lbl = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Ticket Cancellation & Refund Management",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(side="left")

        # Top PNR Search Card
        search_card_outer = tk.Frame(self, bg=COLORS["border"], padx=1, pady=1)
        search_card_outer.pack(fill="x", padx=20, pady=(0, 15))

        search_card = tk.Frame(search_card_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        search_card.pack(fill="both", expand=True)

        tk.Label(
            search_card,
            text="Search & Select Reservation to Cancel",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 8))

        input_box = tk.Frame(search_card, bg=COLORS["bg_card"])
        input_box.pack(fill="x")

        # Label: Enter or Select PNR Number
        tk.Label(
            input_box,
            text="Enter or Select PNR Number:",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(side="left", padx=(0, 8))

        # PNR Combobox with autocomplete & suggestions
        self.pnr_combo = ttk.Combobox(input_box, font=FONTS["body"], width=24)
        self.pnr_combo.pack(side="left", padx=(0, 6))
        self.pnr_combo.bind("<KeyRelease>", self.on_pnr_key_release)
        self.pnr_combo.bind("<<ComboboxSelected>>", lambda e: self.lookup_pnr())
        self.pnr_combo.bind("<Return>", lambda e: self.lookup_pnr())

        # Refresh PNR Suggestions Button
        self.refresh_btn = tk.Button(
            input_box,
            text="↻ Refresh List",
            font=FONTS["small_bold"],
            bg="#E2E8F0",
            fg=COLORS["text_dark"],
            activebackground="#CBD5E1",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.refresh_pnr_list
        )
        self.refresh_btn.pack(side="left", padx=(0, 12))

        # Search Ticket Button
        self.search_btn = tk.Button(
            input_box,
            text="🔍 Search Ticket",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_light"],
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=5,
            cursor="hand2",
            command=self.lookup_pnr
        )
        self.search_btn.pack(side="left")

        # Hint & Count Label
        self.pnr_status_lbl = tk.Label(
            search_card,
            text="Loading active reservations...",
            font=FONTS["small"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            anchor="w"
        )
        self.pnr_status_lbl.pack(fill="x", pady=(6, 0))

        # Main Content: Two Columns (Left: Booking & Passenger Info; Right: Charges & Refund Action)
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        container.pack(fill="both", expand=True, pady=(0, 20))
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)

        # ------------------ LEFT COLUMN: RESERVATION DETAILS ------------------
        left_outer = tk.Frame(container, bg=COLORS["border"], padx=1, pady=1)
        left_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        left_card = tk.Frame(left_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        left_card.pack(fill="both", expand=True)

        tk.Label(
            left_card,
            text="Reservation & Passenger Details",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 8))

        # Booking Information Text Display
        self.details_text = tk.Text(
            left_card,
            height=7,
            bg="#F8FAFC",
            fg=COLORS["text_dark"],
            font=FONTS["mono"],
            relief="flat",
            padx=10,
            pady=8,
            wrap="word"
        )
        self.details_text.pack(fill="x", pady=(0, 10))
        self.details_text.insert(
            "1.0",
            "Select or enter a PNR above and click 'Search Ticket' to display reservation information."
        )
        self.details_text.config(state="disabled")

        tk.Label(
            left_card,
            text="Passenger Party Details:",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 4))

        # Passenger tree
        cols = ("id", "name", "age", "gender", "seat")
        self.pass_tree = ttk.Treeview(left_card, columns=cols, show="headings", height=5)
        self.pass_tree.heading("id", text="#")
        self.pass_tree.heading("name", text="Passenger Name")
        self.pass_tree.heading("age", text="Age")
        self.pass_tree.heading("gender", text="Gender")
        self.pass_tree.heading("seat", text="Seat Assigned")

        self.pass_tree.column("id", width=40, anchor="center")
        self.pass_tree.column("name", width=180, anchor="w")
        self.pass_tree.column("age", width=60, anchor="center")
        self.pass_tree.column("gender", width=80, anchor="center")
        self.pass_tree.column("seat", width=100, anchor="center")
        self.pass_tree.pack(fill="both", expand=True)

        # ------------------ RIGHT COLUMN: CANCELLATION SUMMARY ------------------
        right_outer = tk.Frame(container, bg=COLORS["border"], padx=1, pady=1)
        right_outer.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        right_card = tk.Frame(right_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        right_card.pack(fill="both", expand=True)

        tk.Label(
            right_card,
            text="Cancellation Summary & Refund",
            font=FONTS["h3"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w", pady=(0, 12))

        # Financial Breakdown Box
        fin_card = tk.Frame(right_card, bg="#FEF2F2", padx=14, pady=12, relief="groove", bd=1)
        fin_card.pack(fill="x", pady=(0, 15))

        # Original Fare
        row1 = tk.Frame(fin_card, bg="#FEF2F2")
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="Total Ticket Fare:", font=FONTS["body_bold"], bg="#FEF2F2", fg=COLORS["text_body"]).pack(side="left")
        self.orig_fare_lbl = tk.Label(row1, text="₹ 0.00", font=FONTS["body_bold"], bg="#FEF2F2", fg=COLORS["text_dark"])
        self.orig_fare_lbl.pack(side="right")

        # Cancellation Fee (20%)
        row2 = tk.Frame(fin_card, bg="#FEF2F2")
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="Cancellation Fee (20%):", font=FONTS["body"], bg="#FEF2F2", fg=COLORS["danger"]).pack(side="left")
        self.charge_lbl = tk.Label(row2, text="₹ 0.00", font=FONTS["body_bold"], bg="#FEF2F2", fg=COLORS["danger"])
        self.charge_lbl.pack(side="right")

        # Divider
        tk.Frame(fin_card, height=1, bg="#FCA5A5").pack(fill="x", pady=6)

        # Refund Amount
        row3 = tk.Frame(fin_card, bg="#FEF2F2")
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="ESTIMATED REFUND:", font=("Segoe UI", 11, "bold"), bg="#FEF2F2", fg="#991B1B").pack(side="left")
        self.refund_lbl = tk.Label(row3, text="₹ 0.00", font=("Segoe UI", 16, "bold"), bg="#FEF2F2", fg=COLORS["success"])
        self.refund_lbl.pack(side="right")

        # Cancellation Reason input
        tk.Label(right_card, text="Reason for Cancellation:", font=FONTS["body_bold"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(10, 4))
        self.reason_entry = ttk.Entry(right_card, font=FONTS["body"])
        self.reason_entry.insert(0, "Change of travel plans")
        self.reason_entry.pack(fill="x", pady=(0, 15))

        # Status note
        self.status_note_lbl = tk.Label(
            right_card,
            text="Search an active reservation to view cancellation charges and refund eligibility.",
            font=FONTS["small"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
            wraplength=280,
            justify="left"
        )
        self.status_note_lbl.pack(fill="x", pady=(0, 15))

        # Cancel Ticket Button
        self.cancel_btn = tk.Button(
            right_card,
            text="⚠ CANCEL TICKET",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["danger"],
            fg="#FFFFFF",
            activebackground="#B91C1C",
            activeforeground="#FFFFFF",
            relief="flat",
            pady=10,
            cursor="hand2",
            state="disabled",
            command=self.confirm_cancellation
        )
        self.cancel_btn.pack(fill="x")

    def load_data(self):
        """Loads or reloads active PNR suggestions from Oracle Database."""
        self.refresh_pnr_list(preserve_selection=True)

    def refresh_pnr_list(self, preserve_selection: bool = True):
        """
        Retrieves active (CONFIRMED) reservation PNRs from Oracle.
        Excludes already cancelled bookings from the default recommendations.
        """
        current_val = self.pnr_combo.get().strip().upper() if self.pnr_combo else ""
        try:
            pnrs = get_suggested_pnrs(status="CONFIRMED", limit=100)
            self.all_active_pnrs = pnrs
            self.pnr_combo["values"] = self.all_active_pnrs

            count = len(pnrs)
            if count > 0:
                self.pnr_status_lbl.config(
                    text=f"✓ Loaded {count} active confirmed PNR(s) from Oracle. Type to filter or select from dropdown.",
                    fg=COLORS["success"]
                )
                if not current_val:
                    # Suggest the newest booking by default
                    self.pnr_combo.set(pnrs[0])
                elif current_val in pnrs:
                    self.pnr_combo.set(current_val)
            else:
                self.pnr_status_lbl.config(
                    text="No active confirmed reservations currently found in Oracle Database.",
                    fg=COLORS["text_muted"]
                )
        except Exception as e:
            self.pnr_status_lbl.config(
                text=f"Failed to load PNR suggestions: {e}",
                fg=COLORS["danger"]
            )

    def on_pnr_key_release(self, event):
        """
        Filters the combobox dropdown suggestions as the user types.
        Allows flexible autocomplete without overriding manual entry.
        """
        # Ignore navigation keys
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"):
            return

        typed = self.pnr_combo.get().strip().upper()
        if not typed:
            self.pnr_combo["values"] = self.all_active_pnrs
            return

        filtered = [p for p in self.all_active_pnrs if typed in p]
        self.pnr_combo["values"] = filtered

        # If user entered something completely custom, keep values accessible
        if not filtered:
            self.pnr_status_lbl.config(
                text=f"No active PNRs match '{typed}'. Press 'Search Ticket' to query Oracle directly.",
                fg=COLORS["text_muted"]
            )
        else:
            self.pnr_status_lbl.config(
                text=f"Found {len(filtered)} matching active reservation(s).",
                fg=COLORS["primary"]
            )

    def lookup_pnr(self):
        """Searches Oracle DB via PL/SQL GET_RESERVATION_DETAILS."""
        pnr = self.pnr_combo.get().strip().upper()
        if not pnr:
            messagebox.showwarning("Missing PNR", "Please enter or select a PNR number to search.")
            return

        res, passengers, msg = get_reservation_by_pnr(pnr)

        if not res:
            messagebox.showerror("Reservation Not Found", msg or f"No reservation found in Oracle Database for PNR: {pnr}")
            self.current_res = None
            self.cancel_btn.config(state="disabled")
            self.orig_fare_lbl.config(text="₹ 0.00")
            self.charge_lbl.config(text="₹ 0.00")
            self.refund_lbl.config(text="₹ 0.00")
            self.details_text.config(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("1.0", f"✗ No reservation records found matching PNR: {pnr}")
            self.details_text.config(state="disabled")
            for item in self.pass_tree.get_children():
                self.pass_tree.delete(item)
            return

        self.current_res = res
        self.current_pnr = pnr

        # Render Details Text with all required fields
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")

        journey_dt = str(res["journey_date"])[:10]
        status = res["booking_status"]
        pass_list_names = ", ".join([p["passenger_name"] for p in passengers]) if passengers else res["primary_passenger"]

        info_str = (
            f"• PNR Number       : {res['pnr_number']}\n"
            f"• Primary Passenger: {res['primary_passenger']} (Phone: {res['phone_number']})\n"
            f"• Passenger List   : {pass_list_names}\n"
            f"• Train Details    : {res['train_number']} - {res['train_name']} ({res['train_type']})\n"
            f"• Origin / Dest    : {res['from_code']} ({res['from_name']}) ➔ {res['to_code']} ({res['to_name']})\n"
            f"• Journey Date     : {journey_dt} | Class: {res['seat_class']}\n"
            f"• Passengers Count : {res['passenger_count']} passenger(s)\n"
            f"• Total Fare Paid  : ₹ {float(res['total_fare']):,.2f}\n"
            f"• Booking Status   : {status}"
        )
        self.details_text.insert("1.0", info_str)
        self.details_text.config(state="disabled")

        # Populate Passengers Table
        for item in self.pass_tree.get_children():
            self.pass_tree.delete(item)

        for idx, p in enumerate(passengers, 1):
            self.pass_tree.insert(
                "",
                "end",
                values=(idx, p["passenger_name"], p["age"], p["gender"], p["seat_number"])
            )

        # Calculate charges
        total_fare = float(res["total_fare"])

        if status == "CANCELLED":
            self.orig_fare_lbl.config(text=f"₹ {total_fare:,.2f}")
            self.charge_lbl.config(text=f"₹ {float(res.get('cancellation_charge') or 0.0):,.2f}")
            self.refund_lbl.config(text=f"₹ {float(res.get('refund_amount') or 0.0):,.2f}")
            self.status_note_lbl.config(
                text=f"⚠ This reservation is ALREADY CANCELLED.\nCancellation was recorded on {res.get('cancellation_time', 'N/A')}. Further cancellation is prohibited.",
                fg=COLORS["danger"]
            )
            self.cancel_btn.config(state="disabled")
        else:
            # Academic cancellation rule: 20% fee, min 60.00
            charge = round(max(total_fare * 0.20, 60.00), 2)
            charge = min(charge, total_fare)
            refund = round(total_fare - charge, 2)

            self.orig_fare_lbl.config(text=f"₹ {total_fare:,.2f}")
            self.charge_lbl.config(text=f"₹ {charge:,.2f}")
            self.refund_lbl.config(text=f"₹ {refund:,.2f}")
            self.status_note_lbl.config(
                text=f"✓ Reservation is active and eligible for cancellation.\nEstimated refund: ₹ {refund:,.2f} (after 20% cancellation fee).",
                fg=COLORS["success"]
            )
            self.cancel_btn.config(state="normal")

    def confirm_cancellation(self):
        """Calls PL/SQL CANCEL_TICKET stored procedure."""
        if not self.current_res or not self.current_pnr:
            return

        reason = self.reason_entry.get().strip() or "Passenger Request"

        confirm = messagebox.askyesno(
            "Confirm Ticket Cancellation",
            f"Are you sure you want to cancel ticket with PNR: {self.current_pnr}?\n\n"
            f"• Original Fare: {self.orig_fare_lbl.cget('text')}\n"
            f"• Cancellation Charge (20%): {self.charge_lbl.cget('text')}\n"
            f"• Net Refund Amount: {self.refund_lbl.cget('text')}\n"
            f"• Reason: {reason}\n\n"
            f"This operation will execute the Oracle PL/SQL CANCEL_TICKET procedure, restore seat availability in TRAIN_SEATS, update payment status to REFUNDED, and record an audit entry."
        )
        if not confirm:
            return

        ok, refund_amt, fee, msg = cancel_ticket(self.current_pnr, reason=reason)

        if ok:
            messagebox.showinfo(
                "Cancellation Successful",
                f"🎉 TICKET CANCELLED SUCCESSFULLY!\n\n"
                f"• PNR: {self.current_pnr}\n"
                f"• Refund Amount: ₹ {refund_amt:,.2f}\n"
                f"• Cancellation Fee Retained: ₹ {fee:,.2f}\n\n"
                f"Seat inventory restored atomically in Oracle Database.\n"
                f"Audit trail recorded."
            )
            # Re-query details so UI reflects CANCELLED status
            self.lookup_pnr()
            # Refresh PNR suggestions so this PNR is immediately removed from active suggestions!
            self.refresh_pnr_list(preserve_selection=False)
        else:
            messagebox.showerror("Cancellation Failed", f"Could not cancel reservation:\n\n{msg}")
