"""
Timestamp-based Dive Power and Energy Analytics Engine.
Calculates electrical power P(W) = V(V) * I(A), trapezoidal energy integration (Wh),
detects PWM 1500 neutral transitions (Dive In > 1500, Dive Out < 1500),
and pairs Dive In + Dive Out segments into complete dives.
"""

import csv
import math
import os
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


NEUTRAL_PWM = 1500
DEFAULT_DEADBAND = 5  # [1495, 1505] is treated as neutral/idle


def _finite(value) -> Optional[float]:
    """Safely parses a float and checks for finite value."""
    if value is None:
        return None
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError, OverflowError):
        return None


@dataclass
class Segment:
    """Represents an active Dive In or Dive Out motor segment."""
    direction: str  # "IN" or "OUT"
    start_time: float
    samples: List[tuple] = field(default_factory=list)  # (timestamp, power_w)
    energy_wh: float = 0.0
    last_power: Optional[float] = None
    last_time: Optional[float] = None

    def add_sample(self, timestamp: float, power: Optional[float]):
        """Adds a power sample and updates trapezoidal energy integration."""
        if (self.last_time is not None and timestamp > self.last_time 
                and self.last_power is not None and power is not None):
            dt = timestamp - self.last_time
            self.energy_wh += ((self.last_power + power) / 2.0) * (dt / 3600.0)
        
        if power is not None:
            self.samples.append((timestamp, power))
        self.last_time = timestamp
        self.last_power = power

    def finish(self, timestamp: float) -> Dict[str, Any]:
        """Finalizes segment and returns structured metrics dictionary."""
        powers = [p for _, p in self.samples if p is not None]
        duration = max(0.0, timestamp - self.start_time)
        avg_power = sum(powers) / len(powers) if powers else 0.0
        max_power = max(powers) if powers else 0.0
        min_power = min(powers) if powers else 0.0
        start_power = powers[0] if powers else 0.0
        end_power = powers[-1] if powers else 0.0

        return {
            "direction": self.direction,
            "start_time": self.start_time,
            "end_time": timestamp,
            "duration": duration,
            "average_power": avg_power,
            "max_power": max_power,
            "min_power": min_power,
            "start_power": start_power,
            "end_power": end_power,
            "energy_wh": self.energy_wh,
            "samples": list(self.samples)
        }


