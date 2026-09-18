########################################################################&&&%%@!~~~~~------------------------------------------....
# Odinson Solar Tracking System (OSTS) V0.31 - Released September 18th, 2026
##
# Open Source via MIT License | Field-tested on Tesla Model Y Platform
###
#
## If you like this? Then donate to Jeff's Walk to Cure Pediatric Cancers for the amazing ALSF Here:
#####
######## https://www.alexslemonade.org/2026/global-hc-analytics--celgene-reunion-alsf-fundraising-team
###
#### Don't get stingy on cancer now, TSLA and LCID and all of you Ford and SEDG Nuts! =)
#################################################&&&%%@!~~~~~------------------------------------------....

import math
import time
from datetime import datetime


class SolarTracker:
    """
    Simulates dual-axis solar positioning and calculates orientation alignment efficiency.
    """
    def __init__(self, latitude: float = 40.67):
        """
        :param latitude: Host vehicle latitude (default: Bernards/Edison, NJ region ~40.67°N).
        """
        self.latitude = latitude
        self.panel_tilt = 0.0     # Panel tilt angle relative to horizon (0° = flat on hood)
        self.panel_azimuth = 180.0 # Facing South by default (180°)

    def calculate_sun_position(self, hour_of_day: float) -> tuple[float, float]:
        """
        Calculates approximate solar elevation and azimuth based on hour of day.
        
        :param hour_of_day: Decimal hour (0.0 to 24.0).
        :return: Tuple of (solar_elevation_deg, solar_azimuth_deg).
        """
        # Simplified solar elevation model peaking at local solar noon (12:00 PM)
        solar_declination = 0.0  # Vernal/Autumnal equinox baseline approximation
        hour_angle = (hour_of_day - 12.0) * 15.0  # 15 degrees per hour
        
        lat_rad = math.radians(self.latitude)
        dec_rad = math.radians(solar_declination)
        ha_rad = math.radians(hour_angle)
        
        # Elevation angle calculation
        sin_elevation = (math.sin(lat_rad) * math.sin(dec_rad) + 
                         math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad))
        elevation_deg = math.degrees(math.asin(max(-1.0, min(1.0, sin_elevation))))
        
        # Azimuth angle calculation (simplified 180° sweep across daytime)
        azimuth_deg = 180.0 + hour_angle
        
        return max(0.0, elevation_deg), azimuth_deg

    def calculate_alignment_efficiency(self, solar_elevation: float) -> float:
        """
        Calculates cosine loss factor based on panel tilt versus solar elevation angle.
        
        :return: Efficiency factor between 0.0 and 1.0.
        """
        if solar_elevation <= 0:
            return 0.0
            
        optimal_tilt = 90.0 - solar_elevation
        incidence_error = abs(optimal_tilt - self.panel_tilt)
        
        # Cosine attenuation model for off-axis solar capture
        efficiency = math.cos(math.radians(incidence_error))
        return max(0.0, efficiency)

    def track_sun(self, solar_elevation: float) -> str:
        """Adjusts panel tilt actuator to track optimal solar elevation."""
        if solar_elevation <= 0:
            target_tilt = 0.0
        else:
            target_tilt = 90.0 - solar_elevation
            
        delta = target_tilt - self.panel_tilt
        self.panel_tilt = target_tilt
        return f"Actuator adjusted tilt by {delta:+.1f}° -> Current Tilt: {self.panel_tilt:.1f}°"


