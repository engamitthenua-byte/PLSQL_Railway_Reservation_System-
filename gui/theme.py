"""
UI Theme and Styling Configurations for Tkinter & ttk.
Defines cohesive color palettes, typography, card containers, and ttk styles.
Theme Inspiration: Modern Railway Enterprise Dashboard.
"""

import tkinter as tk
from tkinter import ttk
from typing import Tuple

import config

# Color Palette
COLORS = {
    "primary": "#1A2B4C",          # Deep Railway Navy
    "primary_dark": "#0F172A",     # Midnight Slate
    "primary_light": "#253D68",    # Slate Blue
    "secondary": "#D97706",        # Golden Rail Amber
    "secondary_light": "#F59E0B",  # Bright Amber
    "accent": "#0D9488",           # Teal Cyan
    "bg_main": "#F1F5F9",          # Soft Slate Background
    "bg_card": "#FFFFFF",          # Pure Card White
    "bg_sidebar": "#1E293B",       # Dark Slate Sidebar
    "sidebar_hover": "#334155",    # Sidebar item hover
    "sidebar_active": "#2563EB",   # Selected sidebar menu item
    "text_dark": "#0F172A",        # Header text
    "text_body": "#334155",        # Body text
    "text_muted": "#64748B",       # Subtitle / placeholder
    "text_light": "#F8FAFC",       # White text
    "border": "#E2E8F0",           # Subtle border
    "border_focus": "#3B82F6",     # Active input border
    "success": "#16A34A",          # Forest Green
    "danger": "#DC2626",           # Crimson Red
    "warning": "#D97706",          # Warning Amber
    "info": "#2563EB",             # Info Blue
}

# Typography Definitions
FONTS = {
    "h1": ("Segoe UI", 18, "bold"),
    "h2": ("Segoe UI", 14, "bold"),
    "h3": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "mono": ("Consolas", 10),
    "mono_bold": ("Consolas", 10, "bold"),
    "icon": ("Segoe UI Symbol", 12),
}


def apply_custom_styles(root: tk.Tk):
    """Configures ttk styles for a modern, sleek appearance."""
    style = ttk.Style(root)
    # Use 'clam' as base for customizable ttk styling
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Treeview Styling
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground=COLORS["text_dark"],
        rowheight=28,
        fieldbackground="#FFFFFF",
        font=FONTS["body"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground=COLORS["text_dark"],
        font=FONTS["small_bold"],
        relief="flat",
        padding=(6, 6),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#CBD5E1")]
    )
    style.map(
        "Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", "#1E3A8A")]
    )

    # Primary Action Button
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["text_light"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_light"]), ("pressed", COLORS["primary_dark"])],
        foreground=[("active", "#FFFFFF")]
    )

    # Secondary / Accent Button
    style.configure(
        "Secondary.TButton",
        background=COLORS["secondary"],
        foreground=COLORS["text_light"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["secondary_light"]), ("pressed", "#B45309")],
        foreground=[("active", "#FFFFFF")]
    )

    # Success Button
    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground=COLORS["text_light"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        relief="flat",
    )
    style.map(
        "Success.TButton",
        background=[("active", "#22C55E")]
    )

    # Danger Button
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground=COLORS["text_light"],
        font=FONTS["body_bold"],
        padding=(12, 6),
        relief="flat",
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#EF4444")]
    )

    # Combobox
    style.configure(
        "TCombobox",
        fieldbackground="#FFFFFF",
        background="#FFFFFF",
        foreground=COLORS["text_dark"],
        font=FONTS["body"],
        padding=4,
    )

    # Notebook Tabs
    style.configure(
        "TNotebook",
        background=COLORS["bg_main"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background="#E2E8F0",
        foreground=COLORS["text_body"],
        font=FONTS["body_bold"],
        padding=(14, 8),
        relief="flat",
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#FFFFFF"), ("active", "#CBD5E1")],
        foreground=[("selected", COLORS["primary"])]
    )


def create_card(parent, bg=COLORS["bg_card"], border_color=COLORS["border"], padx=16, pady=16) -> tk.Frame:
    """Creates a container frame styled as a modern elevation card."""
    outer = tk.Frame(parent, bg=border_color, padx=1, pady=1)
    card = tk.Frame(outer, bg=bg, padx=padx, pady=pady)
    card.pack(fill="both", expand=True)
    return outer
