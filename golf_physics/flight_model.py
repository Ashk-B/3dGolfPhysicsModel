import math
from .impact_model import calculate_air_density  # Ensure correct import based on project structure


def rpm_to_rad_s(rpm):
    """Convert Revolutions Per Minute to radians per second."""
    return rpm * (2 * math.pi) / 60


def rad_s_to_rpm(rad_s):
    """Convert radians per second to Revolutions Per Minute."""
    return rad_s * 60 / (2 * math.pi)


def simulate_flight(
        launch_speed: float,
        launch_angle_vert: float,  # Degrees
        launch_angle_horiz: float,  # Degrees
        backspin_rpm: float,
        sidespin_rpm: float,
        wind_speed_mps: float,
        wind_dir_deg: float,
        temperature_c: float,
        humidity: float,
        elevation_m: float,
        ball_mass: float,
        ball_radius: float,
        drag_base: float,
        lift_base: float,
        spin_decay_rate: float,  # e.g., 0.000005
        gravity: float,
        time_step: float,
        max_steps: int
) -> list:

    # Simulate the flight of a golf ball until it lands.
    flight_path = []

    # Calculate air density
    rho = calculate_air_density(temperature_c, humidity, elevation_m)
    print(f"Air Density: {rho:.4f} kg/m³")

    # Convert angles from degrees to radians
    launch_angle_vert_rad = math.radians(launch_angle_vert)
    launch_angle_horiz_rad = math.radians(launch_angle_horiz)
    wind_dir_rad = math.radians(wind_dir_deg)

    # Initial velocities
    vx = launch_speed * math.cos(launch_angle_vert_rad) * math.cos(launch_angle_horiz_rad)
    vy = launch_speed * math.cos(launch_angle_vert_rad) * math.sin(launch_angle_horiz_rad)
    vz = launch_speed * math.sin(launch_angle_vert_rad)

    # Debug: Print initial velocities
    print(f"Initial Velocities -> vx: {vx:.2f} m/s, vy: {vy:.2f} m/s, vz: {vz:.2f} m/s")

    # Wind velocities
    wind_vx = wind_speed_mps * math.cos(wind_dir_rad)
    wind_vy = wind_speed_mps * math.sin(wind_dir_rad)

    # Convert spin from RPM to rad/s
    backspin_rad_s = rpm_to_rad_s(backspin_rpm)
    sidespin_rad_s = rpm_to_rad_s(sidespin_rpm)

    # Initial position
    x, y, z = 0.0, 0.0, 0.0

    for step in range(max_steps):
        # Record the current state
        flight_path.append((x, y, z, vx, vy, vz, backspin_rad_s, sidespin_rad_s))

        # Termination condition: ball has hit the ground
        if z < 0:
            break

        # Relative velocities
        rel_vx = vx - wind_vx
        rel_vy = vy - wind_vy
        rel_vz = vz  # Assuming wind doesn't affect vertical velocity

        # Calculate the speed
        speed = math.sqrt(rel_vx ** 2 + rel_vy ** 2 + rel_vz ** 2)

        # Avoid division by zero
        if speed == 0:
            speed = 1e-6

        # Calculate drag and lift coefficients based on spin
        C_d = drag_base
        C_l = lift_base * (backspin_rad_s / 1000)  # Adjusted lift coefficient

        # Calculate drag and lift forces with accurate coefficients
        drag_force = 0.5 * rho * C_d * (speed ** 2) * math.pi * (ball_radius ** 2)
        lift_force = 0.5 * rho * C_l * (speed ** 2) * math.pi * (ball_radius ** 2)

        # Debug: Print forces every 100 steps
        if step % 100 == 0:
            print(f"Step {step}: Drag Force: {drag_force:.2f} N, Lift Force: {lift_force:.2f} N")

        # Drag acceleration components
        ax_drag = -drag_force * (rel_vx) / (speed * ball_mass)
        ay_drag = -drag_force * (rel_vy) / (speed * ball_mass)
        az_drag = -drag_force * (rel_vz) / (speed * ball_mass)

        # Lift acceleration
        az_lift = lift_force / ball_mass

        # Gravity acceleration
        az_gravity = -gravity

        # Update velocities
        vx += (ax_drag) * time_step
        vy += (ay_drag) * time_step
        vz += (az_drag + az_lift + az_gravity) * time_step

        # Update positions
        x += vx * time_step
        y += vy * time_step
        z += vz * time_step

        # Apply spin decay
        backspin_rad_s *= (1 - spin_decay_rate * time_step)
        sidespin_rad_s *= (1 - spin_decay_rate * time_step)

        # Debug: Print state every 100 steps
        if step % 100 == 0:
            print(f"Step {step}: Velocity -> vx: {vx:.2f} m/s, vy: {vy:.2f} m/s, vz: {vz:.2f} m/s")
            print(f"Step {step}: Position -> x: {x:.2f} m, y: {y:.2f} m, z: {z:.2f} m")

    # Debug: Final state
    print(f"Final State -> Position: ({x:.2f}, {y:.2f}, {z:.2f}) m, "
          f"Velocity: ({vx:.2f}, {vy:.2f}, {vz:.2f}) m/s, "
          f"Spin: ({backspin_rad_s:.2f}, {sidespin_rad_s:.2f}) rad/s")

    return flight_path
