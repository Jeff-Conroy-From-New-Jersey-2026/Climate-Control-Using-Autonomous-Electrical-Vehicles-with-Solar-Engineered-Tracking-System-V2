########################################################################&&&%%@!~~~~~------------------------------------------....
# OSTS V0.3 Python Code - Released by Jeff Conroy September 18th, 2026 on GitHub (Python Code Open Source via the MIT License)
## and also LinkedIn with Prototype and actual photos for TSLA, LCID, or anyone who wants to know! =)
#################################################&&&%%@!~~~~~------------------------------------------....

import time
from datetime import datetime


class PowerStation:
    """
    Represents an isolated auxiliary energy storage battery system.
    
    Handles load management, solar input integration, state of charge (SoC) updates,
    runtime calculations, and internal event logging.
    """
    def __init__(self, name: str, capacity_wh: float, efficiency: float = 0.9):
        """
        Initialize the PowerStation instance.

        :param name: Descriptive label for the battery unit.
        :param capacity_wh: Maximum stored energy capacity in Watt-hours (Wh).
        :param efficiency: System conversion efficiency factor (0.0 to 1.0).
        """
        self.name = name
        self.capacity_wh = capacity_wh
        self.current_wh = capacity_wh  # Assume system begins at 100% full capacity
        self.efficiency = efficiency
        self.load_watts = 0.0          # Active discharge load drawing power (Watts)
        self.solar_input_watts = 0.0   # Active solar harvest generation (Watts)
        self.log = []                  # Internal event telemetry audit log

    def set_load(self, watts: float):
        """Updates the active power consumption load in Watts and records the event."""
        self.load_watts = watts
        self._log_event(f"Load set to {watts} W")

    def set_solar_input(self, watts: float):
        """Updates the active incoming solar generation in Watts and records the event."""
        self.solar_input_watts = watts
        self._log_event(f"Solar input set to {watts} W")

    def update_charge(self, duration_seconds: float):
        """
        Calculates net power flow and updates the internal stored energy over a given duration.

        :param duration_seconds: Time interval for the calculation in seconds.
        """
        # Net power in Watts: Positive indicates net charging, negative indicates net drain (accounting for inverter/conversion losses)
        net_watts = self.solar_input_watts - (self.load_watts / self.efficiency)
        
        # Convert net power (Watts) and duration (seconds) into energy change (Watt-hours)
        wh_change = net_watts * (duration_seconds / 3600.0)
        
        # Clamp stored charge strictly within valid boundaries [0.0, capacity_wh]
        self.current_wh = max(0.0, min(self.capacity_wh, self.current_wh + wh_change))

    def estimate_runtime_hours(self) -> float:
        """
        Calculates remaining battery runtime in hours under the active load and solar input.

        :return: Estimated hours remaining (returns infinity if solar input equals or exceeds discharge load).
        """
        net_watts = (self.load_watts / self.efficiency) - self.solar_input_watts
        if net_watts <= 0:
            return float('inf')  # Continuous operation sustained by positive or net-zero energy balance
        return self.current_wh / net_watts

    def _log_event(self, message: str):
        """Appends a timestamped entry to the internal hardware event log."""
        self.log.append(f"[{datetime.now().isoformat()}] {message}")

    def print_status(self):
        """Outputs a structured diagnostic report covering charge state, loads, and operational logs."""
        runtime = self.estimate_runtime_hours()
        print(f"--- {self.name} STATUS ---")
        print(f"Capacity: {self.capacity_wh} Wh | Current Charge: {self.current_wh:.1f} Wh")
        print(f"Efficiency: {self.efficiency * 100:.1f}%")
        print(f"Current load: {self.load_watts} W | Solar Input: {self.solar_input_watts} W")
        if runtime == float('inf'):
            print("Estimated runtime: Infinite (Positive net charge or no load)")
        else:
            print(f"Estimated runtime: {runtime:.2f} hours")
        print("Event log:")
        for entry in self.log:
            print("  ", entry)
        print("-" * 25)


class OSTS:
    """
    Odinson Solar Tracking System (OSTS) management engine.
    
    Manages host vehicle integration, field operational sessions, narrative timelines, 
    and system diagnostic outputs.
    """
    def __init__(self, version: str, vehicle_model: str, power_station: PowerStation):
        """
        Initialize the OSTS telemetry manager.

        :param version: Software/hardware release version string.
        :param vehicle_model: Host vehicle platform description.
        :param power_station: Instantiated PowerStation object powering the auxiliary setup.
        """
        self.version = version
        self.vehicle_model = vehicle_model
        self.power_station = power_station
        self.events = []  # Master timeline event registry

    def record_event(self, description: str):
        """Records a timestamped system milestone to memory and prints to standard output."""
        entry = f"[{datetime.now().isoformat()}] {description}"
        self.events.append(entry)
        print("EVENT:", entry)

    def simulate_field_session(self, load_profile: list[tuple[float, float, float]]):
        """
        Executes a sequence of operational power profiles representing active field work.

        :param load_profile: List of tuples structured as (load_watts, solar_watts, duration_seconds).
        """
        self.record_event("Field session started")
        for load_watts, solar_watts, duration in load_profile:
            # Apply power parameters to hardware model
            self.power_station.set_load(load_watts)
            self.power_station.set_solar_input(solar_watts)
            self.power_station._log_event(f"Running {load_watts}W load / {solar_watts}W solar for {duration}s")
            
            # Recalculate stored energy state based on step duration
            self.power_station.update_charge(duration)
            
            # Accelerated delay to simulate time progression during unit testing
            time.sleep(0.05)
        
        # Power down active loads upon session completion
        self.power_station.set_load(0)
        self.power_station.set_solar_input(0)
        self.record_event("Field session ended")

    def print_summary(self):
        """Prints complete system metrics and chronological timeline logs."""
        print(f"\nOSTS {self.version} deployed on {self.vehicle_model}")
        self.power_station.print_status()
        print("OSTS event history:")
        for e in self.events:
            print("  ", e)


if __name__ == "__main__":
    # Instantiate primary Solar Storage Battery system mounted on host vehicle
    solar_storage_battery = PowerStation(name="Solar Storage Battery", capacity_wh=518, efficiency=0.88)
    osts = OSTS(version="v0.3", vehicle_model="Tesla Model Y", power_station=solar_storage_battery)

    # Narrative Event Logging
    osts.record_event("Inspection of Edison Port JFBR site initiated.")
    osts.record_event("Hostile encounter: Attacked by an individual with a hammer. Vehicle sustained damage.")
    osts.record_event("Damage repaired independently. Anger successfully converted into engineering momentum.")
    osts.record_event("OSTS v0.3 deployed: Solar Storage Battery, tablet, and solar banks mounted on vehicle hood.")

    # Operational Load Profile Sequence: (Discharge Load Watts, Solar Input Watts, Step Duration Seconds)
    load_profile = [
        (45, 15, 600),   # Phase 1: Tablet baseline + telemetry comms + low morning solar input
        (80, 20, 900),   # Phase 2: Tablet + extra sensor diagnostic suite + peak solar yield
        (20, 10, 300),   # Phase 3: Low-power background logging + fading solar input
    ]
    
    # Execute field telemetry test loop
    osts.simulate_field_session(load_profile)
    osts.record_event("Session complete. Packing up to secure high-grade sushi.")
    
    # Output full diagnostic telemetry log
    osts.print_summary()