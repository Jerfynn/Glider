"""
Vector SVG Icon Provider for GliderView.
Renders crisp vector icons for Clean White / Light Theme.
"""

from qtpy.QtGui import QIcon, QPixmap, QPainter, QColor, QImage
from qtpy.QtSvg import QSvgRenderer
from qtpy.QtCore import QByteArray, QSize, Qt

ICONS_SVG = {
    "logo_glider": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="#D97706" stroke-width="1.8" fill="#FEF3C7"/>
            <path d="M7 16C10 13.5 14 13.5 17 16C20 18.5 24 18.5 27 16" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 19C8 16.5 12 16.5 15 19C18 21.5 22 21.5 25 19" stroke="#D97706" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.85"/>
        </svg>
    """,
    "chevron_down": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
    """,
    "check": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
    """,
    "reset_view": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
    """,
    "pan": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v3"></path>
            <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v6"></path>
            <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"></path>
            <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"></path>
        </svg>
    """,
    "rotate": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
    """,
    "zoom_in": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
    """,
    "zoom_out": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
    """,
    "fit_view": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
        </svg>
    """,
    "refresh": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
    """
}


def get_icon(name: str, color: str = "#64748B", size: int = 18) -> QIcon:
    """Returns a QIcon from the SVG dictionary with the requested stroke color and size."""
    raw_svg = ICONS_SVG.get(name)
    if not raw_svg:
        return QIcon()

    svg_data = raw_svg.replace('stroke="currentColor"', f'stroke="{color}"')
    
    renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
    image = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    return QIcon(QPixmap.fromImage(image))
