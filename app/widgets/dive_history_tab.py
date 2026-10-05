"""
Dive Power & Energy History Tab Widget.
Presents a dedicated table and cycle history showing power calculations
and energy consumption from Cycle #1 onwards across all completed and active dives.
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton
)

from app.config import COLORS


class DiveHistoryTabWidget(QFrame):
    """
    Dedicated Cycle History Tab for Dive Power & Energy calculations from Cycle 1.
    Displays:
      - Historical table of all completed dive cycles (Cycle 1, Cycle 2, ...)
      - Dive In Max Power (W), Energy (Wh), Duration (s)
      - Dive Out Max Power (W), Energy (Wh), Duration (s)
      - Max Power for Dive (W)
      - Total Energy Consumed (Wh)
    """

    def __init__(self, analytics_engine, parent=None):
        super().__init__(parent)
        self.setObjectName("DiveHistoryTabCard")
        self.engine = analytics_engine

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Header Title
        header = QHBoxLayout()
        header.setSpacing(8)
        accent = QFrame()
        accent.setFixedSize(4, 16)
        accent.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 2px;")
        
        title = QLabel("DIVE CYCLE POWER & ENERGY HISTORY (FROM CYCLE 1)")
        title.setObjectName("CardTitle")
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {COLORS['text_primary']}; letter-spacing: 0.5px;")
        
        header.addWidget(accent)
        header.addWidget(title)
        header.addStretch()

        self.btn_refresh = QPushButton("↻ REFRESH TABLE")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedHeight(28)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 700;
                padding: 4px 12px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: #F8FAFC;
                border-color: {COLORS['border_highlight']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.btn_refresh.clicked.connect(self.refresh_table)
        header.addWidget(self.btn_refresh)

        root.addLayout(header)

        # Subtitle info banner
        self.lbl_info = QLabel("Tracking individual dive cycle power and energy consumption starting from the first cycle.")
        self.lbl_info.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-weight: 500;")
        root.addWidget(self.lbl_info)

        # Table Container Box
        table_box = QFrame()
        table_box.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        box_layout = QVBoxLayout(table_box)
        box_layout.setContentsMargins(1, 1, 1, 1)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Cycle",
            "Dive In Max (W)",
            "Dive In (Wh)",
            "Dive Out Max (W)",
            "Dive Out (Wh)",
            "Max Power (W)",
            "Total Energy (Wh)",
            "Duration (s)"
        ])
        
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                gridline-color: {COLORS['border']};
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 12px;
                border: none;
            }}
            QHeaderView::section {{
                background-color: #F1F5F9;
                color: {COLORS['text_primary']};
                font-weight: 700;
                font-size: 11px;
                padding: 6px 4px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 6px;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: #EFF6FF;
                color: #1E3A8A;
            }}
        """)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setDefaultAlignment(Qt.AlignCenter)
        self.table.verticalHeader().setVisible(False)

        box_layout.addWidget(self.table)
        root.addWidget(table_box, 1)

        self.refresh_table()

    def update_telemetry(self, packet=None, **_kwargs):
        """Called whenever new telemetry packet arrives."""
        self.refresh_table()

    def refresh_table(self):
        """Populates the history table from the analytics engine."""
        history = getattr(self.engine, "history", [])
        active_dive = getattr(self.engine, "current_dive", None)
        active_segment = getattr(self.engine, "active_segment", None)

        total_rows = len(history)
        has_active_row = (active_dive is not None or active_segment is not None)
        if has_active_row:
            total_rows += 1

        self.table.setRowCount(total_rows)

        # Populate completed dives (Cycle 1, Cycle 2, ...)
        for row_idx, rec in enumerate(history):
            dive_id = f"Cycle #{rec.get('dive_id', row_idx + 1)}"
            in_power = f"{rec.get('dive_in_max_power', 0.0):.2f} W"
            in_energy = f"{rec.get('dive_in_energy', 0.0):.2f} Wh"
            out_power = f"{rec.get('dive_out_max_power', 0.0):.2f} W"
            out_energy = f"{rec.get('dive_out_energy', 0.0):.2f} Wh"
            max_power = f"{rec.get('max_power', 0.0):.2f} W"
            total_energy = f"{rec.get('total_energy', 0.0):.2f} Wh"
            duration = f"{rec.get('total_duration', 0.0):.1f} s"

            vals = [dive_id, in_power, in_energy, out_power, out_energy, max_power, total_energy, duration]
            for col_idx, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        # Populate current ongoing cycle if active
        if has_active_row:
            active_idx = len(history)
            cycle_num = f"Cycle #{active_idx + 1} (Active)"

            cur_in = active_dive.get("in") if active_dive else None
            cur_out = active_dive.get("out") if active_dive else None

            # Calculate live in
            in_p = None
            in_e = None
            if active_segment and active_segment.direction == "IN":
                active_powers = [p for _, p in active_segment.samples if p is not None]
                in_p = max(active_powers) if active_powers else 0.0
                in_e = active_segment.energy_wh
            elif cur_in:
                in_p = cur_in.get("max_power")
                in_e = cur_in.get("energy_wh")

            # Calculate live out
            out_p = None
            out_e = None
            if active_segment and active_segment.direction == "OUT":
                active_powers = [p for _, p in active_segment.samples if p is not None]
                out_p = max(active_powers) if active_powers else 0.0
                out_e = active_segment.energy_wh
            elif cur_out:
                out_p = cur_out.get("max_power")
                out_e = cur_out.get("energy_wh")

            str_in_p = f"{in_p:.2f} W" if in_p is not None else "—"
            str_in_e = f"{in_e:.2f} Wh" if in_e is not None else "—"
            str_out_p = f"{out_p:.2f} W" if out_p is not None else "—"
            str_out_e = f"{out_e:.2f} Wh" if out_e is not None else "—"

            cand_p = [p for p in (in_p, out_p) if p is not None]
            str_max_p = f"{max(cand_p):.2f} W" if cand_p else "—"

            cand_e = [e for e in (in_e, out_e) if e is not None]
            str_tot_e = f"{sum(cand_e):.2f} Wh" if cand_e else "—"

            active_vals = [cycle_num, str_in_p, str_in_e, str_out_p, str_out_e, str_max_p, str_tot_e, "In Progress..."]
            for col_idx, val in enumerate(active_vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(Qt.darkYellow)
                self.table.setItem(active_idx, col_idx, item)

        self.lbl_info.setText(
            f"Showing {len(history)} completed cycle(s)" +
            (f" + Cycle #{len(history) + 1} actively in progress." if has_active_row else ".")
        )
