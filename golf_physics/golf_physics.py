import math
import numpy as np


class GolfBall:
    def __init__(self, initial_speed, launch_angle_deg, azimuth_deg, spin_rpm,
                 wind_speed=0.0, wind_direction_deg=0.0,
                 temperature_C=20.0, relative_humidity=50.0, pressure_hPa=1013.25):
        # Constants
        self.g = 9.81  # m/s^2
        self.mass = 0.04593  # kg
        self.radius = 0.02135  # m
        self.A = math.pi * self.radius ** 2
        self.Cd = 0.25

        self.initial_speed = initial_speed
        self.launch_angle_deg = launch_angle_deg
        self.azimuth_deg = azimuth_deg
        self.spin_rpm = spin_rpm

        # Convert angles to radians
        self.launch_angle = math.radians(launch_angle_deg)
        self.azimuth = math.radians(azimuth_deg)
        # Initial velocity components (m/s)
        self.v0x = initial_speed * math.cos(self.launch_angle) * math.cos(self.azimuth)
        self.v0y = initial_speed * math.cos(self.launch_angle) * math.sin(self.azimuth)
        self.v0z = initial_speed * math.sin(self.launch_angle)
        self.initial_velocity = np.array([self.v0x, self.v0y, self.v0z])
        self.initial_position = np.array([0.0, 0.0, 0.0])
        # Spin conversion
        self.spin_rate_rad = spin_rpm * 2 * math.pi / 60.0
        horizontal_speed = np.linalg.norm(self.initial_velocity[:2])
        if horizontal_speed > 1e-6:
            self.spin_axis = np.array([self.initial_velocity[1],
                                       -self.initial_velocity[0], 0.0]) / horizontal_speed
        else:
            self.spin_axis = np.array([0.0, 0.0, 0.0])
        self.spin_vector = self.spin_rate_rad * self.spin_axis

        # Weather: wind (m/s) and its direction (radians)
        self.wind_speed = wind_speed
        self.wind_direction_rad = math.radians(wind_direction_deg)
        # Compute air density from weather parameters
        # Temperature (K), Pressure (Pa)
        T = temperature_C + 273.15
        p_total = pressure_hPa * 100
        # Saturation vapor pressure (Pa)
        p_sat = 610.94 * math.exp((17.625 * temperature_C) / (temperature_C + 243.04))
        p_v = (relative_humidity / 100.0) * p_sat
        p_d = p_total - p_v
        R_d = 287.05  # J/(kg*K)
        R_v = 461.5  # J/(kg*K)
        self.rho = (p_d / (R_d * T)) + (p_v / (R_v * T))

    def simulate(self, dt=0.001, total_time=10.0):
        sim_data = []
        t = 0.0
        state = np.concatenate((self.initial_position, self.initial_velocity))

        # Derivative: [dx,dy,dz,dvx,dvy,dvz]
        def deriv(state):
            pos = state[0:3]
            vel = state[3:6]
            # Wind vector (m/s) in horizontal plane
            wind_vector = self.wind_speed * np.array([
                math.cos(self.wind_direction_rad),
                math.sin(self.wind_direction_rad),
                0.0
            ])
            # Relative velocity (m/s)
            v_rel = vel - wind_vector
            speed_rel = np.linalg.norm(v_rel)
            vhat = v_rel / speed_rel if speed_rel >= 1e-6 else np.zeros(3)
            # Drag force using relative speed
            F_drag = -0.5 * self.Cd * self.rho * self.A * speed_rel ** 2 * vhat
            # Magnus (lift)
            S = (self.spin_rate_rad * self.radius) / speed_rel if speed_rel >= 1e-6 else 0.0
            Cl = 0.225 + 0.425 * S
            omega_hat = self.spin_vector / np.linalg.norm(self.spin_vector) if np.linalg.norm(
                self.spin_vector) >= 1e-6 else np.zeros(3)
            F_magnus = 0.5 * self.rho * self.A * speed_rel ** 2 * Cl * np.cross(omega_hat, vhat)
            # Gravity
            F_gravity = np.array([0.0, 0.0, -self.mass * self.g])
            F_total = F_drag + F_magnus + F_gravity
            acceleration = F_total / self.mass
            return np.concatenate((vel, acceleration))

        while t <= total_time:
            sim_data.append({
                'time': t,
                'x': state[0],
                'y': state[1],
                'z': state[2],
                'vx': state[3],
                'vy': state[4],
                'vz': state[5],
                'speed': np.linalg.norm(state[3:6])
            })
            if state[2] < 0 and t > 0:
                break
            k1 = dt * deriv(state)
            k2 = dt * deriv(state + 0.5 * k1)
            k3 = dt * deriv(state + 0.5 * k2)
            k4 = dt * deriv(state + k3)
            state = state + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
            t += dt
        return sim_data
