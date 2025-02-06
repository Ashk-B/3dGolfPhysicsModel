import sys
from simulation import GolfShotSimulation
from plotting import plot_trajectory

def get_float(prompt, default):
    """Helper to get a float from user input with a default value."""
    try:
        value = input(f"{prompt} [{default}]: ")
        if value.strip() == "":
            return default
        return float(value)
    except ValueError:
        print("Invalid input. Using default.")
        return default

def main():
    print("Golf Shot Simulation - Interactive Mode")
    print("Press Enter to accept the default value shown in brackets.\n")

    # Impact parameters:
    club_speed_mph = get_float("Club speed at impact (mph)", 90.0)
    loft = get_float("Loft (degrees)", 10.0)
    angle_of_attack = get_float("Angle of attack (degrees)", -2.0)
    swing_path = get_float("Swing path (degrees)", 0.0)
    strike_offset_x = get_float("Strike offset X (m)", 0.0)
    strike_offset_y = get_float("Strike offset Y (m)", 0.0)

    # Environment parameters:
    air_density = get_float("Air density (kg/m³)", 1.225)
    wind_x = get_float("Wind component in x (m/s)", 0.0)
    wind_y = get_float("Wind component in y (m/s)", 0.0)
    wind_z = get_float("Wind component in z (m/s)", 0.0)

    # Ground parameters:
    restitution = get_float("Ground restitution (0-1)", 0.5)
    bounce_friction = get_float("Bounce friction (0-1)", 0.8)
    roll_friction = get_float("Roll friction (m/s²)", 1.0)

    # Ask if the user wants to plot the trajectory.
    plot_choice = input("Do you want to plot the trajectory? (y/n) [n]: ")
    do_plot = plot_choice.strip().lower() == "y"

    # Convert club speed from mph to m/s (1 mph = 0.44704 m/s).
    club_speed_mps = club_speed_mph * 0.44704

    impact_params = {
        'club_speed': club_speed_mps,
        'loft': loft,
        'angle_of_attack': angle_of_attack,
        'swing_path': swing_path,
        'strike_offset_x': strike_offset_x,
        'strike_offset_y': strike_offset_y
    }

    env_params = {
        'air_density': air_density,
        'wind': [wind_x, wind_y, wind_z]
    }

    ground_params = {
        'restitution': restitution,
        'bounce_friction': bounce_friction,
        'roll_friction': roll_friction
    }

    simulation = GolfShotSimulation(impact_params, env_params, ground_params)
    results = simulation.run()

    # Convert distances from meters to yards (1 m = 1.09361 yards).
    carry_distance_yd = results['carry_distance_m'] * 1.09361
    roll_distance_yd = results['roll_distance_m'] * 1.09361
    total_distance_yd = results['total_distance_m'] * 1.09361

    ball_speed_mph = results['initial_conditions']['ball_speed'] / 0.44704

    print("\n--- Simulation Results ---")
    print(f"Smash Factor:           {results['smash_factor']:.2f}")
    print(f"Launch Angle (deg):     {results['launch_angle_deg']:.2f}")
    print(f"Ball Speed:             {results['initial_conditions']['ball_speed']:.2f} m/s ({ball_speed_mph:.2f} mph)")
    print(f"Backspin (rad/s):       {results['backspin_rads']:.2f}")
    print(f"Sidespin (rad/s):       {results['sidespin_rads']:.2f}")
    print(f"Carry Distance:         {carry_distance_yd:.2f} yards")
    print(f"Roll Distance:          {roll_distance_yd:.2f} yards")
    print(f"Total Distance:         {total_distance_yd:.2f} yards")
    print("----------------------------\n")

    if do_plot:
        flight_positions = results['flight_data']['positions']
        bounce_positions = results['bounce_data']['positions']
        plot_trajectory(flight_positions, bounce_positions)

if __name__ == '__main__':
    main()
