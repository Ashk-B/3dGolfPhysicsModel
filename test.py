from golf_physics.complete_golf_sim import CompleteGolfSim
import math

# Conversion factor from mph to m/s
MPH_TO_MPS = 0.44704


def main():
    # Create an instance of the simulation
    sim = CompleteGolfSim()

    print("Custom Golf Shot Simulator")
    print("--------------------------")
    print("Enter your shot parameters below:\n")

    # Gather user inputs (all in metric or SI units unless otherwise noted)
    try:
        # Updated prompt to ask for club speed in mph
        club_speed_mph = float(input("Club speed (mph)? e.g. 100: "))
        # Convert mph to m/s for internal calculations
        club_speed_mps = club_speed_mph * MPH_TO_MPS
        loft_deg = float(input("Club loft (degrees)? e.g. 10: "))
        face_angle_deg = float(input("Face angle (degrees)? negative=closed, e.g. -2: "))
        horizontal_offset_cm = float(input("Horizontal offset from center (cm)? e.g. 0 => center strike: "))
        vertical_offset_cm = float(input("Vertical offset from center (cm)? e.g. 0 => center strike: "))
        wind_speed_mps = float(input("Wind speed (m/s)? e.g. 3 => ~6.7 mph: "))
        wind_dir_deg = float(input("Wind direction (deg)? e.g. 90 => from right to left: "))
        temperature_c = float(input("Temperature (C)? e.g. 20: "))
        humidity = float(input("Relative humidity (0-1)? e.g. 0.5 => 50%: "))
        elevation_m = float(input("Elevation (m)? e.g. 200: "))
        surface_type = input("Surface type (fairway/rough/green)? e.g. fairway: ").lower()
        club_type = input("Club type (driver/iron)? e.g. iron: ").lower()
    except ValueError:
        print("Invalid input detected. Please enter numerical values where appropriate.")
        return

    # Validate surface type
    if surface_type not in ["fairway", "rough", "green"]:
        print("Invalid surface type entered. Defaulting to 'fairway'.")
        surface_type = "fairway"

    # Validate club type
    if club_type not in ["driver", "iron"]:
        print("Invalid club type entered. Defaulting to 'iron'.")
        club_type = "iron"

    # Run the simulation
    result = sim.simulate_shot(
        club_speed_mps=club_speed_mps,
        club_loft_deg=loft_deg,
        club_face_angle_deg=face_angle_deg,
        horizontal_offset_cm=horizontal_offset_cm,
        vertical_offset_cm=vertical_offset_cm,
        wind_speed_mps=wind_speed_mps,
        wind_dir_deg=wind_dir_deg,
        temperature_c=temperature_c,
        humidity=humidity,
        elevation_m=elevation_m,
        surface_type=surface_type,  # Pass surface type
        club_type=club_type  # Pass club type
    )

    # Extract final or partial data
    flight_path = result["flight_path_yards"]
    roll_path_yards = result["roll_path_yards"]  # Renamed for consistency
    final_pos = result["final_position_yards"]
    final_spin = result["final_spin"]
    impact = result["impact_result"]  # Extract impact result to get launch angles

    # Compute 2D distances in yards
    if len(flight_path) > 0:
        cx, cy, cz, *_ = flight_path[-1]
    else:
        cx, cy, cz = 0, 0, 0

    if len(roll_path_yards) > 0:
        fx, fy, fz, *_ = roll_path_yards[-1]
    else:
        fx, fy, fz = cx, cy, cz

    carry_2d_yards = math.sqrt(cx ** 2 + cy ** 2)
    if roll_path_yards:
        total_2d_yards = math.sqrt(fx ** 2 + fx ** 2)
        roll_2d_yards = total_2d_yards - carry_2d_yards
    else:
        total_2d_yards = carry_2d_yards
        roll_2d_yards = 0.0

    print("\n--- RESULTS ---")
    print(f"Club Head Speed: {club_speed_mph:.2f} mph")
    print(f"Launch Angle (Vertical): {impact['launch_angle_vert']:.2f} degrees")
    print(f"Launch Angle (Horizontal): {impact['launch_angle_horiz']:.2f} degrees")
    print(f"Carry: {carry_2d_yards:.2f} yards")
    print(f"Roll:  {roll_2d_yards:.2f} yards")
    print(f"Total: {total_2d_yards:.2f} yards")
    print(f"Final Position (x,y,z): ({fx:.2f}, {fy:.2f}, {fz:.2f}) yards")
    print(f"Final Spin (backspin, side): ({final_spin[0]:.2f} RPM, {final_spin[1]:.2f} RPM)")

    print("\nFlight Path length (in steps):", len(flight_path))
    print("Roll Path length (in steps):", len(roll_path_yards))

    # Optional: Plot the flight and roll paths for visualization
    plot_choice = input("\nWould you like to plot the flight and roll paths? (y/n): ").lower()
    if plot_choice == 'y':
        plot_full_path(flight_path, roll_path_yards)

    print("\nDone.")


def plot_full_path(flight_path_yards, roll_path_yards):
    """
    Plot the flight and roll paths of the golf ball.

    Parameters:
        flight_path_yards (list): Flight path data in yards.
        roll_path_yards (list): Roll path data in yards.
    """
    import matplotlib.pyplot as plt

    # Extract flight path data
    flight_x = [state[0] for state in flight_path_yards]
    flight_y = [state[1] for state in flight_path_yards]
    flight_z = [state[2] for state in flight_path_yards]

    # Extract roll path data
    roll_x = [state[0] for state in roll_path_yards]
    roll_y = [state[1] for state in roll_path_yards]
    roll_z = [state[2] for state in roll_path_yards]

    fig = plt.figure(figsize=(14, 6))

    # Plot Flight Path
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot(flight_x, flight_y, flight_z, label='Flight Path', color='blue')
    ax1.set_title('Flight Path of Golf Ball')
    ax1.set_xlabel('X Position (yards)')
    ax1.set_ylabel('Y Position (yards)')
    ax1.set_zlabel('Z Position (yards)')
    ax1.legend()

    # Mark apex
    if flight_z:
        apex_index = flight_z.index(max(flight_z))
        ax1.scatter(flight_x[apex_index], flight_y[apex_index], flight_z[apex_index], color='red', s=50, label='Apex')
        ax1.legend()

    # Plot Roll Path
    ax2 = fig.add_subplot(122)
    ax2.plot(roll_x, roll_y, label='Roll Path', color='green')
    ax2.set_title('Roll Path of Golf Ball')
    ax2.set_xlabel('X Position (yards)')
    ax2.set_ylabel('Y Position (yards)')
    ax2.grid(True)
    ax2.legend()
    ax2.axis('equal')

    plt.show()


if __name__ == "__main__":
    main()
