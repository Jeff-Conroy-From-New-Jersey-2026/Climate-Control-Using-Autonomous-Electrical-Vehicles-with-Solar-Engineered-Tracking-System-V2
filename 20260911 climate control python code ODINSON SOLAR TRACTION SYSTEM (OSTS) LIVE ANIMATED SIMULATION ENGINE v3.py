import json
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd

# ==============================================================================
# ODINSON SOLAR TRACTION SYSTEM (OSTS) LIVE ANIMATED SIMULATION ENGINE
# By Jeff Conroy | global HealthCare Analytics ~ just an LLC...
### just wait until you see what we do to Cancer next, son s0n!
# Provided under Open Source MIT License
# "If a part moves, it breaks. If it catches wind, it steals your energy."
# ==============================================================================

class VehicleSpecs:
    def __init__(self):
        self.base_efficiency_wh_mi = 250.0  # Baseline EV consumption (Wh/mi)

class OSTS_1_Mechanical:
    """ OSTS-1: Mechanical Active Tracking Protocol """
    def __init__(self):
        self.name = "OSTS-1 (Mechanical Servos)"
        self.pv_efficiency = 0.38
        self.surface_area_ft2 = 75.0
        self.servo_power_draw_w = 250.0      # Continuous motor load tracking sun
        self.aero_drag_penalty_mult = 1.25   # +25% drag penalty from articulators & side mirrors
        self.shading_loss_factor = 0.50      # String topology shading collapse

class OSTS_2_SolidState:
    """ OSTS-2: Solid-State Structural + OP-DCS Mirror Deletion """
    def __init__(self):
        self.name = "OSTS-2 (Solid-State Mirrorless)"
        self.pv_efficiency = 0.42
        self.surface_area_ft2 = 78.5         # Extended solar skin from mirror removal
        self.camera_sensor_draw_w = 18.0     # Ultra-low OP-DCS camera draw
        self.aero_drag_penalty_mult = 0.89   # -11% drag drop vs OSTS-1
        self.shading_loss_factor = 0.92      # Distributed MPPT Matrix

# Initialize Architecture
specs = VehicleSpecs()
osts1 = OSTS_1_Mechanical()
osts2 = OSTS_2_SolidState()

# Global tracking arrays for the live animation
time_history = []
temp_history = []
irr_history = []
power_osts1_history = []
power_osts2_history = []

def fetch_live_weather_data():
    """ Fetches real-time temperature and solar radiation data from Open-Meteo API. """
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.69&longitude=-74.57&current=temperature_2m,direct_radiation,diffuse_radiation"
        req = urllib.request.urlopen(url, timeout=2)
        data = json.loads(req.read().decode('utf-8'))
        current = data.get('current', {})
        
        temp_c = current.get('temperature_2m', 22.0)
        direct_rad = current.get('direct_radiation', 0.0)
        diffuse_rad = current.get('diffuse_radiation', 0.0)
        total_irradiance = max(0.0, direct_rad + diffuse_rad)
        
        return temp_c, total_irradiance
    except Exception:
        # Fallback to simulated live telemetry if API is unreachable
        return None, None

def simulate_step(frame):
    """ Executes one live step of the OSTS comparative model. """
    hour = (frame / 300.0) * 24.0  # Map 300 frames to a 24-hour cycle
    
    # Try fetching live feed; fallback to dynamic mathematical solar curve
    temp_c, live_irr = fetch_live_weather_data()
    
    if live_irr is None or live_irr == 0.0:
        # Simulated daylight curve (6:00 AM to 6:00 PM)
        if 6.0 <= hour <= 18.0:
            solar_irr = 1000.0 * np.sin((hour - 6.0) * np.pi / 12.0)
        else:
            solar_irr = 0.0
        temp_c = 15.0 + 10.0 * np.sin((hour - 8.0) * np.pi / 12.0)
    else:
        solar_irr = live_irr

    # Dynamic Shading Simulation (overpass/tree shading from 10:00 to 12:00)
    shade_factor = 0.40 if (10.0 <= hour <= 12.0) else 1.0

    # --- OSTS-1 Calculation ---
    area_m2_1 = osts1.surface_area_ft2 * 0.092903
    tracking_boost = 1.40 if solar_irr > 50 else 1.0
    p_raw_1 = area_m2_1 * osts1.pv_efficiency * (solar_irr * tracking_boost)
    if shade_factor < 1.0:
        p_raw_1 *= osts1.shading_loss_factor
    p_net_1 = max(0, p_raw_1 - osts1.servo_power_draw_w) if solar_irr > 50 else 0.0

    # --- OSTS-2 Calculation ---
    area_m2_2 = osts2.surface_area_ft2 * 0.092903
    p_raw_2 = area_m2_2 * osts2.pv_efficiency * solar_irr
    if shade_factor < 1.0:
        p_raw_2 *= (shade_factor * osts2.shading_loss_factor)
    p_net_2 = max(0, p_raw_2 - osts2.camera_sensor_draw_w)

    return hour, temp_c, solar_irr, p_net_1 / 1000.0, p_net_2 / 1000.0

# Setup Plot Figure
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

def update(frame):
    """ Animation update callback loop. """
    hour, temp, solar, p1, p2 = simulate_step(frame)

    time_history.append(hour)
    temp_history.append(temp)
    irr_history.append(solar)
    power_osts1_history.append(p1)
    power_osts2_history.append(p2)

    ax1.cla()
    ax2.cla()

    # Left Axis: Power Generation (kW)
    ax1.plot(time_history, power_osts1_history, label='OSTS-1: Mechanical Servos (kW)', color='#e74c3c', linewidth=2, linestyle='--')
    ax1.plot(time_history, power_osts2_history, label='OSTS-2: Solid-State Mirrorless (kW)', color='#2ecc71', linewidth=2.5)
    ax1.set_xlabel("Time (Hour of Day)", fontweight='bold')
    ax1.set_ylabel("Net Power Generation (kW)", fontweight='bold', color='#2c3e50')
    ax1.set_xlim(0, 24)
    ax1.set_ylim(0, max(max(power_osts2_history, default=1.0) * 1.2, 3.0))
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Right Axis: Environmental Irradiance (W/m²)
    ax2.plot(time_history, irr_history, label='Solar Irradiance (W/m²)', color='orange', linestyle=':', alpha=0.5)
    ax2.set_ylabel("Irradiance (W/m²)", fontweight='bold', color='orange')
    ax2.set_ylim(0, 1200)

    # Combine Legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.title(f"OSTS Live Telemetry Stream — Time: {hour:.2f}h | Temp: {temp:.1f}°C | Solar: {solar:.0f} W/m²", fontweight='bold')

print("Rendering simulation animation...")
ani = FuncAnimation(fig, update, frames=300, interval=50, repeat=False)
ani.save("simulation.mp4", fps=20)
print("Animation successfully saved to simulation.mp4!")