class PowerStation:
    """
    Represents an auxiliary battery system integrated with active solar harvesting telemetry.
    """
    def __init__(self, name: str, capacity_wh: float, efficiency: float = 0.9):
        self.name = name
        self.capacity_wh = capacity_wh
        self.current_wh = capacity_wh
        self.efficiency = efficiency
        self.load_watts = 0.0
        self.solar_input_watts = 0.0
        self.log = []

    def set_load(self, watts: float):
        self.load_watts = watts
        self._log_event(f"Load set to {watts:.1f} W")

    def update_solar_harvest(self, peak_solar_watts: float, harvest_efficiency: float):
        """Applies alignment efficiency to compute effective harvested solar wattage."""
        self.solar_input_watts = peak_solar_watts * harvest_efficiency
        self._log_event(f"Solar Harvest: {self.solar_input_watts:.1f} W (Eff: {harvest_efficiency*100:.1f}%)")

    def update_charge(self, duration_seconds: float):
        net_watts = self.solar_input_watts - (self.load_watts / self.efficiency)
        wh_change = net_watts * (duration_seconds / 3600.0)
        self.current_wh = max(0.0, min(self.capacity_wh, self.current_wh + wh_change))

    def estimate_runtime_hours(self) -> float:
        net_watts = (self.load_watts / self.efficiency) - self.solar_input_watts
        if net_watts <= 0:
            return float('inf')
        return self.current_wh / net_watts

    def _log_event(self, message: str):
        self.log.append(f"[{datetime.now().isoformat()}] {message}")

    def print_status(self):
        runtime = self.estimate_runtime_hours()
        print(f"--- {self.name} STATUS ---")
        print(f"Capacity: {self.capacity_wh} Wh | Current Charge: {self.current_wh:.1f} Wh")
        print(f"Current load: {self.load_watts:.1f} W | Dynamic Solar Input: {self.solar_input_watts:.1f} W")
        if runtime == float('inf'):
            print("Estimated runtime: Infinite (Positive net charge balance)")
        else:
            print(f"Estimated runtime: {runtime:.2f} hours")
        print("-" * 35)


class OSTS:
    """
    Odinson Solar Tracking System (OSTS) v0.31 Engine.
    """
    def __init__(self, version: str, vehicle_model: str, power_station: PowerStation, tracker: SolarTracker):
        self.version = version
        self.vehicle_model = vehicle_model
        self.power_station = power_station
        self.tracker = tracker
        self.events = []

    def record_event(self, description: str):
        entry = f"[{datetime.now().isoformat()}] {description}"
        self.events.append(entry)
        print("EVENT:", entry)

    def run_tracking_session(self, sim_schedule: list[tuple[float, float, float, float]]):
        """
        Runs tracking simulation.
        :param sim_schedule: List of tuples (hour_of_day, load_watts, peak_solar_watts, duration_seconds)
        """
        self.record_event("OSTS v0.31 Dynamic Tracking Session Initiated")
        
        for hour, load, peak_solar, duration in sim_schedule:
            # Calculate solar orbital geometry
            solar_elevation, solar_azimuth = self.tracker.calculate_sun_position(hour)
            
            # Execute automated panel tracking adjustment
            actuator_status = self.tracker.track_sun(solar_elevation)
            self.record_event(f"Time {hour:02.1f}h | Sun Elevation: {solar_elevation:.1f}° | {actuator_status}")
            
            # Compute capture efficiency and update battery harvest
            eff = self.tracker.calculate_alignment_efficiency(solar_elevation)
            self.power_station.set_load(load)
            self.power_station.update_solar_harvest(peak_solar, eff)
            
            # Step power calculation forward
            self.power_station.update_charge(duration)
            time.sleep(0.05)
            
        self.record_event("OSTS v0.31 Dynamic Tracking Session Completed")

    def print_summary(self):
        print(f"\n==========================================")
        print(f" OSTS {self.version} Deployment Summary - {self.vehicle_model}")
        print(f"==========================================")
        self.power_station.print_status()
        print("System Timeline History:")
        for e in self.events:
            print("  ", e)


if __name__ == "__main__":
    # Initialize v0.31 Hardware Architecture
    solar_battery = PowerStation(name="Solar Storage Battery", capacity_wh=518, efficiency=0.88)
    tracker_unit = SolarTracker(latitude=40.67) # Local vehicle coordinates
    osts = OSTS(version="v0.31", vehicle_model="Tesla Model Y", power_station=solar_battery, tracker=tracker_unit)

    # Narrative Deployment Milestones
    osts.record_event("Field Inspection initialized on Tesla Model Y hood setup.")
    osts.record_event("Hostile encounter resolved; vehicle damage repaired.")
    osts.record_event("OSTS v0.31 active solar tracking software initialized.")

    # Simulation Schedule: (Hour of Day, Load Watts, Peak Available Solar Watts, Duration Seconds)
    simulation_schedule = [
        (09.0, 45.0, 30.0, 1800),  # Morning run: Low solar elevation, active tilt tracking
        (12.0, 80.0, 60.0, 1800),  # Solar Noon: Peak solar elevation (~49.3°), flat panel tilt
        (16.0, 30.0, 25.0, 1800),  # Late Afternoon: Low solar angle, sharp tilt adjustment
    ]

    # Run field telemetry tracking loop
    osts.run_tracking_session(simulation_schedule)
    osts.print_summary()