# cli.py (updated interface)
from physics.py import *
import matplotlib.pyplot as plt


def get_input():
    print("=== Advanced Golf Simulator ===")
    print("Available clubs:", ", ".join(CLUB_LOFTS.keys()))
    return {
        "club_type": input("Club type: ").lower().strip(),
        "club_speed_mph": float(input("Club speed (mph): ")),
        "attack_angle": float(input("Angle of attack (deg): ")),
        "strike_offset_mm": float(input("Strike offset (mm): ")),
        "wind_speed": float(input("Wind speed (mph): ")),
        "wind_dir": float(input("Wind direction (deg): ")),
    }


def plot_results(trajectory):
    yards = [meters_to_yards(p[0]) for p in trajectory]
    heights = [meters_to_yards(p[2]) for p in trajectory]

    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.plot(yards, heights)
    plt.xlabel("Distance (yards)")
    plt.ylabel("Height (yards)")
    plt.title("Ball Flight")

    plt.subplot(122)
    plt.plot(yards, [meters_to_yards(p[1]) for p in trajectory])
    plt.xlabel("Distance (yards)")
    plt.ylabel("Lateral (yards)")
    plt.title("Shot Shape")

    plt.tight_layout()
    plt.show()


def main():
    params = get_input()

    try:
        vel, spin = calculate_launch_conditions(
            params["club_speed_mph"],
            params["club_type"],
            params["attack_angle"],
            params["strike_offset_mm"]
        )
    except KeyError:
        print(f"Error: Invalid club type '{params['club_type']}'")
        return

    carry, roll, total = simulate_full_shot(
        vel, spin,
        params["wind_speed"],
        params["wind_dir"]
    )

    print("\n=== Shot Analysis ===")
    print(f"Carry: {carry:.1f} yards")
    print(f"Bounce/Roll: {roll:.1f} yards")
    print(f"Total Distance: {total:.1f} yards")

    # Plot full trajectory
    trajectory = simulate_trajectory(vel, spin, params["wind_speed"], params["wind_dir"])
    plot_results(trajectory)


if __name__ == "__main__":
    main()