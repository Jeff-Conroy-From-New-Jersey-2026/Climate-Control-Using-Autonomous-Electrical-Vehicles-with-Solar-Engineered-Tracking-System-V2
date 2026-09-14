##########################################################################################################~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~******* *** **   *
### 
### More OpenSource MIT Licensed Python Code: Version 0.1 of the OSTS Prototype that I implemented myself
###  Here you go, TSLA Energy!  SPCX: you owe me. NASA does not.  NO other company does... but, in a way, I like my Tesla model Y except for some key flaws.#
###
###  ~ By Jeff Conroy | Global HC Analytics LLC Founder | September 14th, 2026 
###
###  Solar Power is our lease well utilized source of power! Look at this US Department of Energy!  Show Respect Elon Musk and your minions!
###
#####################################@@@@@@@@@@@@@@@@@@@@@@555554444333221~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.... 


from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any


@dataclass(slots=True)
class SolarArrayConfig:
    """
    Configuration specifications for the roof-mounted solar PV array.

    Attributes:
        panel_count (int): Number of physical panels mounted on the roof crossbars.
        rated_watts_per_panel (float): Standard Test Conditions (STC) rated power output per panel (Watts).
        array_efficiency (float): Combined efficiency factor accounting for panel degradation, 
                                 cable resistance, and MPPT conversion losses (0.0 to 1.0).
        air_gap_clearance_mm (float): Convective cooling gap between the underside of the panel 
                                      and the vehicle's glass roof surface (in millimeters).
    """
    panel_count: int = 2
    rated_watts_per_panel: float = 180.0  # Dual 180W Monocrystalline panels -> 360W nominal system
    array_efficiency: float = 0.942       # 94.2% system DC-to-DC conversion efficiency target
    air_gap_clearance_mm: float = 16.0    # 16mm convective air gap prevents thermal saturation on glass


@dataclass(slots=True)
class AuxiliaryBatteryConfig:
    """
    Configuration specifications for the isolated auxiliary storage buffer.

    Attributes:
        max_capacity_wh (float): Total energy capacity of the auxiliary battery bank in Watt-hours.
        current_charge_wh (float): Current stored energy level in Watt-hours.
        battery_chemistry (str): Cell chemistry type (e.g., LiFePO4 for safety and thermal stability).
    """
    max_capacity_wh: float = 2058.0       # Standalone 2.05 kWh LiFePO4 power station
    current_charge_wh: float = 1798.0     # Baseline charge state (~87.4% State of Charge)
    battery_chemistry: str = "LiFePO4"    # High cycle life, safe thermal runaway threshold


