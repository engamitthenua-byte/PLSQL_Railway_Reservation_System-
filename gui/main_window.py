"""
Main Application Window for Smart Railway Reservation System.
A Python Tkinter Application Using Oracle Database and PL/SQL.
Provides a modern desktop layout with sidebar navigation, top status bar with
live Oracle DB health indicator, and unified view routing.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

import config
from gui.theme import COLORS, FONTS, apply_custom_styles
from gui.dashboard_page import DashboardPage
from gui.passenger_page import PassengerPage
from gui.train_page import TrainPage
from gui.booking_page import BookingPage
from gui.cancellation_page import CancellationPage
from gui.reservations_page import ReservationsPage
from gui.reports_page import ReportsPage
from database.db_connection import test_connection, close_pool


class MainWindow(tk.Tk):
    """Primary application window and navigation controller."""

    def __init__(self):
        super().__init__()

        self.title(f"{config.APP_TITLE} - {config.APP_SUBTITLE}")
        self.geometry("1340x840")
        self.minsize(1100, 700)
        self.configure(bg=COLORS["bg_main"])

        # Configure TTK styles
        apply_custom_styles(self)

        self.current_page_name = None
        self.pages: Dict[str, tk.Frame] = {}
        self.sidebar_buttons: Dict[str, tk.Button] = {}

        self._build_layout()
        self._test_database_status()

        # Handle window close event cleanly
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Show Dashboard initially
        self.show_page("Dashboard")

    def _build_layout(self):
        # 1. Top Application Bar
        top_bar = tk.Frame(self, bg=COLORS["primary"], height=66, padx=18, pady=10)
        top_bar.pack(side="top", fill="x")

        # Brand / Title
        brand_frame = tk.Frame(top_bar, bg=COLORS["primary"])
        brand_frame.pack(side="left")

        logo_lbl = tk.Label(
            brand_frame,
            text="🚆",
            font=("Segoe UI Emoji", 24),
            bg=COLORS["primary"],
            fg=COLORS["secondary"],
        )
        logo_lbl.pack(side="left", padx=(0, 12))

        title_box = tk.Frame(brand_frame, bg=COLORS["primary"])
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text=config.APP_TITLE,
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["primary"],
            fg="#FFFFFF",
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text=config.APP_SUBTITLE,
            font=("Segoe UI", 9),
            bg=COLORS["primary"],
            fg="#94A3B8",
        ).pack(anchor="w")

        # Database Status Indicator (Right side of top bar)
        self.db_status_frame = tk.Frame(top_bar, bg=COLORS["primary"])
        self.db_status_frame.pack(side="right")

        self.db_dot = tk.Label(
            self.db_status_frame,
            text="●",
            font=("Segoe UI", 14),
            bg=COLORS["primary"],
            fg="#94A3B8",
        )
        self.db_dot.pack(side="left", padx=(0, 4))

        self.db_status_lbl = tk.Label(
            self.db_status_frame,
            text="Connecting to Oracle DB...",
            font=FONTS["small_bold"],
            bg=COLORS["primary"],
            fg="#E2E8F0",
        )
        self.db_status_lbl.pack(side="left", padx=(0, 10))

        reconn_btn = tk.Button(
            self.db_status_frame,
            text="Verify Connection",
            font=("Segoe UI", 8, "bold"),
            bg="#284273",
            fg="#FFFFFF",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._test_database_status
        )
        reconn_btn.pack(side="left")

        # 2. Main Workspace (Sidebar + Content Container)
        workspace = tk.Frame(self, bg=COLORS["bg_main"])
        workspace.pack(side="top", fill="both", expand=True)

        # Left Sidebar
        self.sidebar = tk.Frame(workspace, bg=COLORS["bg_sidebar"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Final Navigation items (Exactly 8 options as per requirements)
        nav_items = [
            ("Dashboard", "📊", "Dashboard"),
            ("Passenger Management", "👥", "Passenger Management"),
            ("Train Management", "🚆", "Train Management"),
            ("Book Ticket", "🎫", "Book Ticket"),
            ("Cancel Ticket", "❌", "Cancel Ticket"),
            ("My Reservations", "📑", "My Reservations"),
            ("Reports and Analytics", "📈", "Reports & Analytics"),
            ("Exit", "🚪", "Exit Application"),
        ]

        tk.Label(
            self.sidebar,
            text="NAVIGATION MENU",
            font=("Segoe UI", 8, "bold"),
            bg=COLORS["bg_sidebar"],
            fg="#64748B",
            padx=16,
            pady=14,
            anchor="w"
        ).pack(fill="x")

        for key, icon, label in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}   {label}",
                font=("Segoe UI", 10),
                bg=COLORS["bg_sidebar"],
                fg="#E2E8F0",
                activebackground=COLORS["sidebar_hover"],
                activeforeground="#FFFFFF",
                relief="flat",
                anchor="w",
                padx=16,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x")
            self.sidebar_buttons[key] = btn

        # Bottom System Info in Sidebar
        side_footer = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], padx=16, pady=14)
        side_footer.pack(side="bottom", fill="x")

        tk.Label(
            side_footer,
            text=f"Oracle User: {config.DB_USER}",
            font=("Segoe UI", 8),
            bg=COLORS["bg_sidebar"],
            fg="#94A3B8",
            anchor="w"
        ).pack(fill="x")
        tk.Label(
            side_footer,
            text=f"Service: {config.DB_SERVICE} ({config.DB_HOST}:{config.DB_PORT})",
            font=("Segoe UI", 8),
            bg=COLORS["bg_sidebar"],
            fg="#64748B",
            anchor="w"
        ).pack(fill="x")

        # Right Content View Area
        self.content_container = tk.Frame(workspace, bg=COLORS["bg_main"])
        self.content_container.pack(side="right", fill="both", expand=True)

        # Initialize View Pages
        self.pages["Dashboard"] = DashboardPage(self.content_container, navigate_callback=self.show_page)
        self.pages["Passenger Management"] = PassengerPage(self.content_container)
        self.pages["Train Management"] = TrainPage(self.content_container)
        self.pages["Book Ticket"] = BookingPage(self.content_container, on_booking_success=lambda pnr: self._on_ticket_booked(pnr))
        self.pages["Cancel Ticket"] = CancellationPage(self.content_container)
        self.pages["My Reservations"] = ReservationsPage(self.content_container)
        reports_page = ReportsPage(self.content_container)
        self.pages["Reports and Analytics"] = reports_page
        self.pages["Reports & Analytics"] = reports_page

    def _test_database_status(self):
        """Tests live Oracle DB connectivity and updates indicator badge."""
        ok, msg = test_connection()
        if ok:
            self.db_dot.config(fg="#22C55E")  # Green
            self.db_status_lbl.config(
                text=f"Oracle DB Connected ({config.DB_SERVICE})",
                fg="#22C55E"
            )
        else:
            self.db_dot.config(fg="#EF4444")  # Red
            self.db_status_lbl.config(
                text="Oracle Disconnected",
                fg="#EF4444"
            )

    def show_page(self, page_name: str):
        """Switches the active frame in the content area."""
        if page_name == "Exit":
            self.on_exit()
            return

        # Normalize page name variations
        if page_name in ("Reports and Analytics", "Reports & Analytics"):
            page_name = "Reports and Analytics"

        if page_name not in self.pages:
            messagebox.showwarning("Navigation", f"Page '{page_name}' is not registered.")
            return

        # Update sidebar button highlight styles
        for key, btn in self.sidebar_buttons.items():
            if key == page_name:
                btn.config(bg=COLORS["sidebar_active"], fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg=COLORS["bg_sidebar"], fg="#E2E8F0", font=("Segoe UI", 10))

        # Hide current page
        if self.current_page_name and self.current_page_name in self.pages:
            self.pages[self.current_page_name].pack_forget()

        # Show target page
        target_page = self.pages[page_name]
        target_page.pack(fill="both", expand=True)
        self.current_page_name = page_name

        # Trigger data refresh if page has load_data method
        if hasattr(target_page, "load_data"):
            try:
                target_page.load_data()
            except Exception:
                pass

    def _on_ticket_booked(self, pnr: str):
        """Callback when a ticket is successfully booked."""
        # Refresh Dashboard data
        dash_page: DashboardPage = self.pages["Dashboard"]
        dash_page.load_data()
        # Optionally show reservations
        self.show_page("My Reservations")

    def on_exit(self):
        """Closes resources gracefully and exits."""
        confirm = messagebox.askyesno(
            "Exit System",
            "Are you sure you want to exit the Smart Railway Reservation System?"
        )
        if confirm:
            try:
                close_pool()
            except Exception:
                pass
            self.destroy()
            sys.exit(0)
