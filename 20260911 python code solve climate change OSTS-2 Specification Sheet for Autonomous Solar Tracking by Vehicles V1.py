import numpy as np
import matplotlib.pyplot as plt

# Configuration Variables
#  Open Source Code Detailing OSTS-2 Specification Sheet for Autonomous Solar Tracking by Vehicles (cars in North America; could easily be for rocket ships in space travel)
##   By Jeff Conroy ~ Global HC Analytics LLC Founder & Managing Principal
###   Released on GitHub - Under the MIT License - more to come! :)

LATITUDE = 39.0 # North America
AVG_INSOLATION = 6.2 # kWh/m^2/day (Standard average)
SYSTEM_EFFICIENCY_LOSSES = 0.85 # 15% system loss (wiring, conversion)

# Vehicle OSTS-2 Spec Sheet (Static Metamaterial/Zoned Skin)
ROOF_AREA_M2 = 2.0 # Effective top-facing roof capture area (m^2)
HOOD_AREA_M2 = 1.0
OTHER_PANELS_M2 = 4.0 # (doors, pillars, trunk, zoned)

SOLAR_EFFICIENCY_ROOF = 0.35 # (35% High-efficiency multi-junction on primary sun-facing)
SOLAR_EFFICIENCY_HOOD = 0.28 # (Zoned skin for durability)
SOLAR_EFFICIENCY_OTHER = 0.15 # (Lower, durable, less perpendicular skin)
VEHICLE_VE_EFFICIENCY = 0.20 # Efficiency of drivetrain (kWh/mile) (Low drag EV)

# Helios Dynamic Canopy OSTS-2 (Stationary)
CANOPY_AREA_M2 = 15.0 # Total collection area on dynamic canopy
CANOPY_PANEL_EFFICIENCY = 0.22 # Standard, cost-effective high-yield panels
RESONANT_LOSS = 0.95 # 5% loss across wireless transmission

# Thermal Harvesting OSTS-2 (Hybrid TEG/TPV)
# Capturing waste heat from battery and road-effect IR.
THE_GAIN_MILES_DAY = 7.0

def simulate_day():
    # Model 1: Vehicle On-The-Go Generation
    # (Simplified: assumes peak insolation only on optimal top-facing surfaces)
    
    # Roof/Hood: Primary Generation (Static LSC focus)
    active_m2_vehicle = ROOF_AREA_M2 + HOOD_AREA_M2
    daily_insolation_kwh = AVG_INSOLATION * active_m2_vehicle
    
    gen_primary = (daily_insolation_kwh * SOLAR_EFFICIENCY_ROOF * SYSTEM_EFFICIENCY_LOSSES)
    gen_other = (AVG_INSOLATION * OTHER_PANELS_M2 * SOLAR_EFFICIENCY_OTHER * SYSTEM_EFFICIENCY_LOSSES)
    
    total_vehicle_kwh = gen_primary + gen_other
    range_on_the_go = total_vehicle_kwh / VEHICLE_VE_EFFICIENCY
    
    # Model 2: Helios Dynamic Canopy (Stationary)
    # Optimal tilt on curved structure maximizes insolation.
    effective_canopy_insolation = AVG_INSOLATION * 1.15 # Curved canopy optimization bonus
    daily_insolation_canopy_kwh = effective_canopy_insolation * CANOPY_AREA_M2
    
    total_canopy_kwh = (daily_insolation_canopy_kwh * CANOPY_PANEL_EFFICIENCY * 
                         SYSTEM_EFFICIENCY_LOSSES * RESONANT_LOSS)
    range_static = total_canopy_kwh / VEHICLE_VE_EFFICIENCY
    
    # Model 3: Thermal Harvesting
    total_the_gain_kwh = THE_GAIN_MILES_DAY * VEHICLE_VE_EFFICIENCY # Convert back to energy
    
    # Summary of Output
    print(f"--- OSTS-2 System Performance Simulation ---")
    print(f"Latitude: {LATITUDE}° N | Average Insolation: {AVG_INSOLATION} kWh/m^2/day")
    print(f"")
    print(f"1. On-the-Go Vehicle Generation (Static LSC):")
    print(f"   Effective Generation Area: {active_m2_vehicle + OTHER_PANELS_M2} m^2 (Full Skin)")
    print(f"   Total Daily Energy Harvested: {total_vehicle_kwh:.2f} kWh")
    print(f"   Projected Daily Range Gain: {range_on_the_go:.1f} miles")
    print(f"")
    print(f"2. Helios Dynamic Canopy Generation (Stationary):")
    print(f"   Collection Area: {CANOPY_AREA_M2} m^2")
    print(f"   Total Daily Energy Harvested (via Wireless): {total_canopy_kwh:.2f} kWh")
    print(f"   Projected Daily Range Gain: {range_static:.1f} miles")
    print(f"")
    print(f"3. UTPV/TEG Hybrid Thermal Harvesting:")
    print(f"   Projected Daily Range Gain (Continuous): {THE_GAIN_MILES_DAY:.1f} miles")
    print(f"")
    print(f"=== Total Daily Grid Independence: {range_on_the_go + range_static + THE_GAIN_MILES_DAY:.1f} miles ===")

    # Visualization of the Day's Generation Curve (On-The-Go)
    time_steps = np.linspace(6, 18, 100) # 6 AM to 6 PM
    
    # Assume bell curve for insolation (peaking at noon)
    insolation_curve = AVG_INSOLATION * (np.sin((time_steps - 6) * np.pi / 12))**2
    
    # Dynamic output assumes LSC (top) is optimal, and skin panels are scaled by cosine loss.
    vehicle_output_curve = (
        (ROOF_AREA_M2 + HOOD_AREA_M2) * SOLAR_EFFICIENCY_ROOF * insolation_curve * SYSTEM_EFFICIENCY_LOSSES
        + (OTHER_PANELS_M2) * SOLAR_EFFICIENCY_OTHER * insolation_curve * SYSTEM_EFFICIENCY_LOSSES
    )
    
    # Plotting for something pretty
    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, vehicle_output_curve, label='Vehicle OSTS-2 (On-The-Go) Production (kWh)', color='#4CAF50', linewidth=2.5)
    plt.fill_between(time_steps, vehicle_output_curve, alpha=0.3, color='#8BC34A')
    
    # Reference lines for total needed
    plt.axhline(y=total_vehicle_kwh/12, color='#555', linestyle='--', label=f'Total Avg Daily On-The-Go ({total_vehicle_kwh:.2f} kWh)')
    
    plt.title('OSTS-2 Vehicle Solar Energy Generation Curve (Summer Day, NA)', fontsize=14)
    plt.xlabel('Time of Day (Hour)', fontsize=12)
    plt.ylabel('Solar Power Output (kW)', fontsize=12)
    plt.xticks(np.arange(6, 19, 1))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulate_day()