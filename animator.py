from pathlib import Path

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from config import SimulationConfig
from power_model import PowerModel, PowerValues
from signal_model import SignalData, SineSignalModel


class PowerTriangleAnimator:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.signal_model = SineSignalModel(config)
        self.power_model = PowerModel(config)

        self.figure = None
        self.time_axis = None
        self.triangle_axis = None

        self.voltage_reference_line = None
        self.current_reference_line = None
        self.power_reference_area = None
        self.power_reference_line = None

        self.active_power_line = None
        self.reactive_power_line = None
        self.apparent_power_line = None

        self.active_power_text = None
        self.reactive_power_text = None
        self.apparent_power_text = None
        self.values_text = None
        self.background = None

    def generate(self) -> Path:
        self.config.validate()
        self.config.ensure_output_directory()
        self._create_figure()

        output_path = self.config.output_path()
        phase_angles = self.config.phase_angles_deg()
        frame_durations = self._frame_durations(phase_angles)

        with self._create_writer(output_path, frame_durations) as writer:
            for phi_deg in phase_angles:
                signal_data = self.signal_model.calculate(phi_deg)
                power_values = self.power_model.calculate(phi_deg)
                self._update_static_frame_parts(signal_data, power_values)
                frame = self._capture_frame()
                writer.append_data(frame)

        plt.close(self.figure)
        return output_path

    def _create_figure(self) -> None:
        plt.style.use("seaborn-v0_8-whitegrid")

        self.figure = plt.figure(
            figsize=(self.config.figure_width, self.config.figure_height),
            dpi=self.config.figure_dpi,
            constrained_layout=True,
        )
        grid = self.figure.add_gridspec(
            nrows=2,
            ncols=1,
            height_ratios=[1.0, 2.0],
        )

        self.time_axis = self.figure.add_subplot(grid[0, 0])
        self.triangle_axis = self.figure.add_subplot(grid[1, 0])

        self.figure.suptitle(
            "Tensão, Corrente e Potências",
            fontsize=15,
            fontweight="bold",
        )

        self._configure_time_axis()
        self._initialize_time_artists()
        self._configure_triangle_axis()
        self._initialize_triangle_lines()

    def _configure_time_axis(self) -> None:
        cycle_duration_ms = self.config.cycle_duration_seconds() * 1000.0

        self.time_axis.set_title("")
        self.time_axis.set_xlabel("Tempo")
        self.time_axis.set_ylabel("Amplitude normalizada")
        self.time_axis.set_xlim(0.0, cycle_duration_ms)
        self.time_axis.set_ylim(-1.5, 1.5)
        self.time_axis.set_autoscale_on(False)
        self.time_axis.tick_params(
            axis="both",
            labelbottom=False,
            labelleft=False,
        )
        self.time_axis.axhline(0.0, color="#444444", linewidth=1.0)
        self.time_axis.grid(True, alpha=0.35)

    def _initialize_time_artists(self) -> None:
        self.voltage_reference_line = self.time_axis.plot(
            [],
            [],
            color="#111111",
            linewidth=2.8,
            alpha=1.0,
            label="Tensão (V)",
            zorder=3,
        )[0]
        self.current_reference_line = self.time_axis.plot(
            [],
            [],
            color="#111111",
            linewidth=2.8,
            linestyle="--",
            alpha=1.0,
            label="Corrente (A)",
            zorder=3,
        )[0]
        self.power_reference_area = self.time_axis.fill_between(
            [],
            [],
            [],
            color="#1f77b4",
            alpha=0.50,
            zorder=1,
        )
        self.power_reference_line = self.time_axis.plot(
            [],
            [],
            color="#1f77b4",
            linewidth=3.4,
            alpha=1.0,
            label="Potência (W)",
            zorder=2,
        )[0]

        self.time_axis.legend(loc="upper right", frameon=True, framealpha=0.94)

    def _configure_triangle_axis(self) -> None:
        apparent_power = self.config.voltage_rms * self.config.current_rms
        axis_limit = apparent_power * 1.25

        self.triangle_axis.set_title("Triângulo de potências", fontweight="bold")
        self.triangle_axis.set_xlabel(r"$P$ [W]")
        self.triangle_axis.set_ylabel(r"$Q$ [VAr]")
        self.triangle_axis.set_xlim(-axis_limit, axis_limit)
        self.triangle_axis.set_ylim(-axis_limit, axis_limit)
        self.triangle_axis.set_autoscale_on(False)
        self.triangle_axis.tick_params(
            axis="both",
            labelbottom=False,
            labelleft=False,
        )
        self.triangle_axis.set_aspect("equal", adjustable="box")
        self.triangle_axis.axhline(0.0, color="#444444", linewidth=1.0)
        self.triangle_axis.axvline(0.0, color="#444444", linewidth=1.0)
        self.triangle_axis.grid(True, alpha=0.35)

    def _initialize_triangle_lines(self) -> None:
        self.active_power_line = self.triangle_axis.plot(
            [],
            [],
            color="#1f77b4",
            linewidth=3.2,
            solid_capstyle="round",
        )[0]
        self.reactive_power_line = self.triangle_axis.plot(
            [],
            [],
            color="#d62728",
            linewidth=3.2,
            solid_capstyle="round",
        )[0]
        self.apparent_power_line = self.triangle_axis.plot(
            [],
            [],
            color="#2ca02c",
            linewidth=3.2,
            solid_capstyle="round",
        )[0]

        self.active_power_text = self.triangle_axis.text(
            0.0,
            0.0,
            "",
            color="#1f77b4",
            fontweight="bold",
            ha="center",
            va="center",
        )
        self.reactive_power_text = self.triangle_axis.text(
            0.0,
            0.0,
            "",
            color="#d62728",
            fontweight="bold",
            ha="center",
            va="center",
        )
        self.apparent_power_text = self.triangle_axis.text(
            0.0,
            0.0,
            "",
            color="#2ca02c",
            fontweight="bold",
            ha="center",
            va="center",
        )
        self.values_text = self.triangle_axis.text(
            0.03,
            0.97,
            "",
            transform=self.triangle_axis.transAxes,
            ha="left",
            va="top",
            fontsize=10,
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": "white",
                "edgecolor": "#dddddd",
                "alpha": 0.94,
            },
        )

    def _update_static_frame_parts(
        self,
        signal_data: SignalData,
        power_values: PowerValues,
    ) -> None:
        self._update_time_references(signal_data)
        self._update_titles(signal_data.phi_deg)
        self._update_triangle(power_values)

    def _update_time_references(self, signal_data: SignalData) -> None:
        time_values = signal_data.time_milliseconds
        voltage_values = self._normalized_voltage(signal_data)
        current_values = self._normalized_current(signal_data)
        power_values = self._normalized_power(signal_data)

        self.voltage_reference_line.set_data(time_values, voltage_values)
        self.current_reference_line.set_data(time_values, current_values)
        self._set_area_data(self.power_reference_area, time_values, power_values)
        self.power_reference_line.set_data(time_values, power_values)

    def _update_titles(self, phi_deg: float) -> None:
        phi_text = rf"$\phi={phi_deg:.1f}^\circ$"
        self.time_axis.set_title(phi_text)

    def _update_triangle(self, power_values: PowerValues) -> None:
        active_power = power_values.active_power
        reactive_power = power_values.reactive_power
        apparent_power = power_values.apparent_power

        self.active_power_line.set_data([0.0, active_power], [0.0, 0.0])
        self.reactive_power_line.set_data(
            [active_power, active_power],
            [0.0, reactive_power],
        )
        self.apparent_power_line.set_data([0.0, active_power], [0.0, reactive_power])

        text_offset = apparent_power * 0.07
        sign = self._sign_for_label(reactive_power)
        horizontal_direction = self._sign_for_label(active_power)

        self.active_power_text.set_text(r"$P$")
        self.active_power_text.set_position((active_power / 2.0, -sign * text_offset))

        self.reactive_power_text.set_text(r"$Q$")
        self.reactive_power_text.set_position(
            (
                active_power + horizontal_direction * text_offset,
                reactive_power / 2.0,
            )
        )

        self.apparent_power_text.set_text(r"$S$")
        self.apparent_power_text.set_position(
            (
                active_power / 2.0,
                reactive_power / 2.0 + sign * text_offset,
            )
        )

        values = [
            rf"$P={power_values.active_power:.1f}\,\mathrm{{W}}$",
            rf"$Q={power_values.reactive_power:.1f}\,\mathrm{{VAr}}$",
            rf"$S={power_values.apparent_power:.1f}\,\mathrm{{VA}}$",
            rf"$FP={power_values.power_factor:.3f}$",
            rf"$\phi={power_values.phi_deg:.1f}^\circ$",
            power_values.load_type,
        ]
        self.values_text.set_text("\n".join(values))

    def _sign_for_label(self, value: float) -> float:
        if value < 0.0:
            return -1.0

        return 1.0

    def _normalized_voltage(self, signal_data: SignalData) -> np.ndarray:
        return 1.4 * signal_data.voltage / self.signal_model.voltage_peak()

    def _normalized_current(self, signal_data: SignalData) -> np.ndarray:
        return 1.1 * signal_data.current / self.signal_model.current_peak()

    def _normalized_power(self, signal_data: SignalData) -> np.ndarray:
        apparent_power = self.config.voltage_rms * self.config.current_rms
        return signal_data.instant_power / (2.0 * apparent_power)

    def _set_area_data(self, area, x_values, y_values) -> None:
        if len(x_values) == 0:
            area.set_verts([])
            return

        x_array = np.asarray(x_values)
        y_array = np.asarray(y_values)
        baseline = np.zeros_like(y_array)

        upper_points = np.column_stack([x_array, y_array])
        lower_points = np.column_stack([x_array[::-1], baseline[::-1]])
        vertices = np.vstack([upper_points, lower_points])
        area.set_verts([vertices])

    def _capture_frame(self) -> np.ndarray:
        canvas = self.figure.canvas
        canvas.draw()
        frame_rgba = np.asarray(canvas.buffer_rgba())
        frame_rgb = frame_rgba[:, :, :3].copy()
        return frame_rgb

    def _frame_durations(self, phase_angles: list[float]) -> list[float]:
        durations = []
        default_duration = self.config.frame_duration_seconds()

        for phi_deg in phase_angles:
            if self.config.hold_time_seconds > 0.0:
                durations.append(self.config.hold_time_seconds)
            else:
                durations.append(default_duration)

        return durations

    def _create_writer(self, output_path: Path, frame_durations: list[float]):
        self._ensure_freeimage()
        return imageio.get_writer(
            output_path,
            format="GIF-FI",
            mode="I",
            duration=frame_durations,
            loop=0,
            palettesize=128,
            subrectangles=False,
        )

    def _ensure_freeimage(self) -> None:
        from imageio.plugins import freeimage

        if freeimage.fi.has_lib():
            return

        try:
            freeimage.download()
        except Exception as exc:
            message = (
                "Could not prepare the FreeImage GIF writer. "
                "Run 'python -c \"from imageio.plugins import freeimage; "
                "freeimage.download()\"' and try again."
            )
            raise RuntimeError(message) from exc
