"""
Modern Glass-Cockpit Primary Flight Display (PFD) / Attitude Indicator Widget.
High-fidelity aerospace/subsea artificial horizon with bank angle arc, precision pitch ladder,
custom boresight reticle, metallic bezel, and digital HUD telemetry cards.
"""

import math
from qtpy.QtCore import Qt, QPointF, QRectF
from qtpy.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGridLayout
)
from qtpy.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QPolygonF,
    QLinearGradient, QRadialGradient, QConicalGradient
)
from app.config import COLORS


class AttitudeHorizonDial(QWidget):
    """
    High-fidelity Glass-Cockpit Artificial Horizon Sphere.
    Features realistic spherical gradient, bank angle graduation ticks,
    aerospace HUD pitch ladder, and precision glowing boresight reticle.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0.0
        self.pitch = 0.0
        self.setMinimumSize(130, 130)

    def set_attitude(self, roll: float, pitch: float):
        self.roll = roll
        self.pitch = pitch
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        w = self.width()
        h = self.height()
        size = min(w, h) - 10
        center = QPointF(w / 2.0, h / 2.0)
        radius = size / 2.0

        if radius <= 10:
            return

        # 1. Outer Bezel & Shadow (Titanium / Slate Ring)
        bezel_thickness = max(4.0, radius * 0.08)
        inner_radius = radius - bezel_thickness

        # Outer bezel shadow / frame
        painter.setPen(Qt.NoPen)
        bezel_grad = QLinearGradient(0, center.y() - radius, 0, center.y() + radius)
        bezel_grad.setColorAt(0.0, QColor("#E2E8F0"))
        bezel_grad.setColorAt(0.5, QColor("#CBD5E1"))
        bezel_grad.setColorAt(1.0, QColor("#94A3B8"))
        painter.setBrush(QBrush(bezel_grad))
        painter.drawEllipse(center, radius, radius)

        # Inner bezel groove
        painter.setBrush(QBrush(QColor("#0F172A")))
        painter.drawEllipse(center, inner_radius + 1.0, inner_radius + 1.0)

        # 2. Circular Clipping Path for Artificial Horizon Sphere
        clip_path = QPainterPath()
        clip_path.addEllipse(center, inner_radius, inner_radius)
        painter.setClipPath(clip_path)

        # 3. Draw Rotated & Pitch-Shifted Horizon
        painter.save()
        painter.translate(center)
        painter.rotate(self.roll)

        # Pitch translation (clamped to dial radius)
        pitch_scale = inner_radius / 45.0  # 45 deg fits comfortably in radius
        pitch_offset = max(-inner_radius * 0.88, min(inner_radius * 0.88, self.pitch * pitch_scale))

        # --- SKY GRADIENT (Upper Oceanic Aero Blue) ---
        sky_grad = QLinearGradient(0, -inner_radius * 2 + pitch_offset, 0, pitch_offset)
        sky_grad.setColorAt(0.0, QColor("#1D4ED8"))   # Deep cobalt
        sky_grad.setColorAt(0.6, QColor("#2563EB"))   # Vivid royal blue
        sky_grad.setColorAt(1.0, QColor("#38BDF8"))   # Bright atmospheric horizon cyan
        painter.fillRect(QRectF(-inner_radius * 2.5, -inner_radius * 2.5 + pitch_offset, inner_radius * 5, inner_radius * 2.5), QBrush(sky_grad))

        # --- GROUND GRADIENT (Lower Subsea Abyss / Earth Ochre) ---
        ground_grad = QLinearGradient(0, pitch_offset, 0, inner_radius * 2 + pitch_offset)
        ground_grad.setColorAt(0.0, QColor("#0F766E"))  # Deep teal ocean floor transition
        ground_grad.setColorAt(0.3, QColor("#0F172A"))  # Deep oceanic abyss
        ground_grad.setColorAt(1.0, QColor("#020617"))  # Midnight dark floor
        painter.fillRect(QRectF(-inner_radius * 2.5, pitch_offset, inner_radius * 5, inner_radius * 2.5), QBrush(ground_grad))

        # --- HORIZON LINE (Crisp Glowing White / Cyan) ---
        horizon_glow = QPen(QColor(255, 255, 255, 100), 4.0)
        painter.setPen(horizon_glow)
        painter.drawLine(QPointF(-inner_radius * 2, pitch_offset), QPointF(inner_radius * 2, pitch_offset))

        horizon_pen = QPen(QColor("#FFFFFF"), 2.0)
        painter.setPen(horizon_pen)
        painter.drawLine(QPointF(-inner_radius * 2, pitch_offset), QPointF(inner_radius * 2, pitch_offset))

        # --- PITCH LADDER BARS ---
        ladder_font = QFont("Consolas", 7, QFont.Bold)
        ladder_font.setStyleHint(QFont.Monospace)
        painter.setFont(ladder_font)

        for deg in [-60, -50, -40, -30, -20, -10, 10, 20, 30, 40, 50, 60]:
            y_pos = pitch_offset - (deg * pitch_scale)
            if abs(y_pos) < inner_radius * 0.92:
                is_major = (deg % 10 == 0 and abs(deg) <= 30)
                bar_len = inner_radius * (0.42 if is_major else 0.26)
                hook_h = 3.5 if deg > 0 else -3.5  # Hooks point toward horizon

                if deg > 0:
                    # Solid white ladder for sky
                    p_pen = QPen(QColor("#FFFFFF"), 1.4)
                    painter.setPen(p_pen)
                    painter.drawLine(QPointF(-bar_len / 2, y_pos), QPointF(bar_len / 2, y_pos))
                    painter.drawLine(QPointF(-bar_len / 2, y_pos), QPointF(-bar_len / 2, y_pos + hook_h))
                    painter.drawLine(QPointF(bar_len / 2, y_pos), QPointF(bar_len / 2, y_pos + hook_h))
                else:
                    # Dashed / broken white-cyan ladder for ground
                    p_pen = QPen(QColor("#E2E8F0"), 1.3, Qt.DashLine)
                    painter.setPen(p_pen)
                    painter.drawLine(QPointF(-bar_len / 2, y_pos), QPointF(bar_len / 2, y_pos))
                    p_solid = QPen(QColor("#E2E8F0"), 1.3)
                    painter.setPen(p_solid)
                    painter.drawLine(QPointF(-bar_len / 2, y_pos), QPointF(-bar_len / 2, y_pos + hook_h))
                    painter.drawLine(QPointF(bar_len / 2, y_pos), QPointF(bar_len / 2, y_pos + hook_h))

                # Pitch Degree Labels
                text = str(abs(deg))
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(QRectF(bar_len / 2 + 3, y_pos - 6, 18, 12), Qt.AlignLeft | Qt.AlignVCenter, text)
                painter.drawText(QRectF(-bar_len / 2 - 21, y_pos - 6, 18, 12), Qt.AlignRight | Qt.AlignVCenter, text)

        painter.restore()

        # 4. Bank Angle Scale (Roll Arc & Graduation Marks)
        painter.save()
        painter.translate(center)

        arc_r = inner_radius - 6.0
        arc_pen = QPen(QColor(255, 255, 255, 140), 1.2)
        painter.setPen(arc_pen)

        # Draw Roll Ticks at 0, +-10, +-20, +-30, +-45, +-60
        roll_angles = [0, -10, 10, -20, 20, -30, 30, -45, 45, -60, 60]
        for ang in roll_angles:
            painter.save()
            painter.rotate(ang)
            is_cardinal = (ang in (0, -30, 30, -60, 60))
            is_45 = (abs(ang) == 45)
            
            if is_cardinal:
                painter.setPen(QPen(QColor("#FBBF24" if ang == 0 else "#FFFFFF"), 1.8))
                painter.drawLine(QPointF(0, -inner_radius), QPointF(0, -inner_radius + 7))
            elif is_45:
                # Triangle index for 45 deg
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                tri_45 = QPolygonF([
                    QPointF(0, -inner_radius + 1),
                    QPointF(-2.5, -inner_radius + 5),
                    QPointF(2.5, -inner_radius + 5)
                ])
                painter.drawPolygon(tri_45)
            else:
                painter.setPen(QPen(QColor(255, 255, 255, 180), 1.0))
                painter.drawLine(QPointF(0, -inner_radius), QPointF(0, -inner_radius + 4))

            painter.restore()

        # Glass Spherical Vignette / Radial Highlight
        glass_grad = QRadialGradient(QPointF(-inner_radius * 0.3, -inner_radius * 0.3), inner_radius * 1.5)
        glass_grad.setColorAt(0.0, QColor(255, 255, 255, 45))
        glass_grad.setColorAt(0.6, QColor(255, 255, 255, 0))
        glass_grad.setColorAt(1.0, QColor(0, 0, 0, 80))
        painter.setBrush(QBrush(glass_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(0, 0), inner_radius, inner_radius)

        painter.restore()

        # 5. Remove clipping for Static HUD Boresight Reticle & Roll Pointer
        painter.setClipPath(QPainterPath())

        painter.save()
        painter.translate(center)

        # Top Roll Index Marker (Static Yellow Triangle)
        painter.setPen(QPen(QColor("#B45309"), 1.0))
        painter.setBrush(QBrush(QColor("#F59E0B")))
        roll_tri = QPolygonF([
            QPointF(0, -inner_radius + 1),
            QPointF(-4.5, -inner_radius + 9),
            QPointF(4.5, -inner_radius + 9)
        ])
        painter.drawPolygon(roll_tri)

        # --- BORESIGHT AIRCRAFT RETICLE (Glowing Industrial Amber) ---
        # Glow layer
        glow_pen = QPen(QColor(245, 158, 11, 80), 4.5)
        painter.setPen(glow_pen)
        painter.drawLine(QPointF(-inner_radius * 0.55, 0), QPointF(-inner_radius * 0.20, 0))
        painter.drawLine(QPointF(-inner_radius * 0.20, 0), QPointF(-inner_radius * 0.20, 5))
        painter.drawLine(QPointF(inner_radius * 0.20, 0), QPointF(inner_radius * 0.55, 0))
        painter.drawLine(QPointF(inner_radius * 0.20, 0), QPointF(inner_radius * 0.20, 5))

        # Sharp foreground reticle
        reticle_pen = QPen(QColor("#F59E0B"), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(reticle_pen)
        # Left Wing
        painter.drawLine(QPointF(-inner_radius * 0.55, 0), QPointF(-inner_radius * 0.20, 0))
        painter.drawLine(QPointF(-inner_radius * 0.20, 0), QPointF(-inner_radius * 0.20, 5))
        # Right Wing
        painter.drawLine(QPointF(inner_radius * 0.20, 0), QPointF(inner_radius * 0.55, 0))
        painter.drawLine(QPointF(inner_radius * 0.20, 0), QPointF(inner_radius * 0.20, 5))
        
        # Center Reference Dot
        painter.setBrush(QBrush(QColor("#F59E0B")))
        painter.setPen(QPen(QColor("#78350F"), 1.0))
        painter.drawEllipse(QPointF(0, 0), 2.5, 2.5)

        painter.restore()


class DigitalAttitudeCard(QFrame):
    """Sleek dark-glass HUD card for a single axis readout (Roll, Pitch, Yaw)."""

    def __init__(self, title: str, unit: str = "°", accent_color: str = "#2563EB", parent=None):
        super().__init__(parent)
        self.setObjectName("DigitalAttitudeCard")
        self.setStyleSheet(f"""
            QFrame#DigitalAttitudeCard {{
                background-color: #F8FAFC;
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {accent_color};
                border-radius: 4px;
                padding: 2px 4px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(1)

        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;")

        self.lbl_val = QLabel(f"+0.00 {unit}")
        self.lbl_val.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 13px;
            font-weight: 700;
            font-family: 'Consolas', 'Roboto Mono', monospace;
        """)

        lay.addWidget(self.lbl_title)
        lay.addWidget(self.lbl_val)

    def set_value(self, text: str):
        self.lbl_val.setText(text)


class AttitudeIndicatorWidget(QFrame):
    """
    Combined Attitude Indicator Card with Modern Horizon Dial and High-Tech
    HUD axis readouts for White Theme.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AttitudeIndicatorCard")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Header Title: ATTITUDE INDICATOR with Amber indicator bar
        header_row = QHBoxLayout()
        header_row.setSpacing(6)
        
        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title_label = QLabel("ATTITUDE INDICATOR")
        title_label.setObjectName("CardTitle")

        header_row.addWidget(bar)
        header_row.addWidget(title_label)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Body Layout: Dial on Left, Sleek HUD Cards on Right
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)

        self.dial = AttitudeHorizonDial(self)
        body_layout.addWidget(self.dial, 1)

        # Digital Telemetry Cards
        readouts_layout = QVBoxLayout()
        readouts_layout.setAlignment(Qt.AlignVCenter)
        readouts_layout.setSpacing(5)

        self.card_roll = DigitalAttitudeCard("Roll", "°", COLORS["trace_roll"], self)
        self.card_pitch = DigitalAttitudeCard("Pitch", "°", COLORS["trace_pitch"], self)
        self.card_yaw = DigitalAttitudeCard("Yaw", "°", COLORS["trace_yaw"], self)

        readouts_layout.addWidget(self.card_roll)
        readouts_layout.addWidget(self.card_pitch)
        readouts_layout.addWidget(self.card_yaw)

        body_layout.addLayout(readouts_layout)
        layout.addLayout(body_layout)

    def update_telemetry(self, roll: float, pitch: float, yaw: float):
        """Update dial and digital cards."""
        self.dial.set_attitude(roll, pitch)
        self.card_roll.set_value(f"{roll:+.2f} °")
        self.card_pitch.set_value(f"{pitch:+.2f} °")
        self.card_yaw.set_value(f"{yaw:.2f} °")

