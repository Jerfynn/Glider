# GliderView - Underwater Glider Telemetry & 3D Orientation Viewer

**GliderView** is a desktop telemetry ground control station and 3D vehicle orientation viewer built with **QtPy**, **PyOpenGL**, and **PyQtGraph**.

---

## 10 Telemetry Channels

The software processes strictly the following **10 telemetry parameters**:

| # | Field Name | Description | Units / Type |
|---|------------|-------------|--------------|
| 1 | **Roll** | Vehicle bank angle | Degrees (°) |
| 2 | **Pitch** | Dive / Climb angle | Degrees (°) |
| 3 | **Yaw** | Compass orientation | Degrees (0 - 360°) |
| 4 | **Depth** | Ocean water depth | Meters (m) |
| 5 | **Temperature** | Water temperature | Celsius (°C) |
| 6 | **Pressure** | Hydrostatic pressure | Bar |
| 7 | **Battery Voltage** | Pack voltage | Volts (V) |
| 8 | **Battery Current** | Current draw | Amperes (A) |
| 9 | **Battery SoC** | State of Charge | Percentage (%) |
| 10| **Battery SoH** | State of Health | Percentage (%) |

---

## Serial Telemetry Data Formats

Send data via serial COM port using any of these standard formats:

### 1. Standard CSV (Recommended)
Send the 10 comma-separated values terminated with `\r\n` or `\n`:
```text
<roll>,<pitch>,<yaw>,<depth>,<temperature>,<pressure>,<battery_voltage>,<battery_current>,<battery_soc>,<battery_soh>\r\n
```

**Example Serial Line:**
```text
12.42,-5.21,184.73,42.7,18.4,5.18,14.82,1.25,85.0,98.2
```

### 2. JSON Format
```json
{
  "roll": 12.42,
  "pitch": -5.21,
  "yaw": 184.73,
  "depth": 42.7,
  "temp": 18.4,
  "pressure": 5.18,
  "voltage": 14.82,
  "current": 1.25,
  "soc": 85.0,
  "soh": 98.2
}
```

### 3. Tagged Key-Value Format
```text
R:12.42,P:-5.21,Y:184.73,D:42.7,T:18.4,PR:5.18,BV:14.82,BC:1.25,SOC:85.0,SOH:98.2
```

---

## How to Run the Software

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the application:
   ```bash
   python main.py
   ```
3. Test using **Simulation / Demo Mode** or connect directly to your hardware COM port.
