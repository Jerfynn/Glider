"""
Dive Power & Energy Analytics Dashboard Tab Widget.
Displays real-time electrical power (W) and timestamp-integrated energy (Wh)
for vehicle Dive In and Dive Out segments, peak power, and maximum energy.
Clean White / Light Theme with high-contrast typography and industrial amber accents.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
)

from app.config import COLORS
from app.core.dive_analytics import DiveAnalyticsEngine


class AnalyticsTabWidget(QFrame):
    """
    Dedicated Dive Power & Energy Analytics Tab.
    Displays:
      1. DIVES (Total & Completed count)
      2. POWER (Dive In, Dive Out, Max Power Consumed for One Dive)
      3. ENERGY (Dive In, Dive Out, Max Energy Consumed for One Dive)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnalyticsTabCard")
        self.engine = DiveAnalyticsEngine()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header Title
        header = QHBoxLayout()
        header.setSpacing(8)
        accent = QFrame()
        accent.setFixedSize(4, 16)
        accent.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 2px;")
        
        title = QLabel("DIVE POWER & ENERGY ANALYTICS")
        title.setObjectName("CardTitle")
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {COLORS['text_primary']}; letter-spacing: 0.5px;")
        
        header.addWidget(accent)
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        # 1. DIVES SECTION
        dives_box = QFrame()
        dives_box.setObjectName("DivesBox")
        dives_box.setStyleSheet(f"""
            QFrame#DivesBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        dives_layout = QVBoxLayout(dives_box)
        dives_layout.setContentsMargins(18, 14, 18, 14)
        dives_layout.setSpacing(10)

        dives_header = QHBoxLayout()
        dives_header.setSpacing(8)
        dives_accent = QFrame()
        dives_accent.setFixedSize(3, 12)
        dives_accent.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")
        dives_lbl = QLabel("DIVES")
        dives_lbl.setStyleSheet(f"font-size: 12px; font-weight: 800; letter-spacing: 0.5px; color: {COLORS['text_primary']};")
        dives_header.addWidget(dives_accent)
        dives_header.addWidget(dives_lbl)
        dives_header.addStretch()
        dives_layout.addLayout(dives_header)

        dives_grid = QGridLayout()
        dives_grid.setHorizontalSpacing(14)

        # Completed Dives Card
        card_completed = self._create_metric_card("COMPLETED DIVES", "0")
        self.lbl_completed_dives = card_completed.findChild(QLabel, "MetricValue")
        dives_grid.addWidget(card_completed, 0, 0)

        # Total Dives Card
        card_total = self._create_metric_card("TOTAL DIVES", "0")
        self.lbl_total_dives = card_total.findChild(QLabel, "MetricValue")
        dives_grid.addWidget(card_total, 0, 1)

        # Active Dive Status Card
        card_status = self._create_metric_card("DIVE STATUS", "IDLE (NEUTRAL)")
        self.lbl_dive_status = card_status.findChild(QLabel, "MetricValue")
        self.lbl_dive_status.setStyleSheet(f"color: #16A34A; font-size: 16px; font-weight: 800; font-family: 'Consolas', monospace; border: 0; background: transparent;")
        dives_grid.addWidget(card_status, 0, 2)

        dives_layout.addLayout(dives_grid)
        root.addWidget(dives_box)

        # 2. POWER SECTION
        power_box = QFrame()
        power_box.setObjectName("PowerBox")
        power_box.setStyleSheet(f"""
            QFrame#PowerBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        power_layout = QVBoxLayout(power_box)
        power_layout.setContentsMargins(18, 14, 18, 14)
        power_layout.setSpacing(10)

        p_header = QHBoxLayout()
        p_header.setSpacing(8)
        p_accent = QFrame()
        p_accent.setFixedSize(3, 12)
        p_accent.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")
        p_lbl = QLabel("POWER")
        p_lbl.setStyleSheet(f"font-size: 12px; font-weight: 800; letter-spacing: 0.5px; color: {COLORS['text_primary']};")
        p_header.addWidget(p_accent)
        p_header.addWidget(p_lbl)
        p_header.addStretch()
        power_layout.addLayout(p_header)

        power_grid = QGridLayout()
        power_grid.setHorizontalSpacing(14)

        card_p_in = self._create_metric_card("1. DIVE IN", "— W")
        self.lbl_power_in = card_p_in.findChild(QLabel, "MetricValue")
        power_grid.addWidget(card_p_in, 0, 0)

        card_p_out = self._create_metric_card("2. DIVE OUT", "— W")
        self.lbl_power_out = card_p_out.findChild(QLabel, "MetricValue")
        power_grid.addWidget(card_p_out, 0, 1)

        card_p_max = self._create_metric_card("3. MAX POWER CONSUMED FOR ONE DIVE", "— W")
        self.lbl_power_max = card_p_max.findChild(QLabel, "MetricValue")
        power_grid.addWidget(card_p_max, 0, 2)

        power_layout.addLayout(power_grid)
        root.addWidget(power_box)

        # 3. ENERGY SECTION
        energy_box = QFrame()
        energy_box.setObjectName("EnergyBox")
        energy_box.setStyleSheet(f"""
            QFrame#EnergyBox {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        energy_layout = QVBoxLayout(energy_box)
        energy_layout.setContentsMargins(18, 14, 18, 14)
        energy_layout.setSpacing(10)

        e_header = QHBoxLayout()
        e_header.setSpacing(8)
        e_accent = QFrame()
        e_accent.setFixedSize(3, 12)
        e_accent.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")
        e_lbl = QLabel("ENERGY")
        e_lbl.setStyleSheet(f"font-size: 12px; font-weight: 800; letter-spacing: 0.5px; color: {COLORS['text_primary']};")
        e_header.addWidget(e_accent)
        e_header.addWidget(e_lbl)
        e_header.addStretch()
        energy_layout.addLayout(e_header)

        energy_grid = QGridLayout()
        energy_grid.setHorizontalSpacing(14)

        card_e_in = self._create_metric_card("1. DIVE IN", "— Wh")
        self.lbl_energy_in = card_e_in.findChild(QLabel, "MetricValue")
        energy_grid.addWidget(card_e_in, 0, 0)

        card_e_out = self._create_metric_card("2. DIVE OUT", "— Wh")
        self.lbl_energy_out = card_e_out.findChild(QLabel, "MetricValue")
        energy_grid.addWidget(card_e_out, 0, 1)

        card_e_max = self._create_metric_card("3. MAX ENERGY CONSUMED FOR ONE DIVE", "— Wh")
        self.lbl_energy_max = card_e_max.findChild(QLabel, "MetricValue")
        energy_grid.addWidget(card_e_max, 0, 2)

        energy_layout.addLayout(energy_grid)
        root.addWidget(energy_box)

        root.addStretch(1)

    def _create_metric_card(self, title: str, default_val: str) -> QFrame:
        card = QFrame()
        card.setObjectName("AnalyticsMetricCard")
        card.setStyleSheet(f"""
            QFrame#AnalyticsMetricCard {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        lbl_title = QLabel(title.upper())
        lbl_title.setObjectName("MetricTitle")
        lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px; font-weight: 700; letter-spacing: 0.4px; border: 0; background: transparent;")

        lbl_val = QLabel(default_val)
        lbl_val.setObjectName("MetricValue")
        lbl_val.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 800; font-family: 'Consolas', monospace; border: 0; background: transparent;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        return card

    def update_telemetry(self, packet, **_unused):
        """Processes incoming telemetry packet safely."""
        try:
            self.engine.update(packet)
            self._refresh_ui()
        except Exception:
            pass

    def _fmt(self, val, unit=""):
        if val is None:
            return "—"
        return f"{val:.2f}{unit}"

    def _refresh_ui(self):
        metrics = self.engine.get_summary_metrics()

        # Dives
        self.lbl_completed_dives.setText(str(metrics["completed_dives"]))
        self.lbl_total_dives.setText(str(metrics["total_dives"]))
        
        if self.engine.active_segment:
            direction_str = "DIVE IN" if self.engine.active_segment.direction == "IN" else "DIVE OUT"
            self.lbl_dive_status.setText(f"ACTIVE ({direction_str})")
            self.lbl_dive_status.setStyleSheet(f"color: {COLORS['accent_yellow']}; font-size: 16px; font-weight: 800; font-family: 'Consolas', monospace; border: 0; background: transparent;")
        else:
            self.lbl_dive_status.setText("IDLE (NEUTRAL)")
            self.lbl_dive_status.setStyleSheet(f"color: #16A34A; font-size: 16px; font-weight: 800; font-family: 'Consolas', monospace; border: 0; background: transparent;")

        # Power
        self.lbl_power_in.setText(self._fmt(metrics["power_dive_in"], " W"))
        self.lbl_power_out.setText(self._fmt(metrics["power_dive_out"], " W"))
        self.lbl_power_max.setText(self._fmt(metrics["max_power_one_dive"], " W"))

        # Energy
        self.lbl_energy_in.setText(self._fmt(metrics["energy_dive_in"], " Wh"))
        self.lbl_energy_out.setText(self._fmt(metrics["energy_dive_out"], " Wh"))
        self.lbl_energy_max.setText(self._fmt(metrics["max_energy_one_dive"], " Wh"))