class DiveAnalyticsEngine:
    """
    Incremental dive state machine for vehicle power & energy analytics.
    Tracks sequential Complete Dives: Dive In (PWM > 1500) + Dive Out (PWM < 1500).
    """

    def __init__(self, log_dir: Optional[str] = None, deadband: int = DEFAULT_DEADBAND):
        self.deadband = max(0, int(deadband))
        if not log_dir:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            log_dir = os.path.join(base_dir, "logs")
        self.log_dir = os.path.abspath(log_dir)

        self.history: List[Dict[str, Any]] = []
        self.current_dive: Optional[Dict[str, Any]] = None
        self.active_segment: Optional[Segment] = None
        self.last_time: Optional[float] = None
        self.last_power: Optional[float] = None
        self.total_energy_wh: float = 0.0

    def reset(self):
        """Resets all analytics history, active dive segments, and cumulative counters to 0."""
        self.history.clear()
        self.current_dive = None
        self.active_segment = None
        self.last_time = None
        self.last_power = None
        self.total_energy_wh = 0.0

    def is_neutral(self, pwm: int) -> bool:
        """Determines if motor PWM is within neutral deadband."""
        return abs(pwm - NEUTRAL_PWM) <= self.deadband

    def update(self, packet):
        """Processes an incoming telemetry packet incrementally."""
        timestamp = _finite(getattr(packet, "timestamp", None))
        if timestamp is None:
            timestamp = time.time()
        
        # Enforce monotonically non-decreasing timestamps
        if self.last_time is not None and timestamp <= self.last_time:
            timestamp = self.last_time + 0.001

        # Extract Voltage & Current safely
        voltage = _finite(getattr(packet, "battery_voltage", None))
        current = _finite(getattr(packet, "battery_current", None))

        # Calculate Power (W) = abs(V * I)
        power: Optional[float] = None
        if voltage is not None and current is not None:
            power = abs(voltage * current)

        # Extract Motor PWM
        raw_pwm = _finite(getattr(packet, "pwm", None))
        if raw_pwm is None:
            raw_pwm = NEUTRAL_PWM
        pwm = int(round(raw_pwm))

        # Total energy accumulation
        if (self.last_time is not None and self.last_power is not None 
                and power is not None and timestamp > self.last_time):
            dt = timestamp - self.last_time
            self.total_energy_wh += ((self.last_power + power) / 2.0) * (dt / 3600.0)

        # State Machine Transitions
        if self.active_segment is None:
            # Vehicle was IDLE. Check if starting active movement
            # User specification: DIVE IN is PWM < 1500, DIVE OUT is PWM > 1500
            if not self.is_neutral(pwm):
                direction = "IN" if pwm < NEUTRAL_PWM else "OUT"
                
                # Initialize new dive container if needed
                if self.current_dive is None:
                    dive_num = len(self.history) + 1
                    self.current_dive = {"dive": dive_num, "in": None, "out": None}
                elif direction == "IN" and self.current_dive.get("in") is not None and self.current_dive.get("out") is not None:
                    # Previous dive was full, start new dive
                    dive_num = len(self.history) + 1
                    self.current_dive = {"dive": dive_num, "in": None, "out": None}

                self.active_segment = Segment(direction=direction, start_time=timestamp)
                self.active_segment.add_sample(timestamp, power)
        else:
            # An active segment is running
            if self.is_neutral(pwm):
                # Vehicle returned to neutral boundary -> Close active segment
                segment = self.active_segment
                segment.add_sample(timestamp, power)
                metrics = segment.finish(timestamp)
                
                if segment.direction == "IN":
                    self.current_dive["in"] = metrics
                else:
                    self.current_dive["out"] = metrics
                
                self.active_segment = None
                self._check_dive_completion()
            else:
                current_dir = "IN" if pwm < NEUTRAL_PWM else "OUT"
                if current_dir != self.active_segment.direction:
                    # Direction reversed directly without neutral sample
                    segment = self.active_segment
                    segment.add_sample(timestamp, power)
                    metrics = segment.finish(timestamp)
                    if segment.direction == "IN":
                        self.current_dive["in"] = metrics
                    else:
                        self.current_dive["out"] = metrics
                    self._check_dive_completion()

                    if self.current_dive is None:
                        dive_num = len(self.history) + 1
                        self.current_dive = {"dive": dive_num, "in": None, "out": None}

                    self.active_segment = Segment(direction=current_dir, start_time=timestamp)
                    self.active_segment.add_sample(timestamp, power)
                else:
                    self.active_segment.add_sample(timestamp, power)

        self.last_time = timestamp
        self.last_power = power

    def _check_dive_completion(self):
        """Pairs Dive In and Dive Out to finalize a complete dive."""
        if not self.current_dive:
            return
        dive_in = self.current_dive.get("in")
        dive_out = self.current_dive.get("out")

        if dive_in is not None and dive_out is not None:
            # Both segments complete!
            in_wh = dive_in.get("energy_wh", 0.0)
            out_wh = dive_out.get("energy_wh", 0.0)
            total_wh = in_wh + out_wh

            in_max_p = dive_in.get("max_power", 0.0)
            out_max_p = dive_out.get("max_power", 0.0)
            max_power = max(in_max_p, out_max_p)

            record = {
                "dive_id": self.current_dive["dive"],
                "dive_in_start_time": dive_in["start_time"],
                "dive_in_end_time": dive_in["end_time"],
                "dive_out_start_time": dive_out["start_time"],
                "dive_out_end_time": dive_out["end_time"],
                "dive_in_duration": dive_in["duration"],
                "dive_out_duration": dive_out["duration"],
                "dive_in_average_power": dive_in["average_power"],
                "dive_in_max_power": dive_in["max_power"],
                "dive_in_min_power": dive_in["min_power"],
                "dive_in_start_power": dive_in["start_power"],
                "dive_in_end_power": dive_in["end_power"],
                "dive_in_energy": in_wh,
                "dive_out_average_power": dive_out["average_power"],
                "dive_out_max_power": dive_out["max_power"],
                "dive_out_min_power": dive_out["min_power"],
                "dive_out_start_power": dive_out["start_power"],
                "dive_out_end_power": dive_out["end_power"],
                "dive_out_energy": out_wh,
                "max_power": max_power,
                "total_energy": total_wh,
                "total_duration": dive_in["duration"] + dive_out["duration"]
            }

            self.history.append(record)
            self._persist_record(record)
            self.current_dive = None

    def _persist_record(self, record: Dict[str, Any]):
        """Appends completed dive record to persistent CSV log."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, "dive_power_analytics.csv")
            fields = list(record.keys())
            write_header = not os.path.exists(path) or os.path.getsize(path) == 0
            with open(path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                if write_header:
                    writer.writeheader()
                writer.writerow(record)
        except Exception:
            pass

    def get_summary_metrics(self) -> Dict[str, Any]:
        """
        Computes the exact dashboard analytics metrics for the current/latest cycle:
        - During Dive In: displays live Dive In power & energy.
        - During Idle (between Dive In and Dive Out): retains Dive In power & energy!
        - During Dive Out: displays retained Dive In power/energy AND live Dive Out power/energy.
        - Upon Complete Dive (Dive In + Dive Out): displays both segments and complete totals.
        - When the next cycle starts, it resets and starts clean for the new cycle!
        """
        completed_dives = len(self.history)
        total_dives = completed_dives
        if self.current_dive is not None or self.active_segment is not None:
            total_dives = completed_dives + 1

        # Check latest context: current ongoing dive or last completed dive
        cur_in = self.current_dive.get("in") if self.current_dive else None
        cur_out = self.current_dive.get("out") if self.current_dive else None
        
        last_record = self.history[-1] if self.history else None

        # Determine Dive In Power & Energy
        dive_in_power = None
        dive_in_energy = None
        if self.active_segment and self.active_segment.direction == "IN":
            active_powers = [p for _, p in self.active_segment.samples if p is not None]
            dive_in_power = max(active_powers) if active_powers else None
            dive_in_energy = self.active_segment.energy_wh
        elif cur_in:
            dive_in_power = cur_in.get("max_power")
            dive_in_energy = cur_in.get("energy_wh")
        elif last_record and not self.active_segment and not self.current_dive:
            # Show completed cycle metrics until a new cycle starts
            dive_in_power = last_record.get("dive_in_max_power")
            dive_in_energy = last_record.get("dive_in_energy")

        # Determine Dive Out Power & Energy
        dive_out_power = None
        dive_out_energy = None
        if self.active_segment and self.active_segment.direction == "OUT":
            active_powers = [p for _, p in self.active_segment.samples if p is not None]
            dive_out_power = max(active_powers) if active_powers else None
            dive_out_energy = self.active_segment.energy_wh
        elif cur_out:
            dive_out_power = cur_out.get("max_power")
            dive_out_energy = cur_out.get("energy_wh")
        elif last_record and not self.active_segment and not self.current_dive:
            # Show completed cycle metrics until a new cycle starts
            dive_out_power = last_record.get("dive_out_max_power")
            dive_out_energy = last_record.get("dive_out_energy")

        # Max Power Consumed for One Dive
        max_power_candidates = [p for p in (dive_in_power, dive_out_power) if p is not None]
        max_power_one_dive = max(max_power_candidates) if max_power_candidates else None

        # Max Energy Consumed for One Dive (sum of Dive In + Dive Out for complete dive, or ongoing sum)
        energy_candidates = [e for e in (dive_in_energy, dive_out_energy) if e is not None]
        max_energy_one_dive = sum(energy_candidates) if energy_candidates else None

        return {
            "total_dives": total_dives,
            "completed_dives": completed_dives,
            "is_active": self.active_segment is not None or self.current_dive is not None,
            "power_dive_in": dive_in_power,
            "power_dive_out": dive_out_power,
            "max_power_one_dive": max_power_one_dive,
            "energy_dive_in": dive_in_energy,
            "energy_dive_out": dive_out_energy,
            "max_energy_one_dive": max_energy_one_dive,
        }
