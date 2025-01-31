import numpy as np
from .physics import *
from .constants import *


class GolfShotSimulator:
    def __init__(self, surface="fairway", dt=0.001):
        self.dt = dt
        self.surface = surface
        self.cor = SURFACE_PROPERTIES[surface]["cor"]
        self.mu = SURFACE_PROPERTIES[surface]["mu"]

    def simulate_shot(self, params):
        # Impact phase
        vel, spin = calculate_launch_conditions(
            params["club_speed"],
            params["loft_deg"],
            params["attack_angle_deg"],
            params["swing_path_deg"],
            params["strike_offset_mm"]
        )

        # Flight phase
        trajectory = [np.array([0, 0, 0])]
        while trajectory[-1][2] >= 0:
            new_pos, new_vel = runge_kutta_step(
                trajectory[-1], vel, spin, self.dt, params["wind"]
            )
            trajectory.append(new_pos)
            vel = new_vel
            spin *= 0.9995  # Spin decay

        # Bounce and roll
        impact_vel = vel.copy()
        impact_vel[2] *= -self.cor  # Vertical bounce
        impact_vel[:2] *= (1 - self.mu)  # Horizontal friction

        roll_distance = np.linalg.norm(impact_vel[:2]) ** 2 / (2 * self.mu * GRAVITY)

        return {
            "trajectory": np.array(trajectory),
            "carry": trajectory[-1][0],
            "total": trajectory[-1][0] + roll_distance,
            "spin": spin
        }