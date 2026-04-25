from dataclasses import dataclass
from pathlib import Path


@dataclass
class SimulationConfig:
    voltage_rms: float = 220.0
    current_rms: float = 10.0
    frequency_hz: float = 60.0
    phi_start_deg: float = -90.0
    phi_end_deg: float = -90.0
    phi_step_deg: float = 15.0
    samples_per_cycle: int = 60
    cycles_per_phi: int = 1
    fps: int = 30
    hold_time_seconds: float = 1.0
    output_gif_path: str = r"output/power_triangle_animation.gif"
    figure_width: float = 12
    figure_height: float = 10
    figure_dpi: int = 80

    def validate(self) -> None:
        errors = []

        if self.phi_step_deg <= 0:
            errors.append("phi_step_deg must be positive.")

        if self.phi_start_deg > self.phi_end_deg:
            errors.append("phi_start_deg must be less than or equal to phi_end_deg.")

        if self.samples_per_cycle <= 0:
            errors.append("samples_per_cycle must be greater than zero.")

        if self.cycles_per_phi <= 0:
            errors.append("cycles_per_phi must be greater than zero.")

        if self.fps <= 0:
            errors.append("fps must be greater than zero.")

        if self.voltage_rms <= 0:
            errors.append("voltage_rms must be greater than zero.")

        if self.current_rms <= 0:
            errors.append("current_rms must be greater than zero.")

        if self.frequency_hz <= 0:
            errors.append("frequency_hz must be greater than zero.")

        if self.hold_time_seconds < 0:
            errors.append("hold_time_seconds must be zero or positive.")

        if self.figure_width <= 0:
            errors.append("figure_width must be greater than zero.")

        if self.figure_height <= 0:
            errors.append("figure_height must be greater than zero.")

        if self.figure_dpi <= 0:
            errors.append("figure_dpi must be greater than zero.")

        if len(errors) > 0:
            message = "Invalid simulation configuration:\n" + "\n".join(errors)
            raise ValueError(message)

    def phase_angles_deg(self) -> list[float]:
        self.validate()

        values = []
        current_value = self.phi_start_deg
        end_value = self._effective_phi_end_deg()
        tolerance = self.phi_step_deg * 1.0e-9

        while current_value <= end_value + tolerance:
            values.append(round(current_value, 10))
            current_value = current_value + self.phi_step_deg

        last_value = values[-1]
        if last_value < end_value - tolerance:
            values.append(end_value)

        return values

    def _effective_phi_end_deg(self) -> float:
        if self.phi_start_deg == self.phi_end_deg:
            return self.phi_start_deg + 360.0

        return self.phi_end_deg

    def cycle_duration_seconds(self) -> float:
        return 1.0 / self.frequency_hz

    def frame_duration_seconds(self) -> float:
        return 1.0 / self.fps

    def hold_frame_count(self) -> int:
        return int(round(self.hold_time_seconds * self.fps))

    def output_path(self) -> Path:
        return Path(self.output_gif_path)

    def ensure_output_directory(self) -> None:
        output_path = self.output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
