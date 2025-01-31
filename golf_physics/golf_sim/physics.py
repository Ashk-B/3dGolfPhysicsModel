# physics.py
import numpy as np

# Constants
BALL_MASS = 0.04593  # kg
BALL_RADIUS = 0.021335  # m
GRAVITY = np.array([0, 0, -9.81])
AIR_DENSITY = 1.225
DRAG_COEFFICIENT = 0.25
MAGNUS_COEFFICIENT = 0.1

CLUB_LOFTS = {
    "driver": 9.5,
    "5-iron": 25,
    "wedge": 56
}


def calculate_launch_conditions(club_speed, club_type, attack_angle, strike_offset_mm):
    loft_deg = CLUB_LOFTS[club_type]
    loft = np.radians(loft_deg + 0.3 * attack_angle)
    strike_offset = strike_offset_mm / 1000  # mm to meters

    # Smash factor (simplified)
    ball_speed = club_speed * (1.45 - 0.008 * abs(strike_offset_mm))

    # Velocity vector
    vx = ball_speed * np.cos(loft)
    vz = ball_speed * np.sin(loft)

    # Spin (backspin only for simplicity)
    backspin_rpm = (club_speed * np.tan(loft) * strike_offset) * 60 / (2 * np.pi)

    return np.array([vx, 0, vz]), np.array([0, 0, backspin_rpm])


def aerodynamic_forces(velocity, spin_rpm):
    vel_mag = np.linalg.norm(velocity)
    if vel_mag == 0:
        return np.zeros(3)

    # Drag
    F_drag = -0.5 * AIR_DENSITY * DRAG_COEFFICIENT * np.pi * BALL_RADIUS ** 2 * vel_mag * velocity

    # Magnus (simplified to side force)
    spin_rads = np.radians(spin_rpm) * (2 * np.pi / 60)
    F_magnus = 0.5 * AIR_DENSITY * MAGNUS_COEFFICIENT * np.pi * BALL_RADIUS ** 2 * np.cross(spin_rads, velocity)

    return F_drag + F_magnus


def simulate_trajectory(initial_vel, initial_spin, dt=0.01):
    trajectory = [np.zeros(3)]
    vel = initial_vel.copy()
    spin = initial_spin.copy()

    while trajectory[-1][2] >= 0:
        F = aerodynamic_forces(vel, spin)
        accel = F / BALL_MASS + GRAVITY
        vel += accel * dt
        trajectory.append(trajectory[-1] + vel * dt)
        spin *= 0.999  # Simplified spin decay

    return np.array(trajectory)