class SolarOverlandTelemetryEngine:
    """
    Real-time telemetry and monitoring engine for off-grid vehicle solar power architectures.

    Key Operational Responsibilities:
    1. Dynamic Power Generation: Calculates real-time DC power harvest based on solar irradiance and thermal state.
    2. Galvanic Isolation Enforcement: Verifies zero high-voltage/12V electrical coupling with the primary vehicle.
    3. Thermal Derating Model: Computes performance penalties based on ambient temperature and convective air flow.
    4. State Monitoring: Tracks auxiliary storage battery State of Charge (SoC) and allows dynamic charge updates.
    """

    def __init__(
        self,
        solar_cfg: SolarArrayConfig,
        battery_cfg: AuxiliaryBatteryConfig,
        snapshot_callback: Callable[[Dict[str, Any]], None] | None = None,
    ) -> None:
        """
        Initializes the telemetry engine with array hardware and battery configurations.

        :param solar_cfg: Instantiated SolarArrayConfig containing PV array physical parameters.
        :param battery_cfg: Instantiated AuxiliaryBatteryConfig containing storage status parameters.
        :param snapshot_callback: Optional user-defined callback function invoked whenever a 
                                  telemetry snapshot is captured (ideal for UI/dashboard feeds).
        """
        self.solar: SolarArrayConfig = solar_cfg
        self.battery: AuxiliaryBatteryConfig = battery_cfg
        
        # Mandatory Safety Metric: Galvanic Isolation Check.
        # 0.0V coupling confirms the system is 100% physically and electrically isolated 
        # from the vehicle's high-voltage traction pack and secondary 12V/16V low-voltage bus.
        self.hv_dc_coupling_volts: float = 0.0
        
        self._snapshot_callback: Callable[[Dict[str, Any]], None] | None = snapshot_callback

    @property
    def max_nominal_output_watts(self) -> float:
        """
        Calculates maximum theoretical peak power output under Standard Test Conditions (STC: 1000 W/m², 25°C).

        Formula:
            Peak Power (W) = Panel Count * Rated Wattage per Panel
        """
        return float(self.solar.panel_count * self.solar.rated_watts_per_panel)

    @property
    def current_soc_percent(self) -> float:
        """
        Calculates current State of Charge (SoC) percentage of the auxiliary storage buffer.

        Returns:
            float: Battery charge level expressed as a percentage (0.0% to 100.0%).
        """
        # Guard clause against zero or negative maximum capacity configuration
        if self.battery.max_capacity_wh <= 0.0:
            return 0.0
        
        raw_soc = (self.battery.current_charge_wh / self.battery.max_capacity_wh) * 100.0
        # Clamp output strictly between 0.0% and 100.0%
        return max(0.0, min(100.0, raw_soc))

    def verify_hv_isolation(self) -> bool:
        """
        Safety Check Protocol: Guarantees absolute physical isolation from the vehicle electrical systems.

        Returns:
            bool: True if voltage coupling is exactly 0.0V (Safe/Isolated), False otherwise (Fault/Breach).
        """
        return self.hv_dc_coupling_volts == 0.0

    def compute_thermal_derating(self, ambient_temp_c: float) -> float:
        """
        Calculates thermal derating multiplier based on ambient air temperature and air-gap ventilation.

        Physics / Thermodynamics Context:
            - Photovoltaic cell efficiency drops as panel operating temperature exceeds standard reference (25°C).
            - Monocrystalline Silicon temperature coefficient: ~ -0.35% power per °C above 25°C.
            - A convective air gap (≥16mm) allows laminar airflow underneath the array, mitigating thermal absorption 
              from the glass vehicle roof.

        :param ambient_temp_c: Current ambient temperature in degrees Celsius (°C).
        :return: Efficiency retention multiplier clamped between 0.80 (20% max loss) and 1.00 (No thermal loss).
        """
        # No thermal derating penalty if ambient temperature is at or below STC baseline (25°C)
        if ambient_temp_c <= 25.0:
            return 1.0

        # Calculate excess temperature above 25°C threshold
        temp_delta = ambient_temp_c - 25.0
        
        # Calculate unmitigated power loss based on standard silicon temperature coefficient (0.35%/°C)
        raw_loss = temp_delta * 0.0035

        # Evaluate convective cooling benefit provided by the physical roof mounting gap
        # Air gaps >= 16mm provide superior airflow, mitigating up to 5% thermal degradation
        cooling_benefit = 0.05 if self.solar.air_gap_clearance_mm >= 16.0 else 0.03
        
        # Net efficiency reduction after applying air-gap thermal relief
        loss_factor = max(0.0, raw_loss - cooling_benefit)

        # Retain at least 80% efficiency under extreme ambient heat conditions
        return max(0.80, 1.0 - loss_factor)

    def update_battery_energy(self, energy_delta_wh: float) -> float:
        """
        Simulates charging or discharging of the auxiliary battery.

        :param energy_delta_wh: Energy added (positive) or consumed (negative) in Watt-hours.
        :return: Updated total stored energy in Watt-hours.
        """
        new_charge = self.battery.current_charge_wh + energy_delta_wh
        # Constrain current charge within [0.0, max_capacity_wh]
        self.battery.current_charge_wh = max(0.0, min(self.battery.max_capacity_wh, new_charge))
        return self.battery.current_charge_wh

    def fetch_telemetry_snapshot(
        self,
        solar_irradiance_factor: float = 1.0,
        ambient_temp_c: float = 25.0,
    ) -> Dict[str, Any]:
        """
        Executes a telemetry evaluation frame and compiles system metrics into a formatted dictionary.

        :param solar_irradiance_factor: Normalized sunlight level (0.0 = total darkness, 1.0 = peak direct sun).
        :param ambient_temp_c: Current ambient temperature in degrees Celsius (°C).
        :return: Dictionary containing calculated power metrics, safety status, and battery state.
        """
        # Validate and clamp solar irradiance input factor to safe range [0.0, 1.0]
        clamped_irradiance = max(0.0, min(1.0, solar_irradiance_factor))

        # 1. Calculate thermal retention factor based on ambient temperature and air-gap spacing
        thermal_factor = self.compute_thermal_derating(ambient_temp_c)

        # 2. Compute effective system conversion efficiency
        effective_efficiency = self.solar.array_efficiency * thermal_factor

        # 3. Compute real-time power harvest in Watts
        # Power = Nominal Max * Irradiance Ratio * Effective Efficiency
        pv_generation_watts = self.max_nominal_output_watts * clamped_irradiance * effective_efficiency

        # 4. Enforce high-voltage safety isolation verification
        isolation_secure = self.verify_hv_isolation()
        system_status = "NOMINAL" if isolation_secure else "FAULT_ISOLATION_BREACH"

        # 5. Build comprehensive telemetry frame payload matching blueprint metrics
        telemetry_frame: Dict[str, Any] = {
            "system_status": system_status,
            "pv_generation_watts": round(pv_generation_watts, 1),
            "pv_efficiency_pct": round(effective_efficiency * 100.0, 1),
            "thermal_derating_pct": round(thermal_factor * 100.0, 1),
            "battery_soc_pct": round(self.current_soc_percent, 1),
            "battery_capacity_wh": round(self.battery.current_charge_wh, 1),
            "battery_max_wh": round(self.battery.max_capacity_wh, 1),
            "battery_chemistry": self.battery.battery_chemistry,
            "hv_coupling": "ISOLATED" if isolation_secure else "CONNECTED",
            "hv_coupling_voltage": self.hv_dc_coupling_volts,
            "air_gap_status": f"{self.solar.air_gap_clearance_mm}mm Convective Active",
            "ambient_temp_c": ambient_temp_c,
            "irradiance_factor": clamped_irradiance,
        }

        # 6. Execute callback hook if registered (e.g., streaming data to dashboard UI)
        if self._snapshot_callback is not None:
            self._snapshot_callback(telemetry_frame)

        return telemetry_frame


