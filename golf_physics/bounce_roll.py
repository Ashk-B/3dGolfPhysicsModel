import math

def simulate_bounce_and_roll(
        last_flight_state: tuple,
        ball_mass: float,
        ball_radius: float,
        gravity: float,
        ground_restitution: float,
        surface_type: str,
        ground_friction: float,
        spin_friction_factor: float,  # e.g., 0.001
        time_step: float,
        max_steps: int
) -> list:
    """
    Handle bounces & rolling friction with energy loss on each bounce.
    Includes sliding before rolling if necessary.

    Parameters:
        last_flight_state (tuple): Last state from flight simulation (x, y, z, vx, vy, vz, bspin, sspin).
        ball_mass (float): Mass of the golf ball in kg.
        ball_radius (float): Radius of the golf ball in meters.
        gravity (float): Acceleration due to gravity in m/s².
        ground_restitution (float): Coefficient of restitution for ground bounces.
        surface_type (str): Type of surface (fairway, rough, green).
        ground_friction (float): Ground friction coefficient.
        spin_friction_factor (float): Factor determining spin decay due to ground contact.
        time_step (float): Simulation time step in seconds.
        max_steps (int): Maximum number of simulation steps.

    Returns:
        list: Each element is a tuple containing (x, y, z, vx, vy, vz, backspin_rad_s, sidespin_rad_s).
    """
    roll_path = []
    xg, yg, zg, vxg, vyg, vzg, bspin, sspin = last_flight_state

    # Define friction and restitution based on surface type
    surface_properties = {
        "fairway": {"friction": 0.35, "restitution": 0.40},
        "rough": {"friction": 0.30, "restitution": 0.35},
        "green": {"friction": 0.45, "restitution": 0.30}
    }

    props = surface_properties.get(surface_type.lower(), {"friction": 0.35, "restitution": 0.40})
    current_friction = props["friction"]
    current_restitution = props["restitution"]

    for step in range(max_steps):
        roll_path.append((xg, yg, zg, vxg, vyg, vzg, bspin, sspin))
        speed_h = math.sqrt(vxg ** 2 + vyg ** 2)

        # Termination condition: both horizontal and vertical speeds are negligible
        if speed_h < 0.05 and abs(vzg) < 0.05:
            break

        if zg <= 0.0:
            if abs(vzg) > 0.1:
                # **Bounce Phase**
                # Invert and scale vertical velocity based on restitution
                vzg = -vzg * current_restitution

                # **Energy Loss in Horizontal Velocity Due to Bounce**
                horizontal_energy_loss = 0.3  # Reduced from 0.5 to prevent excessive energy loss
                reduction_factor = math.sqrt(1 - horizontal_energy_loss)  # ~0.588
                vxg *= reduction_factor
                vyg *= reduction_factor

                # **Apply Friction During Bounce to Further Reduce Horizontal Velocity**
                additional_friction = 0.05  # Reduced from 0.1 to prevent excessive energy loss
                vxg *= (1 - additional_friction)
                vyg *= (1 - additional_friction)

                # **Apply Spin Decay Due to Ground Contact**
                spin_decay_ground = spin_friction_factor * time_step
                bspin *= (1.0 - spin_decay_ground)
                sspin *= (1.0 - spin_decay_ground)

                # **Optional: Log the bounce for debugging**
                if step % 1000 == 0:
                    print(f"Bounce {step}: vxg={vxg:.4f} m/s, vyg={vyg:.4f} m/s, vzg={vzg:.4f} m/s, "
                          f"bspin={bspin:.2f} rad/s, sspin={sspin:.2f} rad/s")
            else:
                # **Rolling Phase**
                # Determine if the ball is sliding or rolling
                # Sliding occurs if the horizontal speed is greater than rotational speed * radius
                # Assuming the ball starts rolling without slipping when v = ω * r
                rotational_speed = bspin * ball_radius  # v = ω * r
                if speed_h > rotational_speed + 0.1:  # Increased tolerance
                    # **Sliding Phase**
                    # Apply sliding friction
                    sliding_friction = current_friction * gravity
                    ax = -sliding_friction * (vxg / speed_h)
                    ay = -sliding_friction * (vyg / speed_h)

                    # Update velocities
                    vxg += ax * time_step
                    vyg += ay * time_step

                    # Apply spin decay due to sliding
                    spin_decay = spin_friction_factor * time_step
                    bspin *= (1.0 - spin_decay)
                    sspin *= (1.0 - spin_decay)

                    # Update positions
                    xg += vxg * time_step
                    yg += vyg * time_step
                    zg = 0.0
                    continue
                else:
                    # **Pure Rolling Phase**
                    rolling_resistance = current_friction * ball_mass * gravity * 1.2  # 20% increase

                    if speed_h > 1e-9:
                        # Normalize velocity to get direction
                        dir_x = vxg / speed_h
                        dir_y = vyg / speed_h

                        # Apply rolling resistance (deceleration)
                        ax = -rolling_resistance * dir_x / ball_mass
                        ay = -rolling_resistance * dir_y / ball_mass

                        # Update velocities
                        vxg += ax * time_step
                        vyg += ay * time_step

                        # Prevent velocities from reversing due to over-deceleration
                        if (vxg * dir_x) < 0:
                            vxg = 0.0
                        if (vyg * dir_y) < 0:
                            vyg = 0.0
                    else:
                        vxg, vyg = 0.0, 0.0

                    # Apply spin decay during rolling
                    spin_decay = spin_friction_factor * time_step
                    bspin *= (1.0 - spin_decay)
                    sspin *= (1.0 - spin_decay)

                    # Set vertical velocity to zero as the ball is rolling on the ground
                    vzg = 0.0

                    # Update positions
                    xg += vxg * time_step
                    yg += vyg * time_step
                    zg = 0.0
                    continue

        else:
            # **Ball is in Mid-Bounce (Still in the Air)**
            # Apply gravity to vertical velocity
            vzg -= gravity * time_step

        # **Update Position Based on Current Velocities**
        xg += vxg * time_step
        yg += vyg * time_step
        zg += vzg * time_step

    return roll_path
