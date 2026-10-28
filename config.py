"""
Configuration module for Smart Railway Reservation System.
A Python Tkinter Application Using Oracle Database and PL/SQL.
Loads settings from .env file or environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

# Oracle Database Settings
DB_USER = os.getenv("DB_USER", "railway_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
DB_SERVICE = os.getenv("DB_SERVICE", "FREEPDB1")

# Connection Pool Settings
DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", "2"))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", "10"))
DB_POOL_INC = int(os.getenv("DB_POOL_INC", "1"))

# Application Metadata
APP_TITLE = "Smart Railway Reservation System"
APP_SUBTITLE = "A Python Tkinter Application Using Oracle Database and PL/SQL"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# UI Theme Colors (Deep Railway Navy & Golden Amber Accent)
THEME_COLORS = {
    "primary": "#1A2B4C",          # Deep Indian Railway Navy
    "primary_dark": "#0F1A2E",     # Midnight Blue
    "primary_light": "#284273",    # Lighter Slate Blue
    "secondary": "#D97706",        # Golden Amber / Warm Rail Gold
    "accent": "#0D9488",           # Teal
    "bg_light": "#F8FAFC",         # Crisp light background
    "bg_card": "#FFFFFF",          # Card white
    "bg_sidebar": "#111827",       # Dark slate sidebar
    "text_dark": "#1E293B",        # Slate dark text
    "text_muted": "#64748B",       # Subtle gray text
    "text_light": "#F8FAFC",       # White text
    "border": "#E2E8F0",           # Border gray
    "success": "#16A34A",          # Forest Green
    "danger": "#DC2626",           # Crimson Red
    "warning": "#EAB308",          # Warning Yellow
    "info": "#2563EB",             # Cobalt Blue
}
