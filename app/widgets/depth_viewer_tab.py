"""
Depth Viewer & Hydraulic Oil Buoyancy System Tab Widget.
Features:
- Glider Outline Schematic with Left (Nose) and Right (Tail) Oil Chambers.
- Timing & State Machine:
  1. Initial (11.0s): Left (Nose) = 225 ml, Right (Tail) = 2.0 L
  2. Phase 1 (34.2s): Left (Nose) = 0 ml, Right (Tail) = 2.225 L
  3. Phase 2 (24.3s): Left (Nose) = 225 ml, Right (Tail) = 2.0 L
  4. Loops continuously every 58.5s with Cycle Count incrementing.
"""

import math
import time
from typing import Optional
from qtpy.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from qtpy.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient,
    QPainterPath, QFont
)
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from app.config import COLORS
from app.core.telemetry_model import TelemetryPacket


class GliderOilSchematicWidget(QWidget):
    """
    Realistic vector-rendered Glider Hydraulic Buoyancy Schematic.
    Features:
    - 2.225 Litre capacity graduated glass beakers for both Left (Nose) and Right (Tail).
    - Realistic fluid physics with dynamic surface meniscus waves and bubbling.
    - Glass hydraulic pipeline with continuous flowing fluid stream and velocity particles.
    - Central bi-directional hydraulic pump with rotating impeller and flow status.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 180)

        self.nose_ml: float = 225.0
        self.tail_l: float = 2.000
        self.target_nose_ml: float = 225.0
        self.target_tail_l: float = 2.000

        self.phase_name: str = "IDLE (WAITING FOR TELEMETRY)"
        self.phase_time_left: float = 0.0
        self.phase_progress: float = 0.0
        self.flow_direction: int = 0  # 0: None, 1: Left to Right, -1: Right to Left
        self.anim_tick: float = 0.0

    def reset(self):
        """Immediately resets fluid levels and status back to default initial state."""
        self.nose_ml = 225.0
        self.tail_l = 2.000
        self.target_nose_ml = 225.0
        self.target_tail_l = 2.000
        self.phase_name = "IDLE (WAITING FOR TELEMETRY)"
        self.phase_time_left = 0.0
        self.phase_progress = 0.0
        self.flow_direction = 0
        self.anim_tick = 0.0
        self.update()

    def update_state(self, nose_ml: float, tail_l: float, phase_name: str,
                     phase_time_left: float, phase_progress: float, flow_dir: int,
                     instant: bool = False):
        self.target_nose_ml = nose_ml
        self.target_tail_l = tail_l
        self.phase_name = phase_name
        self.phase_time_left = phase_time_left
        self.phase_progress = phase_progress
        self.flow_direction = flow_dir

        if instant:
            self.nose_ml = nose_ml
            self.tail_l = tail_l
        else:
            # Responsive visual fluid transition
            self.nose_ml += (self.target_nose_ml - self.nose_ml) * 0.35
            self.tail_l += (self.target_tail_l - self.tail_l) * 0.35
        self.anim_tick += 0.12
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()

        # 1. Background Container Card (with safety margins)
        card_rect = QRectF(6, 4, w - 12, h - 8)
        painter.setPen(QPen(QColor(COLORS['border']), 1.2))
        painter.setBrush(QBrush(QColor(COLORS['bg_card'])))
        painter.drawRoundedRect(card_rect, 8, 8)

        # 2. Dynamic Vertical Space Allocation
        status_bar_h = 26.0
        status_bar_y = card_rect.bottom() - status_bar_h - 6.0
        status_bar_w = card_rect.width() - 16.0
        status_bar_x = card_rect.left() + 8.0

        usable_top = card_rect.top() + 6.0
        usable_bottom = status_bar_y - 6.0
        usable_h = max(80.0, usable_bottom - usable_top)

        # 3. Dynamic Glider Hull Geometry
        hull_cx = w * 0.5
        hull_cy = usable_top + usable_h * 0.44
        hull_w = min(w * 0.84, 680.0)
        hull_h = min(80.0, max(46.0, usable_h * 0.38))

        hx = hull_cx - hull_w * 0.5
        hy = hull_cy - hull_h * 0.5

        # Draw Glider Fuselage Silhouette Path
        hull_path = QPainterPath()
        nose_rx = hx + 32
        hull_path.moveTo(nose_rx, hy)
        hull_path.cubicTo(hx - 20, hy + 5, hx - 20, hy + hull_h - 5, nose_rx, hy + hull_h)
        tail_x = hx + hull_w
        hull_path.lineTo(tail_x - 30, hy + hull_h * 0.85)
        hull_path.lineTo(tail_x, hy + hull_h * 0.65)
        hull_path.lineTo(tail_x, hy + hull_h * 0.35)
        hull_path.lineTo(tail_x - 30, hy + hull_h * 0.15)
        hull_path.lineTo(nose_rx, hy)
        hull_path.closeSubpath()

        # Wing & Tail Fin paths (scaled to fit usable height)
        wing_h = min(36.0, max(20.0, usable_h * 0.22))
        fin_h = min(32.0, max(18.0, usable_h * 0.19))

        wing_path = QPainterPath()
        wing_path.moveTo(hull_cx - 36, hy + 4)
        wing_path.lineTo(hull_cx - 62, hy - wing_h)
        wing_path.lineTo(hull_cx - 34, hy - wing_h)
        wing_path.lineTo(hull_cx + 10, hy + 4)
        wing_path.closeSubpath()

        fin_path = QPainterPath()
        fin_path.moveTo(tail_x - 42, hy + 12)
        fin_path.lineTo(tail_x - 28, hy - fin_h)
        fin_path.lineTo(tail_x - 10, hy - fin_h)
        fin_path.lineTo(tail_x - 18, hy + 16)
        fin_path.closeSubpath()

        # Draw Wings & Fins
        painter.setPen(QPen(QColor("#CBD5E1"), 1.4))
        painter.setBrush(QBrush(QColor("#F1F5F9")))
        painter.drawPath(wing_path)
        painter.drawPath(fin_path)

        # Draw Hull Body Fill & Outline
        hull_grad = QLinearGradient(hx, hy, hx, hy + hull_h)
        hull_grad.setColorAt(0.0, QColor("#FFFFFF"))
        hull_grad.setColorAt(0.4, QColor("#F8FAFC"))
        hull_grad.setColorAt(1.0, QColor("#E2E8F0"))
        painter.setBrush(QBrush(hull_grad))
        painter.setPen(QPen(QColor("#94A3B8"), 1.8))
        painter.drawPath(hull_path)

        # Hull Ring Accents
        painter.setPen(QPen(QColor("#CBD5E1"), 1.2, Qt.DashLine))
        painter.drawLine(int(hx + hull_w * 0.32), int(hy + 6), int(hx + hull_w * 0.32), int(hy + hull_h - 6))
        painter.drawLine(int(hx + hull_w * 0.68), int(hy + 6), int(hx + hull_w * 0.68), int(hy + hull_h - 6))

        # 4. Hydraulic Connecting Pipeline & Fluid Stream
        tank_w = min(56.0, max(40.0, hull_w * 0.085))
        tank_h = min(68.0, max(42.0, usable_h * 0.36))
        nose_tank_x = hx + 38
        nose_tank_y = hull_cy - tank_h * 0.5
        tail_tank_x = hx + hull_w - 48 - tank_w
        tail_tank_y = hull_cy - tank_h * 0.5

        pipe_y = hull_cy
        pipe_x1 = nose_tank_x + tank_w
        pipe_x2 = tail_tank_x

        self._draw_hydraulic_pipeline(painter, pipe_x1, pipe_x2, pipe_y, hull_cx)

        # 5. Left Oil Chamber (Nose Side - 2.225 L Capacity, Current: nose_ml)
        self._draw_oil_chamber(
            painter, nose_tank_x, nose_tank_y, tank_w, tank_h,
            curr_val_ml=self.nose_ml, max_val_ml=2225.0,
            label="NOSE (LEFT)", is_left=True
        )

        # 6. Right Oil Chamber (Tail Side - 2.225 L Capacity, Current: tail_l * 1000)
        self._draw_oil_chamber(
            painter, tail_tank_x, tail_tank_y, tank_w, tank_h,
            curr_val_ml=self.tail_l * 1000.0, max_val_ml=2225.0,
            label="TAIL (RIGHT)", is_left=False
        )

        # 7. Bottom Phase Status Bar (inside card_rect)
        self._draw_phase_status_bar(painter, status_bar_x, status_bar_y, status_bar_w, status_bar_h)

    def _draw_hydraulic_pipeline(self, painter: QPainter, x1: float, x2: float, y: float, cx: float):
        """Draws realistic translucent hydraulic pipe with flowing liquid stream and central pump."""
        pipe_len = x2 - x1
        if pipe_len <= 10:
            return

        # 1. Outer Pipe Metallic/Glass Sleeve
        sleeve_rect = QRectF(x1, y - 5, pipe_len, 10)
        pipe_grad = QLinearGradient(x1, y - 5, x1, y + 5)
        pipe_grad.setColorAt(0.0, QColor("#64748B"))
        pipe_grad.setColorAt(0.3, QColor("#E2E8F0"))
        pipe_grad.setColorAt(0.7, QColor("#CBD5E1"))
        pipe_grad.setColorAt(1.0, QColor("#475569"))
        painter.setPen(QPen(QColor("#475569"), 1.0))
        painter.setBrush(QBrush(pipe_grad))
        painter.drawRoundedRect(sleeve_rect, 2.5, 2.5)

        # 2. Inner Fluid Core
        core_rect = QRectF(x1 + 1, y - 3.0, pipe_len - 2, 6)
        fluid_grad = QLinearGradient(x1, y - 3.0, x1, y + 3.0)
        fluid_grad.setColorAt(0.0, QColor("#FEF08A"))
        fluid_grad.setColorAt(0.5, QColor("#F59E0B"))
        fluid_grad.setColorAt(1.0, QColor("#B45309"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(fluid_grad))
        painter.drawRect(core_rect)

        # 3. Dynamic Flowing Fluid Particles & Streamlines
        if self.flow_direction != 0:
            num_particles = 12
            for i in range(num_particles):
                shift = (self.anim_tick * 0.18 * self.flow_direction + (i / num_particles)) % 1.0
                if shift < 0:
                    shift += 1.0
                px = x1 + 10 + shift * (pipe_len - 20)

                streak_len = 14.0
                tail_x = px - streak_len if self.flow_direction > 0 else px + streak_len
                
                streak_grad = QLinearGradient(tail_x, y, px, y)
                streak_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
                streak_grad.setColorAt(1.0, QColor(255, 255, 255, 220))
                painter.setPen(QPen(QBrush(streak_grad), 1.8, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(QPointF(tail_x, y), QPointF(px, y))

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawEllipse(QPointF(px, y), 1.6, 1.6)

        # 4. Central Bi-Directional Hydraulic Micro-Pump Unit
        pump_r = 15
        pump_rect = QRectF(cx - pump_r, y - pump_r, pump_r * 2, pump_r * 2)

        flange_grad = QRadialGradient(cx, y, pump_r)
        flange_grad.setColorAt(0.0, QColor("#F8FAFC"))
        flange_grad.setColorAt(0.7, QColor("#CBD5E1"))
        flange_grad.setColorAt(1.0, QColor("#475569"))
        painter.setPen(QPen(QColor("#334155"), 1.5))
        painter.setBrush(QBrush(flange_grad))
        painter.drawEllipse(pump_rect)

        glass_r = 10
        glass_rect = QRectF(cx - glass_r, y - glass_r, glass_r * 2, glass_r * 2)
        painter.setPen(QPen(QColor("#64748B"), 0.8))
        painter.setBrush(QBrush(QColor("#D97706" if self.flow_direction != 0 else "#94A3B8")))
        painter.drawEllipse(glass_rect)

        blade_angle = (self.anim_tick * 15.0 * self.flow_direction) if self.flow_direction != 0 else 0.0
        painter.setPen(QPen(QColor("#FFFFFF"), 1.8, Qt.SolidLine, Qt.RoundCap))
        for b_idx in range(4):
            rad = math.radians(blade_angle + b_idx * 90)
            bx = cx + math.cos(rad) * (glass_r - 2)
            by = y + math.sin(rad) * (glass_r - 2)
            painter.drawLine(QPointF(cx, y), QPointF(bx, by))

        painter.setBrush(QBrush(QColor("#1E293B")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, y), 2.5, 2.5)

        # Pump Flow Direction Badge (Above Pump)
        font_pump = QFont("Segoe UI", 7, QFont.Bold)
        painter.setFont(font_pump)
        if self.flow_direction == 1:
            flow_label = "PUMPING NOSE → TAIL (11.72 ml/s)"
            painter.setPen(QPen(QColor(COLORS['accent_yellow'])))
        elif self.flow_direction == -1:
            flow_label = "PUMPING TAIL → NOSE (9.26 ml/s)"
            painter.setPen(QPen(QColor(COLORS['accent_yellow'])))
        else:
            flow_label = "HYDRAULIC PUMP: STANDBY"
            painter.setPen(QPen(QColor(COLORS['text_secondary'])))
        
        painter.drawText(QRectF(cx - 110, y - pump_r - 15, 220, 13), Qt.AlignCenter, flow_label)

    def _draw_oil_chamber(self, painter: QPainter, x: float, y: float, w: float, h: float,
                          curr_val_ml: float, max_val_ml: float, label: str, is_left: bool):
        """Draws realistic graduated cylindrical glass beaker with accurate 2.225 L scaling and fluid waves."""
        # 1. Beaker Outer Glass Cylinder
        tank_rect = QRectF(x, y, w, h)
        glass_grad = QLinearGradient(x, y, x + w, y)
        glass_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        glass_grad.setColorAt(0.1, QColor(241, 245, 249, 210))
        glass_grad.setColorAt(0.9, QColor(241, 245, 249, 210))
        glass_grad.setColorAt(1.0, QColor(255, 255, 255, 240))

        painter.setPen(QPen(QColor("#475569"), 1.6))
        painter.setBrush(QBrush(glass_grad))
        painter.drawRoundedRect(tank_rect, 5, 5)

        # Top Collar Lip
        lip_rect = QRectF(x - 2, y - 2, w + 4, 4)
        painter.setPen(QPen(QColor("#64748B"), 1.0))
        painter.setBrush(QBrush(QColor("#F1F5F9")))
        painter.drawRoundedRect(lip_rect, 2, 2)

        # 2. Fluid Fill Calculation (Accurate proportional ratio relative to 2.225 L max capacity)
        ratio = max(0.0, min(1.0, curr_val_ml / max_val_ml))
        fluid_max_h = h - 6
        fill_h = fluid_max_h * ratio
        fill_y = y + h - 3 - fill_h

        # 3. Render Hydraulic Oil Fluid Body with Dynamic Meniscus Wave
        if fill_h > 1.2:
            fluid_path = QPainterPath()
            fluid_left = x + 2.5
            fluid_right = x + w - 2.5
            fluid_bottom = y + h - 3

            wave_amp = 1.2 if self.flow_direction != 0 else 0.0
            wave_pts = 8
            dx = (fluid_right - fluid_left) / wave_pts

            fluid_path.moveTo(fluid_left, fill_y)
            for step in range(1, wave_pts + 1):
                wx = fluid_left + step * dx
                phase = self.anim_tick * 4.0 + (step * 0.8) if self.flow_direction != 0 else 0.0
                wy = fill_y + math.sin(phase) * wave_amp
                fluid_path.lineTo(wx, wy)

            fluid_path.lineTo(fluid_right, fluid_bottom)
            fluid_path.lineTo(fluid_left, fluid_bottom)
            fluid_path.closeSubpath()

            oil_grad = QLinearGradient(x, fill_y, x, fluid_bottom)
            oil_grad.setColorAt(0.0, QColor("#FBBF24"))
            oil_grad.setColorAt(0.3, QColor("#F59E0B"))
            oil_grad.setColorAt(0.7, QColor("#D97706"))
            oil_grad.setColorAt(1.0, QColor("#92400E"))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(oil_grad))
            painter.drawPath(fluid_path)

            painter.setPen(QPen(QColor(255, 255, 255, 200), 1.4))
            meniscus_path = QPainterPath()
            meniscus_path.moveTo(fluid_left + 1, fill_y)
            for step in range(1, wave_pts + 1):
                wx = fluid_left + step * dx
                phase = self.anim_tick * 4.0 + (step * 0.8) if self.flow_direction != 0 else 0.0
                wy = fill_y + math.sin(phase) * wave_amp
                meniscus_path.lineTo(wx, wy)
            painter.drawPath(meniscus_path)

            if self.flow_direction != 0:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(255, 255, 255, 130)))
                for b_i in range(2):
                    b_phase = (self.anim_tick * 0.4 + b_i * 0.5) % 1.0
                    b_x = fluid_left + 6 + (b_i * 16)
                    b_y = fluid_bottom - (fill_h * b_phase)
                    if b_y > fill_y + 2:
                        painter.drawEllipse(QPointF(b_x, b_y), 1.0, 1.0)

        # 4. Glass Reflection Vertical Streak
        painter.setPen(QPen(QColor(255, 255, 255, 110), 1.5))
        painter.drawLine(int(x + 6), int(y + 3), int(x + 6), int(y + h - 5))

        # 5. Scientific Measurement Graduation Tick Marks
        painter.setPen(QPen(QColor("#64748B"), 0.8))
        font_tick = QFont("Segoe UI", 5, QFont.Bold)
        painter.setFont(font_tick)

        ticks = [
            (2225.0, "2.2L", True),
            (2000.0, "2.0L", False),
            (1500.0, "1.5L", False),
            (1000.0, "1.0L", False),
            (500.0, "0.5L", False),
            (225.0, "0.2L", True),
        ]

        for val_ml, tick_lbl, is_major in ticks:
            t_ratio = val_ml / 2225.0
            gy = y + h - 3 - (fluid_max_h * t_ratio)
            tick_len = 5 if is_major else 3
            
            if is_left:
                painter.drawLine(int(x + w - 2 - tick_len), int(gy), int(x + w - 2), int(gy))
            else:
                painter.drawLine(int(x + 2), int(gy), int(x + 2 + tick_len), int(gy))

        # 6. Title Label (Above Beaker)
        painter.setPen(QPen(QColor(COLORS['text_secondary'])))
        font_title = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font_title)
        if is_left:
            painter.drawText(QRectF(x - 40, y - 26, w + 80, 16), Qt.AlignCenter, label)
        else:
            painter.drawText(QRectF(x - 50, y - 26, w + 90, 16), Qt.AlignCenter, label)

        # 7. Value & Capacity Readout (Below Beaker)
        font_val = QFont("Consolas", 10, QFont.Bold)
        painter.setFont(font_val)
        painter.setPen(QPen(QColor(COLORS['text_primary'])))

        if is_left:
            val_str = f"{curr_val_ml:.0f} ml"
        else:
            val_str = f"{(curr_val_ml / 1000.0):.3f} L"

        painter.drawText(QRectF(x - 40, y + h + 4, w + 80, 16), Qt.AlignCenter, val_str)

        font_cap = QFont("Segoe UI", 7)
        painter.setFont(font_cap)
        painter.setPen(QPen(QColor(COLORS['text_secondary'])))
        painter.drawText(QRectF(x - 40, y + h + 18, w + 80, 14), Qt.AlignCenter, "Max: 2.225 L")

    def _draw_phase_status_bar(self, painter: QPainter, bar_x: float, bar_y: float, bar_w: float, bar_h: float):
        """Draws the bottom status bar securely inside the available container area."""
        # Container
        painter.setPen(QPen(QColor(COLORS['border']), 1.0))
        painter.setBrush(QBrush(QColor("#F8FAFC")))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 5, 5)

        # Progress fill
        if self.phase_progress > 0:
            prog_w = max(4.0, (bar_w - 4) * min(1.0, self.phase_progress))
            prog_grad = QLinearGradient(bar_x, bar_y, bar_x + prog_w, bar_y)
            prog_grad.setColorAt(0.0, QColor("#FEF3C7"))
            prog_grad.setColorAt(1.0, QColor("#FDE68A"))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(prog_grad))
            painter.drawRoundedRect(QRectF(bar_x + 2, bar_y + 2, prog_w, bar_h - 4), 4, 4)

        # Phase Text & Timer
        painter.setPen(QPen(QColor(COLORS['text_primary'])))
        font = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font)

        status_text = f"STATUS: {self.phase_name}"
        painter.drawText(QRectF(bar_x + 10, bar_y, bar_w * 0.6, bar_h), Qt.AlignVCenter | Qt.AlignLeft, status_text)

        if self.phase_time_left > 0:
            timer_text = f"REMAINING: {self.phase_time_left:.1f} s"
        else:
            timer_text = "STANDBY"

        painter.setPen(QPen(QColor(COLORS['accent_yellow'])))
        painter.drawText(QRectF(bar_x + bar_w * 0.6, bar_y, bar_w * 0.4 - 10, bar_h), Qt.AlignVCenter | Qt.AlignRight, timer_text)


class DepthViewerTabWidget(QFrame):
    """
    Dedicated Depth Viewer Tab Widget with Glider Hydraulic Oil Schematic
    and Cycle Count Display.
    """
    cycle_count_changed = Signal(int)
    vbe_state_changed = Signal(float, float)  # nose_ml, tail_l

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DepthViewerCard")

        self._first_packet_time: Optional[float] = None
        self._is_active: bool = False
        self._cycle_count: int = 0
        self.current_nose_ml: float = 225.0
        self.current_tail_l: float = 2.000

        # Fast 50ms timer for smooth fluid and timeline animation
        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self._on_tick)

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 6, 10, 6)
        root_layout.setSpacing(6)

        # 1. Header Bar with Cycle Count Header
        header_row = QHBoxLayout()
        header_row.setSpacing(6)

        bar = QFrame()
        bar.setFixedWidth(3)
        bar.setFixedHeight(12)
        bar.setStyleSheet(f"background-color: {COLORS['accent_yellow']}; border-radius: 1px;")

        title_label = QLabel("DEPTH VIEWER - HYDRAULIC BUOYANCY SYSTEM")
        title_label.setObjectName("CardTitle")

        header_row.addWidget(bar)
        header_row.addWidget(title_label)
        header_row.addStretch()
        root_layout.addLayout(header_row)

        # 2. Top Summary Row: Cycle Count Card + Telemetry Cards
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # Big Cycle Count Display Card
        card_cycle = QFrame()
        card_cycle.setFixedHeight(68)
        card_cycle.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        lay_cycle = QVBoxLayout(card_cycle)
        lay_cycle.setContentsMargins(14, 4, 14, 4)
        lay_cycle.setSpacing(1)

        lbl_c_title = QLabel("CYCLE COUNT")
        lbl_c_title.setAlignment(Qt.AlignCenter)
        lbl_c_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.2px;
                border: none;
                background: transparent;
            }}
        """)
        lay_cycle.addWidget(lbl_c_title)

        self.lbl_count = QLabel("0")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        self.lbl_count.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent_yellow']};
                font-size: 30px;
                font-weight: 800;
                font-family: 'Segoe UI', 'SF Pro Display', 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                border: none;
                background: transparent;
            }}
        """)
        lay_cycle.addWidget(self.lbl_count)
        top_row.addWidget(card_cycle, 1)

        # Left Chamber Stats Card
        self.card_left_stat = self._create_stat_card("LEFT (NOSE) VOLUME", "225 ml", "Capacity: 2.225 L")
        top_row.addWidget(self.card_left_stat, 1)

        # Right Chamber Stats Card
        self.card_right_stat = self._create_stat_card("RIGHT (TAIL) VOLUME", "2.000 L", "Capacity: 2.225 L")
        top_row.addWidget(self.card_right_stat, 1)

        root_layout.addLayout(top_row)

        # 3. Main Interactive Glider Outline & Oil Tank Schematic
        self.schematic = GliderOilSchematicWidget(self)
        root_layout.addWidget(self.schematic, 1)

    def _create_stat_card(self, title: str, init_val: str, subtext: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(68)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(1)

        lbl_t = QLabel(title)
        lbl_t.setAlignment(Qt.AlignCenter)
        lbl_t.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.8px;
                border: none;
                background: transparent;
            }}
        """)
        lay.addWidget(lbl_t)

        lbl_v = QLabel(init_val)
        lbl_v.setObjectName("StatValue")
        lbl_v.setAlignment(Qt.AlignCenter)
        lbl_v.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 20px;
                font-weight: 800;
                font-family: 'Consolas', 'SF Mono', monospace;
                border: none;
                background: transparent;
            }}
        """)
        lay.addWidget(lbl_v)

        lbl_s = QLabel(subtext)
        lbl_s.setAlignment(Qt.AlignCenter)
        lbl_s.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 9px;
                border: none;
                background: transparent;
            }}
        """)
        lay.addWidget(lbl_s)

        return card

    def start_simulation(self):
        """Starts or restarts the depth viewer hydraulic simulation from t=0."""
        self._is_active = True
        self._first_packet_time = time.time()
        self._cycle_count = 0
        self.lbl_count.setText("0")
        self.card_left_stat.findChild(QLabel, "StatValue").setText("225.0 ml")
        self.card_right_stat.findChild(QLabel, "StatValue").setText("2.000 L")
        self.schematic.update_state(
            nose_ml=225.0, tail_l=2.000,
            phase_name="INITIAL CALIBRATION (11.0s)",
            phase_time_left=11.0, phase_progress=0.0, flow_dir=0,
            instant=True
        )
        if not self._timer.isActive():
            self._timer.start()
        self._on_tick()

    def on_telemetry_received(self, packet: TelemetryPacket):
        """Called whenever a valid telemetry packet arrives."""
        if not self._is_active:
            self.start_simulation()

    def set_connected_state(self, is_connected: bool, is_receiving: bool = False):
        """Resets or activates simulation based on connection and telemetry state."""
        if not is_connected or not is_receiving:
            self.reset()
        elif is_receiving and not self._is_active:
            self.start_simulation()

    def reset(self):
        """Resets the cycle counter to zero, resets fluid levels, and stops timer."""
        self._is_active = False
        self._first_packet_time = None
        self._cycle_count = 0
        if self._timer.isActive():
            self._timer.stop()
        self.lbl_count.setText("0")
        self.card_left_stat.findChild(QLabel, "StatValue").setText("225 ml")
        self.card_right_stat.findChild(QLabel, "StatValue").setText("2.000 L")
        self.schematic.reset()


    def _on_tick(self):
        """Calculates active phase, continuous oil transfer levels, and cycle count."""
        if not self._is_active or self._first_packet_time is None:
            self.reset()
            return

        elapsed = time.time() - self._first_packet_time

        # 1. Timing State Machine with 4-Phase Hydraulic Cycle (68.5s total per cycle):
        # 0. Initial Calibration: 11.0s (Nose: 225ml, Tail: 2.000L, Static)
        # 1. Phase 1 (Dive): 19.2s (Nose 225ml -> 0ml, Tail 2.000L -> 2.225L, Flow: Left -> Right)
        # 2. Phase 2 (Stable): 15.0s (Nose: 0ml, Tail: 2.225L, Static)
        # 3. Phase 3 (Climb): 24.3s (Nose 0ml -> 225ml, Tail 2.225L -> 2.000L, Flow: Right -> Left)
        # 4. Phase 4 (State): 10.0s (Nose: 225ml, Tail: 2.000L, Static)
        # Total repeating loop: 19.2 + 15.0 + 24.3 + 10.0 = 68.5s
        if elapsed < 11.0:
            # Initial 11s Calibration phase
            nose_ml = 225.0
            tail_l = 2.000
            new_count = 0
            phase_name = "INITIAL CALIBRATION (11.0s)"
            phase_time_left = max(0.0, 11.0 - elapsed)
            phase_prog = elapsed / 11.0
            flow_dir = 0
        else:
            cycle_elapsed = (elapsed - 11.0) % 68.5
            new_count = int((elapsed - 11.0) / 68.5)

            if cycle_elapsed < 19.2:
                # Phase 1 (Dive): 19.2s (225ml -> 0ml, 2.000L -> 2.225L)
                prog = max(0.0, min(1.0, cycle_elapsed / 19.2))
                nose_ml = 225.0 * (1.0 - prog)
                tail_l = 2.000 + 0.225 * prog
                phase_name = "PHASE 1: DIVE - TRANSFERRING TO TAIL (19.2s)"
                phase_time_left = max(0.0, 19.2 - cycle_elapsed)
                phase_prog = prog
                flow_dir = 1  # Left -> Right
            elif cycle_elapsed < 34.2:
                # Phase 2 (Stable): 15.0s (0ml, 2.225L Static)
                prog = max(0.0, min(1.0, (cycle_elapsed - 19.2) / 15.0))
                nose_ml = 0.0
                tail_l = 2.225
                phase_name = "PHASE 2: STABLE DIVE (15.0s)"
                phase_time_left = max(0.0, 34.2 - cycle_elapsed)
                phase_prog = prog
                flow_dir = 0  # Static
            elif cycle_elapsed < 58.5:
                # Phase 3 (Climb): 24.3s (0ml -> 225ml, 2.225L -> 2.000L)
                prog = max(0.0, min(1.0, (cycle_elapsed - 34.2) / 24.3))
                nose_ml = 225.0 * prog
                tail_l = 2.225 - 0.225 * prog
                phase_name = "PHASE 3: CLIMB - TRANSFERRING TO NOSE (24.3s)"
                phase_time_left = max(0.0, 58.5 - cycle_elapsed)
                phase_prog = prog
                flow_dir = -1  # Right -> Left
            else:
                # Phase 4 (State): 10.0s (225ml, 2.000L Static)
                prog = max(0.0, min(1.0, (cycle_elapsed - 58.5) / 10.0))
                nose_ml = 225.0
                tail_l = 2.000
                phase_name = "PHASE 4: SURFACE STATE (10.0s)"
                phase_time_left = max(0.0, 68.5 - cycle_elapsed)
                phase_prog = prog
                flow_dir = 0  # Static

        # Update Cycle Counter
        if new_count != self._cycle_count:
            self._cycle_count = new_count
            self.lbl_count.setText(str(self._cycle_count))
            self.cycle_count_changed.emit(self._cycle_count)

        self.current_nose_ml = nose_ml
        self.current_tail_l = tail_l
        self.vbe_state_changed.emit(nose_ml, tail_l)

        # Update Quick Cards with continuous real-time readout
        self.card_left_stat.findChild(QLabel, "StatValue").setText(f"{nose_ml:.1f} ml")
        self.card_right_stat.findChild(QLabel, "StatValue").setText(f"{tail_l:.3f} L")

        # Update Graphic Schematic
        self.schematic.update_state(
            nose_ml=nose_ml,
            tail_l=tail_l,
            phase_name=phase_name,
            phase_time_left=phase_time_left,
            phase_progress=phase_prog,
            flow_dir=flow_dir
        )

