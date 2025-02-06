import argparse
from simulation import GolfShotSimulation
from plotting import plot_trajectory


def parse_arguments():
    parser = argparse.ArgumentParser(description="Test the golf shot simulation.")

    # impact parameters
    parser.add_argument("--club_speed", type=float, default=90.0,
                        help="Club speed at impact (mph)")
    parser.add_argument("--loft", type=float, default=10.0,
                        help="Loft of the club (degrees)")
    parser.add_argument("--angle_of_attack", type=float, default=-2.0,
                        help="Angle of attack (degrees)")
    parser.add_argument("--swing_path", type=float, default=0.0,
                        help="Swing path angle (degrees)")
    parser.add_argument("--strike_offset_x", type=float, default=0.0,
                        help="Horizontal strike offset (m)")
    parser.add_argument("--strike_offset_y", type=float, default=0.0,
                        help="Vertical strike offset (m)")

    # environment parameters.
    parser.add_argument("--air_density", type=float, default=1.225,
                        help="Air density (kg/m³)")
    parser.add_argument("--wind_x", type=float, default=0.0,
                        help="Wind component in x (m/s)")
    parser.add_argument("--wind_y", type=float, default=0.0,
                        help="Wind component in y (m/s)")
    parser.add_argument("--wind_z", type=float, default=0.0,
                        help="Wind component in z (m/s)")

    # ground parameters.
    parser.add_argument("--restitution", type=float, default=0.5,
                        help="Coefficient of restitution for bounce")
    parser.add_argument("--bounce_friction", type=float, default=0.8,
                        help="Friction factor at bounce reducing horizontal speed")
    parser.add_argument("--roll_friction", type=float, default=1.0,
                        help="Rolling friction deceleration (m/s²)")

    # plot
    parser.add_argument("--plot", action="store_true", help="Plot the 3D trajectory")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # convert club speed from mph to m/s. (1 mph = 0.44704 m/s)
    club_speed_mps = args.club_speed * 0.44704

    impact_params = {
        'club_speed': club_speed_mps,
        'loft': args.loft,
        'angle_of_attack': args.angle_of_attack,
        'swing_path': args.swing_path,
        'strike_offset_x': args.strike_offset_x,
        'strike_offset_y': args.strike_offset_y
    }

    env_params = {
        'air_density': args.air_density,
        'wind': [args.wind_x, args.wind_y, args.wind_z]
    }

    ground_params = {
        'restitution': args.restitution,
        'bounce_friction': args.bounce_friction,
        'roll_friction': args.roll_friction
    }

    simulation = GolfShotSimulation(impact_params, env_params, ground_params)
    results = simulation.run()

    # convert distances from meters to yards (1 m = 1.09361 yards).
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

    if args.plot:
        flight_positions = results['flight_data']['positions']
        bounce_positions = results['bounce_data']['positions']
        plot_trajectory(flight_positions, bounce_positions)


if __name__ == '__main__':
    main()
