from dataclasses import dataclass

import numpy as np

from config import SimulationConfig


@dataclass
class PowerValues:
    phi_deg: float
    phi_rad: float
    active_power: float
    reactive_power: float
    apparent_power: float
    power_factor: float
    load_type: str


class PowerModel:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def calculate(self, phi_deg: float) -> PowerValues:
        phi_rad = float(np.deg2rad(phi_deg))
        apparent_power = self.config.voltage_rms * self.config.current_rms
        active_power = apparent_power * float(np.cos(phi_rad))
        reactive_power = apparent_power * float(np.sin(phi_rad))
        power_factor = float(np.cos(phi_rad))
        load_type = self._load_type(reactive_power, apparent_power)

        return PowerValues(
            phi_deg=phi_deg,
            phi_rad=phi_rad,
            active_power=active_power,
            reactive_power=reactive_power,
            apparent_power=apparent_power,
            power_factor=power_factor,
            load_type=load_type,
        )

    def _load_type(self, reactive_power: float, apparent_power: float) -> str:
        tolerance = apparent_power * 1.0e-9

        if reactive_power > tolerance:
            return "Carga indutiva"

        if reactive_power < -tolerance:
            return "Carga capacitiva"

        return "Carga puramente resistiva"
