import math
from golf_physics import GolfBall

# Conversion factors
M_TO_YARD = 1 / 0.9144  # m → yards
MPH_TO_MS = 0.44704  # mph → m/s
MS_TO_MPH = 2.23694  # m/s → mph


def get_float_input(prompt, default, condition=lambda x: True):
    while True:
        inp = input(f"{prompt} (default: {default}): ").strip()
        if inp == "":
            return default
        try:
            val = float(inp)
            if not condition(val):
                print("Value out of range.")
            else:
                return val
        except:
            print("Enter a numeric value.")


def get_string_input(prompt, default, options):
    inp = input(f"{prompt} (default: {default}): ").strip().lower()
    if inp == "":
        return default
    if inp in options:
        return inp
    else:
        print(f"Invalid input. Using default ({default}).")
        return default


def compute_ground_contact(sim_data):
    if len(sim_data) < 2:
        raise ValueError("Insufficient data.")
    s_prev = sim_data[-2]
    s_last = sim_data[-1]
    z_prev, z_last = s_prev['z'], s_last['z']
    frac = z_prev / (z_prev - z_last)
    ground_x = s_prev['x'] + frac * (s_last['x'] - s_prev['x'])
    ground_y = s_prev['y'] + frac * (s_last['y'] - s_prev['y'])
    v_ground_x = s_prev['vx'] + frac * (s_last['vx'] - s_prev['vx'])
    v_ground_y = s_prev['vy'] + frac * (s_last['vy'] - s_prev['vy'])
    v_horizontal = math.sqrt(v_ground_x ** 2 + v_ground_y ** 2)
    return ground_x, ground_y, v_horizontal


def run_simulation():
    print("=== 3D Golf Ball Simulation ===\n")
    # Club inputs (mph)
    club_speed_mph = get_float_input("Club head speed (mph)", 100.0, lambda x: x > 0)
    club_speed = club_speed_mph * MPH_TO_MS
    club_loft = get_float_input("Club head loft (degrees)", 10.5, lambda x: 0 <= x <= 90)
    angle_of_attack = get_float_input("Angle of attack (degrees, +up)", 2.0)
    clubface_angle = get_float_input("Clubface angle (degrees, +open)", 0.0)
    ball_spin_rpm = get_float_input("Ball spin rate (rpm)", 3000.0, lambda x: x >= 0)

    # Weather inputs
    wind_speed_mph = get_float_input("Wind speed (mph)", 0.0)
    wind_speed = wind_speed_mph * MPH_TO_MS
    wind_direction = get_float_input("Wind direction (degrees, 0=headwind)", 0.0)
    temperature_C = get_float_input("Temperature (°C)", 20.0)
    rel_humidity = get_float_input("Relative Humidity (%)", 50.0, lambda x: 0 <= x <= 100)
    pressure_hPa = get_float_input("Air Pressure (hPa)", 1013.25)

    # Surface input
    surface = get_string_input("Surface type (fairway, rough, green)", "fairway", ["fairway", "rough", "green"])

    # Convert club → ball parameters
    smash_factor = 1.5
    ball_speed = club_speed * smash_factor  # m/s
    launch_angle = club_loft + angle_of_attack
    azimuth = clubface_angle
    ball_speed_mph = ball_speed * MS_TO_MPH

    print("\nBall parameters:")
    print(f"  Ball Speed: {ball_speed_mph:.2f} mph")
    print(f"  Launch Angle: {launch_angle:.2f}°")
    print(f"  Azimuth: {azimuth:.2f}°")
    print(f"  Ball Spin: {ball_spin_rpm:.2f} rpm")
    print("\nWeather:")
    print(f"  Wind Speed: {wind_speed_mph:.2f} mph")
    print(f"  Wind Direction: {wind_direction:.2f}°")
    print(f"  Temperature: {temperature_C:.2f} °C")
    print(f"  Relative Humidity: {rel_humidity:.2f} %")
    print(f"  Air Pressure: {pressure_hPa:.2f} hPa")
    print(f"Surface: {surface.capitalize()}\n")

    # Create ball instance with weather parameters
    ball = GolfBall(ball_speed, launch_angle, azimuth, ball_spin_rpm,
                    wind_speed, wind_direction,
                    temperature_C, rel_humidity, pressure_hPa)
    sim_data = ball.simulate(dt=0.001, total_time=10.0)

    max_height_m = max(s['z'] for s in sim_data)
    max_height_yards = max_height_m * M_TO_YARD
    ground_x, ground_y, v_horizontal = compute_ground_contact(sim_data)
    carry_m = math.sqrt(ground_x ** 2 + ground_y ** 2)
    carry_yards = carry_m * M_TO_YARD

    # Set base friction deceleration based on surface type
    base_friction = {"fairway": 4.0, "rough": 6.0, "green": 10.0}[surface]
    # Adjust friction based on relative humidity (if RH > 50, surface softens; if < 50, harder)
    # For each 1% above 50, reduce friction by 0.5%; below 50, increase by 0.5%
    adjustment = 1.0 - 0.005 * (rel_humidity - 50)
    friction = base_friction * adjustment

    roll_m = (v_horizontal ** 2) / (2 * friction)
    roll_yards = roll_m * M_TO_YARD
    total_yards = carry_yards + roll_yards
    lateral_yards = ground_y * M_TO_YARD

    summary_table = [
        ["Carry Distance", f"{carry_yards:.2f} yards"],
        ["Roll Distance", f"{roll_yards:.2f} yards"],
        ["Total Distance", f"{total_yards:.2f} yards"],
        ["Lateral Distance", f"{lateral_yards:.2f} yards"],
        ["Max Height", f"{max_height_yards:.2f} yards"],
        ["Ball Spin", f"{ball_spin_rpm:.2f} rpm"],
        ["Spin Axis", f"({ball.spin_axis[0]:.2f}, {ball.spin_axis[1]:.2f}, {ball.spin_axis[2]:.2f})"],
        ["Ball Speed", f"{ball_speed_mph:.2f} mph"],
        ["Launch Angle", f"{launch_angle:.2f}°"],
        ["Friction Deceleration", f"{friction:.2f} m/s²"]
    ]

    print("=== Summary Table ===")
    print("{:<22} {:>20}".format("Metric", "Value"))
    print("-" * 44)
    for row in summary_table:
        print("{:<22} {:>20}".format(row[0], row[1]))
    print("")


if __name__ == "__main__":
    run_simulation()
