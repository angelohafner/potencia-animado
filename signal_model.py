from dataclasses import dataclass

import numpy as np

from config import SimulationConfig


@dataclass
class SignalData:
    phi_deg: float
    time_seconds: np.ndarray
    time_milliseconds: np.ndarray
    voltage: np.ndarray
    current: np.ndarray
    instant_power: np.ndarray


class SineSignalModel:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def calculate(self, phi_deg: float) -> SignalData:
        phi_rad = np.deg2rad(phi_deg)
        cycle_duration_seconds = self.config.cycle_duration_seconds()
        omega = 2.0 * np.pi * self.config.frequency_hz

        time_seconds = np.linspace(
            0.0,
            cycle_duration_seconds,
            self.config.samples_per_cycle,
            endpoint=True,
        )
        time_milliseconds = time_seconds * 1000.0

        voltage_peak = np.sqrt(2.0) * self.config.voltage_rms
        current_peak = np.sqrt(2.0) * self.config.current_rms

        voltage = voltage_peak * np.sin(omega * time_seconds)
        current = current_peak * np.sin(omega * time_seconds - phi_rad)
        instant_power = voltage * current

        return SignalData(
            phi_deg=phi_deg,
            time_seconds=time_seconds,
            time_milliseconds=time_milliseconds,
            voltage=voltage,
            current=current,
            instant_power=instant_power,
        )

    def voltage_peak(self) -> float:
        return float(np.sqrt(2.0) * self.config.voltage_rms)

    def current_peak(self) -> float:
        return float(np.sqrt(2.0) * self.config.current_rms)
