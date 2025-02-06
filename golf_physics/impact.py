import numpy as np
from constants import DEFAULT_SMASH_FACTOR


class ImpactModule:
    """
    Computes initial ball conditions (velocity, spin, etc.) based on club and strike parameters.

    Inputs:
      - club_speed: Club speed in m/s (converted from mph in the UI)
      - loft: Loft of the club (degrees)
      - angle_of_attack: Angle of attack (degrees)
      - swing_path: Swing path angle (degrees)
      - strike_offset_x: Horizontal strike offset (m)
      - strike_offset_y: Vertical strike offset (m)
      - smash_factor: Ratio of ball speed to club speed (default provided)
    """

    def __init__(self, club_speed, loft, angle_of_attack, swing_path,
                 strike_offset_x, strike_offset_y, smash_factor=DEFAULT_SMASH_FACTOR):
        self.club_speed = club_speed
        self.loft = loft
        self.angle_of_attack = angle_of_attack
        self.swing_path = swing_path
        self.strike_offset_x = strike_offset_x
        self.strike_offset_y = strike_offset_y
        self.smash_factor = smash_factor

    def compute_initial_conditions(self):
        # Compute ball speed (m/s) from club speed and smash factor.
        ball_speed = self.club_speed * self.smash_factor

        # Effective launch angle (degrees): starting with loft, then adjusting by angle_of_attack.
        launch_angle_deg = self.loft + 0.2 * self.angle_of_attack
        launch_angle = np.deg2rad(launch_angle_deg)

        # Initial velocity vector (x: forward, y: vertical, z: lateral).
        v0_x = ball_speed * np.cos(launch_angle)
        v0_y = ball_speed * np.sin(launch_angle)
        v0_z = 0.0  # No initial lateral velocity; spin may later induce curvature.
        velocity = np.array([v0_x, v0_y, v0_z])

        # Spin generation (simplified):
        # Backspin (rad/s) influenced by club speed, loft, and vertical offset.
        # Sidespin (rad/s) influenced by swing path and horizontal offset.
        backspin = 3000 * (self.club_speed / 40) * (self.loft / 10) - 1000 * self.strike_offset_y
        sidespin = 500 * np.deg2rad(self.swing_path) + 800 * self.strike_offset_x
        spin = np.array([0.0, backspin, sidespin])

        # Starting position (ball on tee, slightly above ground).
        position = np.array([0.0, 0.05, 0.0])

        return {
            'position': position,
            'velocity': velocity,
            'spin': spin,
            'launch_angle_deg': launch_angle_deg,
            'ball_speed': ball_speed
        }
