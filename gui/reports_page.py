"""
Reports & Analytics Page View for Smart Railway Reservation System.
Visualizes revenue yields, train performance, seat occupancy percentages,
and embeds Matplotlib charts inside Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import COLORS, FONTS, create_card
from services.report_service import (
    get_train_performance_report,
    get_seat_occupancy_by_class,
    get_cancellations_report,
    get_dashboard_summary
)


class ReportsPage(tk.Frame):
    """Financial yields, operational reporting, and data visualization interface."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.notebook = None
        self.train_tree = None
        self.occupancy_tree = None
        self.cancel_tree = None
        self.chart_frame = None
        self.canvas = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_main"], pady=12, padx=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Reports, Analytics & Financial Yields",
            font=FONTS["h1"],
            bg=COLORS["bg_main"],
            fg=COLORS["text_dark"],
        ).pack(side="left")

        refresh_btn = tk.Button(
            header,
            text="↻ Regenerate Reports",
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

        # Tabbed Notebook Container
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # TAB 1: Train Performance & Revenue Report
        tab1 = tk.Frame(self.notebook, bg=COLORS["bg_main"], padx=14, pady=14)
        self.notebook.add(tab1, text="🚆 Train Revenue & Yields")
        self._build_train_report_tab(tab1)

        # TAB 2: Class Occupancy Breakdown
        tab2 = tk.Frame(self.notebook, bg=COLORS["bg_main"], padx=14, pady=14)
        self.notebook.add(tab2, text="💺 Seat Occupancy Analysis")
        self._build_occupancy_tab(tab2)

        # TAB 3: Visual Charts (Matplotlib)
        tab3 = tk.Frame(self.notebook, bg=COLORS["bg_main"], padx=14, pady=14)
        self.notebook.add(tab3, text="📊 Visual Analytics (Charts)")
        self._build_charts_tab(tab3)

        # TAB 4: Cancellations & Refund Audit
        tab4 = tk.Frame(self.notebook, bg=COLORS["bg_main"], padx=14, pady=14)
        self.notebook.add(tab4, text="📋 Cancellations & Audit Log")
        self._build_cancellations_tab(tab4)

    def _build_train_report_tab(self, parent):
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=COLORS["bg_card"], padx=14, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Train-wise Revenue and Passenger Loads (Generated via PL/SQL Procedure)", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        cols = ("num", "name", "res_count", "conf_pax", "can_pax", "gross_rev", "can_fees", "net_rev")
        self.train_tree = ttk.Treeview(card, columns=cols, show="headings", height=12)

        self.train_tree.heading("num", text="Train No")
        self.train_tree.heading("name", text="Train Name")
        self.train_tree.heading("res_count", text="Total Res")
        self.train_tree.heading("conf_pax", text="Confirmed Pax")
        self.train_tree.heading("can_pax", text="Cancelled Pax")
        self.train_tree.heading("gross_rev", text="Gross Fare")
        self.train_tree.heading("can_fees", text="Fees Retained")
        self.train_tree.heading("net_rev", text="Net Revenue")

        self.train_tree.column("num", width=80, anchor="center")
        self.train_tree.column("name", width=220, anchor="w")
        self.train_tree.column("res_count", width=80, anchor="center")
        self.train_tree.column("conf_pax", width=95, anchor="center")
        self.train_tree.column("can_pax", width=95, anchor="center")
        self.train_tree.column("gross_rev", width=110, anchor="e")
        self.train_tree.column("can_fees", width=110, anchor="e")
        self.train_tree.column("net_rev", width=120, anchor="e")

        scroller = ttk.Scrollbar(card, orient="vertical", command=self.train_tree.yview)
        self.train_tree.configure(yscrollcommand=scroller.set)

        self.train_tree.pack(side="left", fill="both", expand=True)
        scroller.pack(side="right", fill="y")

    def _build_occupancy_tab(self, parent):
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=COLORS["bg_card"], padx=14, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Seat Class Inventory & Capacity Utilization", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        cols = ("class", "desc", "total", "booked", "avail", "pct")
        self.occupancy_tree = ttk.Treeview(card, columns=cols, show="headings", height=8)

        self.occupancy_tree.heading("class", text="Class Code")
        self.occupancy_tree.heading("desc", text="Category Description")
        self.occupancy_tree.heading("total", text="Total Capacity")
        self.occupancy_tree.heading("booked", text="Booked Seats")
        self.occupancy_tree.heading("avail", text="Available Seats")
        self.occupancy_tree.heading("pct", text="Occupancy Rate")

        self.occupancy_tree.column("class", width=90, anchor="center")
        self.occupancy_tree.column("desc", width=180, anchor="w")
        self.occupancy_tree.column("total", width=120, anchor="center")
        self.occupancy_tree.column("booked", width=120, anchor="center")
        self.occupancy_tree.column("avail", width=120, anchor="center")
        self.occupancy_tree.column("pct", width=120, anchor="center")

        self.occupancy_tree.pack(fill="both", expand=True)

    def _build_charts_tab(self, parent):
        self.chart_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        self.chart_frame.pack(fill="both", expand=True)

    def _build_cancellations_tab(self, parent):
        outer = tk.Frame(parent, bg=COLORS["border"], padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(outer, bg=COLORS["bg_card"], padx=14, pady=12)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Cancellation Log & Refund Ledger (Triggers & Audit Trail)", font=FONTS["h3"], bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(0, 8))

        cols = ("ref", "pnr", "passenger", "train", "date", "class", "refund", "charge", "time", "reason")
        self.cancel_tree = ttk.Treeview(card, columns=cols, show="headings", height=10)

        self.cancel_tree.heading("ref", text="Cancel Ref")
        self.cancel_tree.heading("pnr", text="PNR")
        self.cancel_tree.heading("passenger", text="Passenger")
        self.cancel_tree.heading("train", text="Train")
        self.cancel_tree.heading("date", text="Journey Date")
        self.cancel_tree.heading("class", text="Class")
        self.cancel_tree.heading("refund", text="Refund Paid")
        self.cancel_tree.heading("charge", text="Cancellation Fee")
        self.cancel_tree.heading("time", text="Timestamp")
        self.cancel_tree.heading("reason", text="Reason")

        self.cancel_tree.column("ref", width=130, anchor="center")
        self.cancel_tree.column("pnr", width=100, anchor="center")
        self.cancel_tree.column("passenger", width=140, anchor="w")
        self.cancel_tree.column("train", width=65, anchor="center")
        self.cancel_tree.column("date", width=85, anchor="center")
        self.cancel_tree.column("class", width=50, anchor="center")
        self.cancel_tree.column("refund", width=95, anchor="e")
        self.cancel_tree.column("charge", width=95, anchor="e")
        self.cancel_tree.column("time", width=120, anchor="center")
        self.cancel_tree.column("reason", width=150, anchor="w")

        scroller = ttk.Scrollbar(card, orient="vertical", command=self.cancel_tree.yview)
        self.cancel_tree.configure(yscrollcommand=scroller.set)

        self.cancel_tree.pack(side="left", fill="both", expand=True)
        scroller.pack(side="right", fill="y")

    def load_data(self):
        """Fetches reporting datasets and redraws Matplotlib figures."""
        try:
            # 1. Train Performance Report
            perf = get_train_performance_report()
            for item in self.train_tree.get_children():
                self.train_tree.delete(item)

            for p in perf:
                self.train_tree.insert(
                    "",
                    "end",
                    values=(
                        p["train_number"],
                        p["train_name"],
                        p["total_reservations"],
                        p["confirmed_passengers"],
                        p["cancelled_passengers"],
                        f"₹ {float(p['gross_revenue']):,.2f}",
                        f"₹ {float(p['cancellation_fees_retained']):,.2f}",
                        f"₹ {float(p['net_revenue']):,.2f}",
                    )
                )

            # 2. Seat Occupancy Report
            occupancy = get_seat_occupancy_by_class()
            class_desc_map = {
                "1A": "AC First Class",
                "2A": "AC 2 Tier",
                "3A": "AC 3 Tier",
                "SL": "Sleeper Class"
            }
            for item in self.occupancy_tree.get_children():
                self.occupancy_tree.delete(item)

            for o in occupancy:
                c_code = o["seat_class"]
                pct_str = f"{float(o['occupancy_pct'] or 0.0):.1f}%"
                self.occupancy_tree.insert(
                    "",
                    "end",
                    values=(
                        c_code,
                        class_desc_map.get(c_code, "Standard"),
                        o["total_seats"],
                        o["booked_seats"],
                        o["available_seats"],
                        pct_str
                    )
                )

            # 3. Cancellations Report
            cancels = get_cancellations_report()
            for item in self.cancel_tree.get_children():
                self.cancel_tree.delete(item)

            for c in cancels:
                self.cancel_tree.insert(
                    "",
                    "end",
                    values=(
                        c["cancellation_ref"],
                        c["pnr_number"],
                        c["passenger_name"],
                        c["train_number"],
                        str(c["journey_date"])[:10],
                        c["seat_class"],
                        f"₹ {float(c['refund_amount']):.2f}",
                        f"₹ {float(c['cancellation_charge']):.2f}",
                        c["cancel_time"],
                        c["reason"] or "N/A"
                    )
                )

            # 4. Draw Matplotlib Charts
            self._render_charts(perf, occupancy)

        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate reports:\n{e}")

    def _render_charts(self, perf_data: List[Dict[str, Any]], occ_data: List[Dict[str, Any]]):
        """Draws two side-by-side charts: Revenue by Train and Class Distribution."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(9, 4.5), dpi=100, facecolor="#FFFFFF")

        # Subplot 1: Train Revenue Bar Chart
        ax1 = fig.add_subplot(121)
        train_names = [f"{p['train_number']}" for p in perf_data[:6]]
        revenues = [float(p["net_revenue"]) for p in perf_data[:6]]

        bars = ax1.bar(train_names, revenues, color="#1A2B4C", width=0.55)
        ax1.set_title("Top Train Revenue (₹)", fontsize=11, fontweight="bold", pad=8)
        ax1.set_ylabel("Net Revenue (INR)", fontsize=9)
        ax1.tick_params(axis="x", rotation=35, labelsize=8)
        ax1.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.annotate(
                    f"₹{int(height)}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=7, fontweight="bold"
                )

        # Subplot 2: Seat Occupancy Pie / Bar Chart
        ax2 = fig.add_subplot(122)
        classes = [o["seat_class"] for o in occ_data]
        booked_vals = [int(o["booked_seats"]) for o in occ_data]
        avail_vals = [int(o["available_seats"]) for o in occ_data]

        # Stacked bar
        x_idx = range(len(classes))
        ax2.bar(x_idx, booked_vals, label="Booked Seats", color="#D97706", width=0.5)
        ax2.bar(x_idx, avail_vals, bottom=booked_vals, label="Available Seats", color="#CBD5E1", width=0.5)
        ax2.set_xticks(x_idx)
        ax2.set_xticklabels(classes, fontsize=9)
        ax2.set_title("Seat Capacity by Travel Class", fontsize=11, fontweight="bold", pad=8)
        ax2.set_ylabel("Number of Seats", fontsize=9)
        ax2.legend(fontsize=8, loc="upper right")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)

        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
