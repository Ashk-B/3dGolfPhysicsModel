# physics.py
import numpy as np
from scipy.interpolate import interp1d

# Constants
BALL_MASS = 0.04593  # kg
BALL_DIAMETER = 0.04267  # m
AIR_VISCOSITY = 1.81e-5  # Pa·s
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = np.array([0, 0, -9.81])

# Reynolds number vs drag coefficient (empirical data for golf balls)
REYNOLDS_DATA = np.array([50000, 100000, 150000, 200000, 250000])
DRAG_COEFF_DATA = np.array([0.25, 0.23, 0.21, 0.19, 0.18])
drag_coeff_interp = interp1d(REYNOLDS_DATA, DRAG_COEFF_DATA, kind='quadratic')

CLUB_LOFTS = {
    # ... (same club list as previous example)
}


def mph_to_mps(mph):
    return mph * 0.44704


def meters_to_yards(m):
    return m * 1.09361


def calculate_reynolds(velocity):
    return (AIR_DENSITY * np.linalg.norm(velocity) * BALL_DIAMETER) / AIR_VISCOSITY


def aerodynamic_coefficients(velocity, spin_rate):
    re = calculate_reynolds(velocity)
    cd = np.clip(float(drag_coeff_interp(re)), 0.15, 0.25)
    cm = 0.1 * (1 - np.exp(-re / 100000))  # Magnus coefficient model
    return cd, cm


def calculate_launch_conditions(club_speed_mph, club_type, attack_angle, strike_offset_mm):
    # ... (same as previous example with improved spin calculation)
    return vel, spin


def rk4_step(pos, vel, spin, wind, dt):
    def acceleration(v, s):
        vel_rel = v - wind
        cd, cm = aerodynamic_coefficients(vel_rel, s)
        F_drag = -0.5 * cd * AIR_DENSITY * np.pi * (BALL_DIAMETER / 2) ** 2 * np.linalg.norm(vel_rel) * vel_rel
        F_magnus = 0.5 * cm * AIR_DENSITY * np.pi * (BALL_DIAMETER / 2) ** 2 * np.cross(s, vel_rel)
        return (F_drag + F_magnus) / BALL_MASS + GRAVITY

    # RK4 integration
    k1v = acceleration(vel, spin) * dt
    k1p = vel * dt

    k2v = acceleration(vel + 0.5 * k1v, spin) * dt
    k2p = (vel + 0.5 * k1v) * dt

    k3v = acceleration(vel + 0.5 * k2v, spin) * dt
    k3p = (vel + 0.5 * k2v) * dt

    k4v = acceleration(vel + k3v, spin) * dt
    k4p = (vel + k3v) * dt

    new_vel = vel + (k1v + 2 * k2v + 2 * k3v + k4v) / 6
    new_pos = pos + (k1p + 2 * k2p + 2 * k3p + k4p) / 6

    # Physics-based spin decay
    spin_decay = np.exp(-0.0001 * dt * np.linalg.norm(new_vel))
    new_spin = spin * spin_decay

    return new_pos, new_vel, new_spin


def simulate_full_shot(initial_vel, initial_spin, wind_mph, wind_dir_deg, dt=0.001):
    # Convert wind to vector with turbulence
    base_wind = mph_to_mps(wind_mph) * np.array([
        np.cos(np.radians(wind_dir_deg)),
        np.sin(np.radians(wind_dir_deg)),
        0
    ])

    # Flight simulation
    pos = np.zeros(3)
    vel = initial_vel.copy()
    spin = initial_spin.copy()
    trajectory = [pos.copy()]

    while pos[2] >= 0:
        # Add wind turbulence (10% variation)
        turbulence = 0.1 * base_wind * np.random.normal(0, 1)
        current_wind = base_wind + turbulence

        pos, vel, spin = rk4_step(pos, vel, spin, current_wind, dt)
        trajectory.append(pos.copy())

    # Advanced bounce physics
    impact_vel = vel.copy()
    normal = np.array([0, 0, 1])
    tangent = impact_vel[:2] / np.linalg.norm(impact_vel[:2] + 1e-8)

    # Normal impulse
    v_normal = np.dot(impact_vel, normal)
    j_normal = -(1 + 0.7) * BALL_MASS * v_normal  # COR = 0.7

    # Tangential impulse
    v_tangent = np.dot(impact_vel, tangent)
    j_tangent = -BALL_MASS * np.clip(v_tangent, -0.3 * v_normal, 0.3 * v_normal)  # Friction

    # Update velocity
    delta_v = (j_normal * normal + j_tangent * tangent) / BALL_MASS
    bounce_vel = impact_vel + delta_v

    # Spin change from ground contact
    torque = np.cross(BALL_DIAMETER / 2 * normal, j_tangent * tangent)
    spin += torque / (0.4 * BALL_MASS * (BALL_DIAMETER / 2) ** 2)

    # Roll simulation
    roll_speed = np.linalg.norm(bounce_vel[:2])
    roll_time = roll_speed / (0.2 * 9.81)  # Friction deceleration
    roll_distance = roll_speed * roll_time - 0.5 * 0.2 * 9.81 * roll_time ** 2

    carry = trajectory[-1][0]
    total = carry + roll_distance

    return meters_to_yards(carry), meters_to_yards(roll_distance), meters_to_yards(total)