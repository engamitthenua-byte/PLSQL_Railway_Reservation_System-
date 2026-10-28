"""
Dashboard Page View for Smart Railway Reservation System.
Visualizes database-backed live operational metrics, revenue summaries,
and recent reservation activity directly from Oracle Database.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from gui.theme import COLORS, FONTS
from services.report_service import get_dashboard_summary


class DashboardPage(tk.Frame):
    """Main dashboard overview frame displaying Oracle Database metrics."""

    def __init__(self, parent, navigate_callback: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.navigate = navigate_callback

        self.cards_frame = None
        self.shortcuts_frame = None
        self.tree = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Top Header Banner
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        title_box = tk.Frame(header, bg=COLORS["bg_main"])
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text="Railway Operations Dashboard",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="Live Oracle Database Metrics & Real-Time Operational Telemetry",
            font=FONTS["small"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_muted"],
        ).pack(anchor="w")

        refresh_btn = tk.Button(
            header,
            text="↻ Refresh Data",
            font=FONTS["body_bold"],
            bg=COLORS["primary"],
            fg="#FFFFFF",
            activebackground=COLORS["primary_light"],
            activeforeground="#FFFFFF",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.load_data,
        )
        refresh_btn.pack(side="right")

        # Container for Statistic Cards (Grid layout: 5 KPI cards across columns)
        self.cards_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        self.cards_frame.pack(fill="x", pady=(0, 10))
        for col in range(5):
            self.cards_frame.columnconfigure(col, weight=1, uniform="card")

        # Navigation Shortcuts Section
        self.shortcuts_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        self.shortcuts_frame.pack(fill="x", pady=(0, 12))
        for col in range(5):
            self.shortcuts_frame.columnconfigure(col, weight=1, uniform="shortcut")

        # Lower Content Section: Recent Reservation Activity Table
        content_frame = tk.Frame(self, bg=COLORS["bg_main"], padx=20)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))

        table_card_outer = tk.Frame(content_frame, bg=COLORS["border"], padx=1, pady=1)
        table_card_outer.pack(fill="both", expand=True)

        table_card = tk.Frame(table_card_outer, bg=COLORS["bg_card"], padx=16, pady=14)
        table_card.pack(fill="both", expand=True)

        card_header = tk.Frame(table_card, bg=COLORS["bg_card"])
        card_header.pack(fill="x", pady=(0, 10))

        tk.Label(
            card_header,
            text="Recent Reservation Activity",
            font=FONTS["h2"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"],
        ).pack(side="left")

        tk.Label(
            card_header,
            text="Live Oracle DB Transaction Records (RESERVATIONS & AUDIT_LOG)",
            font=FONTS["small"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(side="left", padx=12, pady=3)

        # Treeview Table
        columns = ("pnr", "passenger", "train", "route", "class", "pass_count", "fare", "status", "time")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)

        self.tree.heading("pnr", text="PNR Number")
        self.tree.heading("passenger", text="Passenger Name")
        self.tree.heading("train", text="Train")
        self.tree.heading("route", text="Route")
        self.tree.heading("class", text="Class")
        self.tree.heading("pass_count", text="Pax")
        self.tree.heading("fare", text="Total Fare")
        self.tree.heading("status", text="Booking Status")
        self.tree.heading("time", text="Booking Time")

        self.tree.column("pnr", width=120, anchor="center")
        self.tree.column("passenger", width=170, anchor="w")
        self.tree.column("train", width=80, anchor="center")
        self.tree.column("route", width=110, anchor="center")
        self.tree.column("class", width=60, anchor="center")
        self.tree.column("pass_count", width=50, anchor="center")
        self.tree.column("fare", width=95, anchor="e")
        self.tree.column("status", width=105, anchor="center")
        self.tree.column("time", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _render_stat_card(self, parent, row, col, title, value, subtitle, accent_color, icon_text=""):
        """Helper to create a single stylized KPI metric card."""
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        outer.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        card = tk.Frame(outer, bg=COLORS["bg_card"], padx=14, pady=12)
        card.pack(fill="both", expand=True)

        top_row = tk.Frame(card, bg=COLORS["bg_card"])
        top_row.pack(fill="x")

        tk.Label(
            top_row,
            text=title.upper(),
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_muted"],
        ).pack(side="left")

        if icon_text:
            icon_lbl = tk.Label(
                top_row,
                text=icon_text,
                font=("Segoe UI Symbol", 12),
                bg="#F1F5F9",
                fg=accent_color,
                padx=6,
                pady=2,
            )
            icon_lbl.pack(side="right")

        val_lbl = tk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"],
            anchor="w",
        )
        val_lbl.pack(fill="x", pady=(4, 2))

        sub_lbl = tk.Label(
            card,
            text=subtitle,
            font=FONTS["small"],
            bg=COLORS["bg_card"],
            fg=accent_color,
            anchor="w",
        )
        sub_lbl.pack(fill="x")

    def _render_shortcut_card(self, parent, col, title, action_text, target_page, color):
        """Helper to create quick action navigation shortcut cards."""
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        outer.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")

        card = tk.Frame(outer, bg=COLORS["bg_card"], padx=12, pady=10)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"]
        ).pack(anchor="w")

        if self.navigate:
            btn = tk.Button(
                card,
                text=action_text,
                font=FONTS["small_bold"],
                bg=color,
                fg="#FFFFFF",
                relief="flat",
                cursor="hand2",
                command=lambda: self.navigate(target_page)
            )
            btn.pack(anchor="w", pady=(6, 0))

    def load_data(self):
        """Fetches live summary statistics and recent bookings from Oracle Database."""
        try:
            summary = get_dashboard_summary()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load dashboard metrics:\n{e}")
            return

        # Clear existing card widgets
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # Render 5 Core Database KPI Cards
        # 1. Registered Passengers
        self._render_stat_card(
            self.cards_frame, 0, 0,
            "Passengers",
            f"{summary['total_passengers']}",
            "Registered in system",
            COLORS["primary"],
            "👥"
        )

        # 2. Total Trains
        self._render_stat_card(
            self.cards_frame, 0, 1,
            "Total Trains",
            f"{summary['total_trains']}",
            "Fleet services in DB",
            COLORS["accent"],
            "🚆"
        )

        # 3. Stations
        self._render_stat_card(
            self.cards_frame, 0, 2,
            "Total Stations",
            f"{summary['total_stations']}",
            "Junctions & Terminals",
            COLORS["secondary"],
            "🏛"
        )

        # 4. Confirmed Reservations
        self._render_stat_card(
            self.cards_frame, 0, 3,
            "Confirmed Bookings",
            f"{summary['confirmed_reservations']}",
            f"{summary['total_reservations']} total created",
            COLORS["success"],
            "🎫"
        )

        # 5. Cancelled Reservations
        self._render_stat_card(
            self.cards_frame, 0, 4,
            "Cancelled Tickets",
            f"{summary['cancelled_reservations']}",
            f"₹ {summary['total_revenue']:,.2f} net revenue",
            COLORS["danger"],
            "❌"
        )

        # Render Quick Action Shortcut Cards
        for widget in self.shortcuts_frame.winfo_children():
            widget.destroy()

        self._render_shortcut_card(self.shortcuts_frame, 0, "Passenger Records", "Manage Passengers ➔", "Passenger Management", COLORS["primary"])
        self._render_shortcut_card(self.shortcuts_frame, 1, "Train Fleet", "Manage Trains ➔", "Train Management", COLORS["accent"])
        self._render_shortcut_card(self.shortcuts_frame, 2, "Reserve Ticket", "Book Ticket ➔", "Book Ticket", COLORS["secondary"])
        self._render_shortcut_card(self.shortcuts_frame, 3, "Cancel Reservation", "Cancel Ticket ➔", "Cancel Ticket", COLORS["danger"])
        self._render_shortcut_card(self.shortcuts_frame, 4, "Reports & Cursors", "View Reports ➔", "Reports and Analytics", COLORS["info"])

        # Populate Recent Reservations Table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for b in summary["recent_activity"]:
            route_str = f"{b['from_code']} ➔ {b['to_code']}"
            status_tag = b["booking_status"].lower()
            self.tree.insert(
                "",
                "end",
                values=(
                    b["pnr_number"],
                    b["passenger_name"],
                    b["train_number"],
                    route_str,
                    b["seat_class"],
                    b["passenger_count"],
                    f"₹ {float(b['total_fare']):.2f}",
                    b["booking_status"],
                    b["booking_time"],
                ),
                tags=(status_tag,)
            )

        self.tree.tag_configure("confirmed", foreground=COLORS["success"])
        self.tree.tag_configure("cancelled", foreground=COLORS["danger"])
