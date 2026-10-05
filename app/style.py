"""
Professional Clean White / Light Theme Ground Control Station Stylesheet.
"""

from app.config import COLORS
from app.utils.assets import ASSET_PATHS

MAIN_STYLESHEET = f"""
/* Global Reset & Base Typography */
QMainWindow, QWidget#CentralWidget {{
    background-color: {COLORS['bg_main']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', 'Roboto', sans-serif;
    font-size: 12px;
}}

/* Card Panels */
QFrame.GliderCard, QFrame#ConnectionCard, QFrame#SerialStatusCard, QFrame#RawStreamCard, 
QFrame#TelemetryMetricsCard, QFrame#AttitudeIndicatorCard, QFrame#TelemetryGraphsCard,
QFrame#MapViewCard, QFrame#SettingsCard, QFrame#VehicleModeCard {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QFrame.GliderCard:hover {{
    border-color: {COLORS['border_highlight']};
}}

/* Section Headers */
QLabel#CardTitle {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    color: {COLORS['text_primary']};
    text-transform: uppercase;
    padding-bottom: 2px;
}}

QLabel#SubtleLabel {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    font-weight: 500;
}}

QLabel#MetricValue {{
    font-size: 12px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
}}

/* Dropdowns / QComboBox */
QComboBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    padding: 3px 8px;
    color: {COLORS['text_primary']};
    font-size: 12px;
    min-height: 24px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_highlight']};
    background-color: {COLORS['bg_card_hover']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent_yellow']};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left-width: 0px;
    background: transparent;
}}

QComboBox::down-arrow {{
    image: url("{ASSET_PATHS['chevron_down']}");
    width: 12px;
    height: 12px;
    margin-right: 4px;
}}

QComboBox::down-arrow:hover {{
    image: url("{ASSET_PATHS['chevron_down_hover']}");
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_highlight']};
    border-radius: 3px;
    selection-background-color: {COLORS['accent_yellow_subtle']};
    selection-color: {COLORS['text_primary']};
    color: {COLORS['text_primary']};
    padding: 3px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    min-height: 22px;
    padding: 2px 8px;
    border-radius: 2px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {COLORS['bg_card_secondary']};
    color: {COLORS['text_primary']};
}}

/* Line Inputs / QLineEdit */
QLineEdit {{
    background-color: #FFFFFF;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    padding: 3px 8px;
    color: {COLORS['text_primary']};
    font-size: 12px;
    font-weight: 600;
    font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
    min-height: 24px;
    selection-background-color: {COLORS['accent_yellow']};
    selection-color: #FFFFFF;
}}

QLineEdit:hover {{
    border-color: {COLORS['border_highlight']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_yellow']};
    background-color: #FFFFFF;
}}

QLineEdit:disabled {{
    background-color: #F3F4F6;
    color: {COLORS['text_secondary']};
    border-color: {COLORS['border']};
}}

/* Push Buttons */
QPushButton {{
    background-color: #FFFFFF;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    padding: 4px 10px;
    font-weight: 500;
    font-size: 11px;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['border_highlight']};
    color: {COLORS['text_primary']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_card_secondary']};
}}

QPushButton#PrimaryButton {{
    background-color: {COLORS['accent_yellow']};
    border: 1px solid {COLORS['accent_yellow_hover']};
    color: #FFFFFF;
    font-weight: 700;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {COLORS['accent_yellow_hover']};
}}

QPushButton#PrimaryButton:pressed {{
    background-color: {COLORS['accent_yellow_pressed']};
}}

QPushButton#DisconnectButton {{
    background-color: {COLORS['status_red_bg']};
    border: 1px solid {COLORS['status_red_border']};
    color: {COLORS['status_red']};
    font-weight: 600;
}}

QPushButton#DisconnectButton:hover {{
    background-color: #FECDCA;
    color: #991B1B;
}}

QPushButton#DisconnectButton:pressed {{
    background-color: #FCA5A5;
}}

/* Navigation Toolbar Buttons */
QPushButton#NavToolButton {{
    background-color: #FFFFFF;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    padding: 3px 8px;
    color: {COLORS['text_secondary']};
    font-size: 11px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton#NavToolButton:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['border_highlight']};
    color: {COLORS['text_primary']};
}}

/* Tab Widget & Bar */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['bg_card']};
    border-radius: 0 0 4px 4px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 14px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

QTabBar::tab:selected {{
    color: {COLORS['text_primary']};
    border-bottom: 2px solid {COLORS['accent_yellow']};
}}

QTabBar::tab:hover:!selected {{
    color: {COLORS['text_primary']};
    background-color: rgba(0, 0, 0, 0.03);
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: {COLORS['bg_main']};
    width: 6px;
    margin: 0px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border_highlight']};
    min-height: 20px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['accent_yellow']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: {COLORS['bg_main']};
    height: 6px;
    margin: 0px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['border_highlight']};
    min-width: 20px;
    border-radius: 3px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Terminal Log View */
QPlainTextEdit, QTextEdit {{
    background-color: {COLORS['bg_terminal']};
    color: #E2E8F0;
    font-family: 'Consolas', 'Roboto Mono', 'SF Mono', monospace;
    font-size: 11px;
    border: 1px solid {COLORS['border']};
    border-radius: 3px;
    padding: 6px;
    line-height: 1.4;
}}

/* CheckBoxes with crisp vector Tick Marks */
QCheckBox {{
    color: {COLORS['text_primary']};
    font-size: 11px;
    spacing: 7px;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    background: transparent;
    border: none;
}}

QCheckBox::indicator:unchecked {{
    image: url("{ASSET_PATHS['checkbox_unchecked']}");
}}

QCheckBox::indicator:unchecked:hover {{
    image: url("{ASSET_PATHS['checkbox_hover']}");
}}

QCheckBox::indicator:checked {{
    image: url("{ASSET_PATHS['checkbox_checked']}");
}}

QCheckBox::indicator:checked:hover {{
    image: url("{ASSET_PATHS['checkbox_checked']}");
}}
"""
