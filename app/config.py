"""
Application Configuration and Constants for GliderView.
Clean, Professional White / Light Theme with Industrial Yellow/Amber Accents.
"""

APP_NAME = "GliderView"
APP_VERSION = "v1.0.0"
APP_SUBTITLE = "Underwater Glider Telemetry Viewer"

# Standard Baud Rates
DEFAULT_BAUD_RATES = [
    "9600",
    "19200",
    "38400",
    "57600",
    "115200",
    "230400",
    "460800",
    "921600"
]

DEFAULT_DATA_BITS = ["8", "7", "6", "5"]
DEFAULT_PARITIES = ["None", "Even", "Odd", "Mark", "Space"]
DEFAULT_STOP_BITS = ["1", "1.5", "2"]

# Time Windows for Graphs (seconds)
GRAPH_TIME_WINDOWS = {
    "10 Seconds": 10,
    "30 Seconds": 30,
    "60 Seconds": 60,
    "2 Minutes": 120,
    "5 Minutes": 300
}

# Professional White / Light Theme Palette
COLORS = {
    # Backgrounds (Clean White & Soft Off-White Surfaces)
    "bg_main": "#F3F4F6",           # Clean light gray/off-white main background
    "bg_card": "#FFFFFF",           # Pure white card/panel surfaces
    "bg_card_hover": "#F8FAFC",     # Subtle hover surface
    "bg_card_secondary": "#EDF0F4", # Secondary inset panels
    "bg_input": "#FFFFFF",          # Inset input background
    "bg_terminal": "#0F172A",       # High-contrast dark slate terminal for log clarity
    
    # Borders (Crisp Light Grays)
    "border": "#E2E8F0",            # Subtle crisp border
    "border_subtle": "#EEF2F6",     # Divider line
    "border_highlight": "#CBD5E1",  # Active/hover border
    
    # Typography (High-Contrast Clean Text)
    "text_primary": "#0F172A",      # Deep dark slate / near-black primary text
    "text_secondary": "#64748B",    # Muted dark slate secondary labels
    "text_muted": "#94A3B8",        # Dim / inactive text
    "text_dim": "#CBD5E1",          # Watermark / disabled
    
    # Primary Accent: Professional Industrial Amber/Yellow
    "accent_yellow": "#D97706",     # Rich readable amber gold
    "accent_yellow_hover": "#B45309",
    "accent_yellow_pressed": "#92400E",
    "accent_yellow_subtle": "#FEF3C7", # Light amber highlight pill
    "accent_yellow_text": "#FFFFFF",
    
    # Status Colors (Clean Light Badges)
    "status_green": "#15803D",      # Crisp forest green text
    "status_green_bg": "#DCFCE7",   # Soft green pill bg
    "status_green_border": "#86EFAC",# Green pill border
    
    "status_amber": "#B45309",      # Amber text
    "status_amber_bg": "#FEF3C7",   # Soft amber pill bg
    "status_amber_border": "#FCD34D",
    
    "status_red": "#DC2626",        # Clean red text
    "status_red_bg": "#FEE2E2",     # Soft red pill bg
    "status_red_border": "#FCA5A5", # Red pill border
    
    # Graph Traces (Vibrant and readable on white background)
    "trace_roll": "#16A34A",        # Emerald green
    "trace_pitch": "#D97706",       # Industrial amber
    "trace_yaw": "#2563EB",         # Royal steel blue
    
    # 3D Vehicle & Environment
    "glider_yellow": "#E5A124",     # Industrial yellow hull
    "glider_hull": "#334155",       # Dark collar/prop trims
    "grid_color": "#E2E8F0",        # Subtle light grid
}
