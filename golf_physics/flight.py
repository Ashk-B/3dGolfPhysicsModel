import numpy as np
from constants import GRAVITY, BALL_MASS, BALL_AREA, TIME_STEP, DEFAULT_DRAG_COEFF, DEFAULT_MAGNUS_COEFF


class FlightModule:
    """
    simulates ball flight using Euler integration.

    it accounts for gravity, aerodynamic drag, and a Magnus (lift) force.
    """

    def __init__(self, initial_conditions, env_params, dt=TIME_STEP):
        self.dt = dt
        self.pos = initial_conditions['position']
        self.vel = initial_conditions['velocity']
        self.spin = initial_conditions['spin']
        self.env = env_params

        # Environment parameters (with defaults):
        self.air_density = self.env.get('air_density', 1.225)
        self.wind = np.array(self.env.get('wind', [0.0, 0.0, 0.0]))
        self.drag_coefficient = self.env.get('drag_coefficient', DEFAULT_DRAG_COEFF)
        self.magnus_coefficient = self.env.get('magnus_coefficient', DEFAULT_MAGNUS_COEFF)

        # Lists to record the trajectory.
        self.positions = [self.pos.copy()]
        self.velocities = [self.vel.copy()]
        self.times = [0.0]

    def aerodynamic_forces(self, velocity, spin):
        """
        Computes drag and Magnus (lift) forces.

        Drag: F_drag = -0.5 * rho * v² * C_d * A * unit(v)
        Magnus: F_magnus = magnus_coefficient * (spin x velocity)
        """
        v_rel = velocity - self.wind  # relative velocity to the air
        v_mag = np.linalg.norm(v_rel)
        if v_mag < 1e-6:
            drag = np.array([0.0, 0.0, 0.0])
        else:
            drag = -0.5 * self.air_density * v_mag ** 2 * self.drag_coefficient * BALL_AREA * (v_rel / v_mag)
        magnus = self.magnus_coefficient * np.cross(spin, velocity)
        return drag + magnus

    def simulate(self):
        """
        Runs the flight simulation until the ball reaches ground level (y <= 0).
        """
        t = 0.0
        while self.pos[1] >= 0:
            aero = self.aerodynamic_forces(self.vel, self.spin)
            acceleration = GRAVITY + aero / BALL_MASS
            self.vel = self.vel + acceleration * self.dt
            self.pos = self.pos + self.vel * self.dt
            t += self.dt

            self.positions.append(self.pos.copy())
            self.velocities.append(self.vel.copy())
            self.times.append(t)

            # Break if the ball is moving downward past ground level.
            if self.pos[1] < 0 and self.vel[1] < 0:
                break

        # Interpolate to better estimate ground contact (y = 0).
        pos_last = self.positions[-2]
        pos_final = self.positions[-1]
        y1, y2 = pos_last[1], pos_final[1]
        if y1 != y2:
            frac = y1 / (y1 - y2)
            ground_pos = pos_last + frac * (pos_final - pos_last)
        else:
            ground_pos = pos_final.copy()

        final_state = {
            'position': ground_pos,
            'velocity': self.velocities[-2]  # approximate pre-bounce velocity
        }
        return {
            'positions': np.array(self.positions),
            'velocities': np.array(self.velocities),
            'times': np.array(self.times),
            'final_state': final_state
        }
