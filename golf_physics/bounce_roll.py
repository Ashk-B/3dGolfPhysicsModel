# bounce_roll.py
import numpy as np
from constants import TIME_STEP


class BounceRollModule:
    """
    simulates bounce and roll after the ball hits the ground.
    """

    def __init__(self, flight_final_state, ground_params, dt=TIME_STEP):
        self.dt = dt
        self.pos = flight_final_state['position']
        self.vel = flight_final_state['velocity']
        self.ground = ground_params

        # Ground parameters with defaults.
        self.restitution = self.ground.get('restitution', 0.5)
        self.bounce_friction = self.ground.get('bounce_friction', 0.8)
        self.roll_friction = self.ground.get('roll_friction', 1.0)  # deceleration (m/s²)

        self.positions = [self.pos.copy()]
        self.times = [0.0]  # local time for bounce-roll phase

    def simulate(self):
        # Bounce: Adjust the vertical velocity and reduce horizontal speed.
        v_in = self.vel.copy()
        v_bounce_y = -self.restitution * v_in[1]
        v_bounce_x = self.bounce_friction * v_in[0]
        v_bounce_z = self.bounce_friction * v_in[2]
        v_after = np.array([v_bounce_x, v_bounce_y, v_bounce_z])
        self.vel = v_after.copy()

        # Set position to ground level.
        self.pos[1] = 0.0
        self.positions.append(self.pos.copy())
        self.times.append(self.dt)

        # Roll: Simulate deceleration on the horizontal plane until the ball comes to rest.
        horizontal_speed = np.linalg.norm(self.vel[[0, 2]])
        t_roll = 0.0
        while horizontal_speed > 0.1:  # threshold (m/s) for stopping
            decel = self.roll_friction
            horizontal_speed = max(0.0, horizontal_speed - decel * self.dt)
            if horizontal_speed == 0.0:
                self.vel[0] = 0.0
                self.vel[2] = 0.0
            else:
                direction = np.array([self.vel[0], self.vel[2]])
                direction_norm = np.linalg.norm(direction)
                if direction_norm > 0:
                    direction = direction / direction_norm
                self.vel[0] = horizontal_speed * direction[0]
                self.vel[2] = horizontal_speed * direction[1]

            # Update horizontal position.
            self.pos[0] += self.vel[0] * self.dt
            self.pos[2] += self.vel[2] * self.dt
            t_roll += self.dt

            self.positions.append(self.pos.copy())
            self.times.append(t_roll)

        final_position = self.pos.copy()
        return {
            'positions': np.array(self.positions),
            'times': np.array(self.times),
            'final_position': final_position
        }
