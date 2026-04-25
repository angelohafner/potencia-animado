from config import SimulationConfig
from animator import PowerTriangleAnimator


def main() -> None:
    config = SimulationConfig()
    animator = PowerTriangleAnimator(config)
    output_path = animator.generate()
    print(f"GIF saved to: {output_path}")


if __name__ == "__main__":
    main()
