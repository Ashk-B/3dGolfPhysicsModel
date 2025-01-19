import math

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
        spin_decay_rate: float,  # e.g., 0.00002
        gravity: float,
        time_step: float,
        max_steps: int
) -> list:
    """
    Simulate the flight of a golf ball until it lands.

    Parameters:
        launch_speed (float): Initial speed of the ball in m/s.
        launch_angle_vert (float): Vertical launch angle in degrees.
        launch_angle_horiz (float): Horizontal launch angle in degrees.
        backspin_rpm (float): Initial backspin in RPM.
        sidespin_rpm (float): Initial sidespin in RPM.
        wind_speed_mps (float): Wind speed in m/s.
        wind_dir_deg (float): Wind direction in degrees (0 = East).
        temperature_c (float): Temperature in Celsius.
        humidity (float): Relative humidity (0-1).
        elevation_m (float): Elevation above sea level in meters.
        ball_mass (float): Mass of the golf ball in kg.
        ball_radius (float): Radius of the golf ball in meters.
        drag_base (float): Base drag coefficient.
        lift_base (float): Base lift coefficient.
        spin_decay_rate (float): Rate at which spin decays.
        gravity (float): Acceleration due to gravity in m/s².
        time_step (float): Simulation time step in seconds.
        max_steps (int): Maximum number of simulation steps.

    Returns:
        list: Each element is a tuple containing (x, y, z, vx, vy, vz, backspin_rad_s, sidespin_rad_s).
    """
    flight_path = []

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
        drag = drag_base * (1 + 0.1 * (backspin_rad_s / 1000))
        lift = lift_base * (backspin_rad_s / 1000)

        # Calculate drag force
        drag_force = 0.5 * drag * (speed ** 2) * math.pi * (ball_radius ** 2)

        # Drag acceleration components
        ax_drag = -drag_force * (rel_vx) / (speed * ball_mass)
        ay_drag = -drag_force * (rel_vy) / (speed * ball_mass)
        az_drag = -drag_force * (rel_vz) / (speed * ball_mass)

        # Calculate lift force (Magnus Effect)
        lift_force = 0.5 * lift * (speed ** 2) * math.pi * (ball_radius ** 2)

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

        # Optional: Log every 10,000 steps to monitor progress
        if step % 10000 == 0 and step != 0:
            print(f"Step {step}: Position=({x:.2f}, {y:.2f}, {z:.2f}) m, "
                  f"Velocity=({vx:.2f}, {vy:.2f}, {vz:.2f}) m/s, "
                  f"Spin=({backspin_rad_s:.2f}, {sidespin_rad_s:.2f}) rad/s")

    # Debug: Final state
    print(f"Final State -> Position: ({x:.2f}, {y:.2f}, {z:.2f}) m, "
          f"Velocity: ({vx:.2f}, {vy:.2f}, {vz:.2f}) m/s, "
          f"Spin: ({backspin_rad_s:.2f}, {sidespin_rad_s:.2f}) rad/s")

    return flight_path
