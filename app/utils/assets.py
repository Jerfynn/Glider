"""
Vector Assets Generator and Exporter for GliderView Qt Stylesheets.
Generates crisp SVG icons for Dropdown Arrows and Checkbox Tick Marks for White / Light Theme.
"""

import os
from qtpy.QtGui import QPixmap, QPainter, QColor, QPen, QImage
from qtpy.QtCore import Qt, QByteArray, QPointF
from qtpy.QtSvg import QSvgRenderer

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

CHEVRON_DOWN_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M4 6L8 10L12 6" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

CHEVRON_DOWN_HOVER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M4 6L8 10L12 6" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

CHECKMARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <rect width="16" height="16" rx="3" fill="#D97706"/>
    <path d="M3.5 8.5L6.5 11.5L12.5 4.5" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

CHECKBOX_UNCHECKED_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <rect x="0.75" y="0.75" width="14.5" height="14.5" rx="2.5" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>
</svg>"""

CHECKBOX_HOVER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">
    <rect x="0.75" y="0.75" width="14.5" height="14.5" rx="2.5" fill="#F8FAFC" stroke="#D97706" stroke-width="1.5"/>
</svg>"""


def export_assets():
    """Writes SVG asset files and returns their absolute paths formatted with forward slashes for QSS."""
    files = {
        "chevron_down.svg": CHEVRON_DOWN_SVG,
        "chevron_down_hover.svg": CHEVRON_DOWN_HOVER_SVG,
        "checkbox_checked.svg": CHECKMARK_SVG,
        "checkbox_unchecked.svg": CHECKBOX_UNCHECKED_SVG,
        "checkbox_hover.svg": CHECKBOX_HOVER_SVG,
    }

    paths = {}
    for filename, content in files.items():
        filepath = os.path.join(ASSETS_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass
        paths[filename.split(".")[0]] = filepath.replace("\\", "/")

    return paths


ASSET_PATHS = export_assets()

