import numpy as np
import matplotlib.pyplot as plt
from golf_sim.simulator import GolfShotSimulator


def get_input():
    print("=== Golf Shot Simulator ===")
    return {
        "club_speed": float(input("Club speed (m/s): ")),
        "loft_deg": float(input("Loft (deg): ")),
        "attack_angle_deg": float(input("Angle of attack (deg): ")),
        "swing_path_deg": float(input("Swing path (deg): ")),
        "strike_offset_mm": float(input("Strike offset (mm): ")),
        "wind_speed": float(input("Wind speed (m/s): ")),
        "wind_dir": float(input("Wind direction (deg): ")),
        "surface": input("Surface [fairway/rough/green]: ").lower()
    }


def plot_results(trajectory):
    fig = plt.figure(figsize=(12, 6))

    # 3D plot
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2])
    ax1.set_title("3D Trajectory")
    ax1.set_xlabel("Distance (m)")
    ax1.set_ylabel("Lateral (m)")
    ax1.set_zlabel("Height (m)")

    # Top-down view
    ax2 = fig.add_subplot(122)
    ax2.plot(trajectory[:, 0], trajectory[:, 1])
    ax2.set_title("Top-Down View")
    ax2.set_xlabel("Distance (m)")
    ax2.set_ylabel("Lateral (m)")

    plt.tight_layout()
    plt.show()


def main():
    params = get_input()

    # Convert wind to vector
    wind_dir = np.radians(params["wind_dir"])
    params["wind"] = params["wind_speed"] * np.array([
        np.cos(wind_dir),
        np.sin(wind_dir),
        0
    ])

    # Run simulation
    simulator = GolfShotSimulator(surface=params["surface"])
    results = simulator.simulate_shot(params)

    # Display results
    print(f"\nCarry Distance: {results['carry']:.1f}m")
    print(f"Total Distance: {results['total']:.1f}m")
    print(f"Final Spin: {results['spin'][2]:.0f} RPM (backspin)")

    plot_results(results["trajectory"])


if __name__ == "__main__":
    main()