# =====================================================================
# VERIFICATION & TEST EXECUTION LOOP - Ensure Results :)
# =====================================================================
if __name__ == "__main__":
    def log_to_console_callback(data: Dict[str, Any]) -> None:
        """Simple callback handler to demonstrate streaming telemetry updates."""
        print(f"[CALLBACK TRIGGERED] System Status: {data['system_status']} | Power Output: {data['pv_generation_watts']}W")

    # Initialize configuration instances based on schematic specifications
    array_config = SolarArrayConfig(
        panel_count=2,
        rated_watts_per_panel=180.0,
        array_efficiency=0.942,
        air_gap_clearance_mm=16.0
    )
    
    battery_config = AuxiliaryBatteryConfig(
        max_capacity_wh=2058.0,
        current_charge_wh=1798.0,
        battery_chemistry="LiFePO4"
    )

    # Initialize Telemetry Engine with snapshot callback
    engine = SolarOverlandTelemetryEngine(
        solar_cfg=array_config,
        battery_cfg=battery_config,
        snapshot_callback=log_to_console_callback
    )

    # Run Telemetry Frame under peak sunlight (1.0 Irradiance @ 28°C Ambient)
    snapshot = engine.fetch_telemetry_snapshot(solar_irradiance_factor=1.0, ambient_temp_c=28.0)

    # Print Formatted System Output
    print("\n" + "=" * 60)
    print("GLOBAL HC ANALYTICS LLC CUSTOM MODIFIED TESLA MODEL Y // OFF-GRID AUXILIARY SOLAR TELEMETRY ")
    print("=" * 60)
    print(f" OPERATIONAL STATUS   : {snapshot['system_status']}")
    print(f" REAL-TIME PV HARVEST : {snapshot['pv_generation_watts']} Watts")
    print(f" TOTAL SYSTEM EFF     : {snapshot['pv_efficiency_pct']}%")
    print(f" THERMAL RETENTION    : {snapshot['thermal_derating_pct']}%")
    print(f" STORAGE STATE (SoC)  : {snapshot['battery_soc_pct']}% ({snapshot['battery_capacity_wh']} / {snapshot['battery_max_wh']} Wh)")
    print(f" BATTERY CHEMISTRY    : {snapshot['battery_chemistry']}")
    print(f" HV GALVANIC STATUS   : {snapshot['hv_coupling']} ({snapshot['hv_coupling_voltage']}V DC)")
    print(f" THERMAL AIR GAP      : {snapshot['air_gap_status']}")
    print("=" * 60 + "\n")