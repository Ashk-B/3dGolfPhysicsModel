from .impact_model import compute_impact, calculate_air_density
from .flight_model import simulate_flight
from .bounce_roll import simulate_bounce_and_roll

import math

METERS_TO_YARDS = 1.09361  # Conversion factor


def rpm_to_rad_s(rpm):
    """Convert Revolutions Per Minute to radians per second."""
    return rpm * (2 * math.pi) / 60


def rad_s_to_rpm(rad_s):
    """Convert radians per second to Revolutions Per Minute."""
    return rad_s * 60 / (2 * math.pi)


class CompleteGolfSim:
    """
    Orchestrates the full shot: impact -> flight -> bounce/roll.
    """

    def __init__(self):
        # Ball & Physics
        self.ball_mass = 0.04593  # kg (standard golf ball mass)
        self.ball_radius = 0.02135  # meters (standard golf ball radius)
        self.gravity = 9.81  # m/s²

        # Impact defaults
        self.ball_compression_rating = 1.0
        self.base_cor = 0.83  # Coefficient of Restitution (adjust as needed)
        self.base_smash_factor = 1.5  # Updated to a standard value

        # Gear Ratios (Set based on club type in simulate_shot)
        self.vert_gear_rpm_cm = 80.0
        self.toe_gear_rpm_cm = 120.0

        # Flight
        self.drag_base = 0.2  # Decreased from 0.25 to reduce air resistance
        self.lift_base = 0.3  # Increased from 0.25 to enhance lift from backspin
        self.spin_decay_rate = 0.000005  # Further reduced for slower spin decay
        self.flight_time_step = 0.01  # Reduced for higher accuracy
        self.flight_max_steps = 1000  # Adjusted for ~10-second simulation

        # Bounce & Roll
        self.ground_restitution = 0.40  # Decreased from 0.60 for more energy loss
        self.ground_friction = 0.35  # Increased from 0.20 to apply more deceleration
        self.spin_friction_factor = 0.001  # Further reduced to slow down spin decay
        self.roll_time_step = 0.01  # Reduced for higher accuracy
        self.roll_max_steps = 2000  # Increased accordingly

    def set_gear_ratios(self, club_type: str):
        """
        Set gear ratios based on the club type.

        Parameters:
            club_type (str): Type of club (driver, iron).
        """
        club_type = club_type.lower()
        if club_type == "driver":
            self.vert_gear_rpm_cm = 60.0  # Lower for drivers
            self.toe_gear_rpm_cm = 80.0
        elif club_type == "iron":
            self.vert_gear_rpm_cm = 80.0  # Higher for irons
            self.toe_gear_rpm_cm = 120.0
        else:
            # Default to iron if unknown club type
            self.vert_gear_rpm_cm = 80.0
            self.toe_gear_rpm_cm = 120.0

    def simulate_shot(
            self,
            club_speed_mps: float,
            club_loft_deg: float,
            club_face_angle_deg: float,
            horizontal_offset_cm: float,
            vertical_offset_cm: float,
            wind_speed_mps: float,
            wind_dir_deg: float,
            temperature_c: float,
            humidity: float,
            elevation_m: float,
            surface_type: str = "fairway",  # New parameter with default
            club_type: str = "iron"  # New parameter with default
    ) -> dict:
        """
        Simulate a golf shot with specified parameters.

        Parameters:
            All parameters as previously defined.

        Returns:
            dict: Contains impact results, flight path, roll path, final position, distances, and final spin rates.
        """

        # Set gear ratios based on club type
        self.set_gear_ratios(club_type)

        # 1) Impact
        impact = compute_impact(
            club_speed_mps=club_speed_mps,
            club_loft_deg=club_loft_deg,
            club_face_angle_deg=club_face_angle_deg,
            horizontal_offset_cm=horizontal_offset_cm,
            vertical_offset_cm=vertical_offset_cm,
            ball_compression_rating=self.ball_compression_rating,
            base_cor=self.base_cor,
            base_smash_factor=self.base_smash_factor,
            toe_gear_rpm_cm=self.toe_gear_rpm_cm,
            vert_gear_rpm_cm=self.vert_gear_rpm_cm
        )

        # 2) Flight
        flight_path_m = simulate_flight(
            launch_speed=impact["launch_speed"],
            launch_angle_vert=impact["launch_angle_vert"],
            launch_angle_horiz=impact["launch_angle_horiz"],
            backspin_rpm=impact["backspin_rpm"],
            sidespin_rpm=impact["sidespin_rpm"],
            wind_speed_mps=wind_speed_mps,
            wind_dir_deg=wind_dir_deg,
            temperature_c=temperature_c,
            humidity=humidity,
            elevation_m=elevation_m,
            ball_mass=self.ball_mass,
            ball_radius=self.ball_radius,
            drag_base=self.drag_base,
            lift_base=self.lift_base,
            spin_decay_rate=self.spin_decay_rate,
            gravity=self.gravity,
            time_step=self.flight_time_step,
            max_steps=self.flight_max_steps
        )

        if not flight_path_m:
            return {
                "impact_result": impact,
                "flight_path_yards": [],
                "roll_path_yards": [],
                "final_position_yards": (0, 0, 0),
                "carry_2d_yards": 0.0,
                "roll_2d_yards": 0.0,
                "total_2d_yards": 0.0,
                "final_spin": (0, 0)
            }

        last_flight = flight_path_m[-1]  # (x, y, z, vx, vy, vz, bs, ss)
        roll_path_m = simulate_bounce_and_roll(
            last_flight_state=last_flight,
            ball_mass=self.ball_mass,
            ball_radius=self.ball_radius,  # Passed ball_radius
            gravity=self.gravity,
            ground_restitution=self.ground_restitution,
            surface_type=surface_type,  # Pass surface type
            ground_friction=self.ground_friction,
            spin_friction_factor=self.spin_friction_factor,
            time_step=self.roll_time_step,
            max_steps=self.roll_max_steps
        )

        # Convert flight_path from meters to yards
        flight_path_yards = []
        for (xm, ym, zm, vxm, vym, vzm, bspin, sspin) in flight_path_m:
            flight_path_yards.append((
                xm * METERS_TO_YARDS,
                ym * METERS_TO_YARDS,
                zm * METERS_TO_YARDS,
                vxm * METERS_TO_YARDS,  # velocity in yards/sec
                vym * METERS_TO_YARDS,
                vzm * METERS_TO_YARDS,
                bspin, sspin
            ))

        # Convert roll_path from meters to yards
        roll_path_yards = []
        final_state = last_flight
        if roll_path_m:
            for (xm, ym, zm, vxm, vym, vzm, bspin, sspin) in roll_path_m:
                roll_path_yards.append((
                    xm * METERS_TO_YARDS,
                    ym * METERS_TO_YARDS,
                    zm * METERS_TO_YARDS,
                    vxm * METERS_TO_YARDS,
                    vym * METERS_TO_YARDS,
                    vzm * METERS_TO_YARDS,
                    bspin, sspin
                ))
            final_state = roll_path_m[-1]

        # Final position in yards
        fx_m, fy_m, fz_m, _, _, _, fbspin, fsspin = final_state
        final_position_yards = (
            fx_m * METERS_TO_YARDS,
            fy_m * METERS_TO_YARDS,
            fz_m * METERS_TO_YARDS
        )

        # Calculate carry, roll, total distances in yards
        carry_2d_yards = math.sqrt((last_flight[0] * METERS_TO_YARDS) ** 2 + (last_flight[1] * METERS_TO_YARDS) ** 2)
        if roll_path_m:
            total_2d_yards = math.sqrt(
                (final_state[0] * METERS_TO_YARDS) ** 2 + (final_state[1] * METERS_TO_YARDS) ** 2)
            roll_2d_yards = total_2d_yards - carry_2d_yards
        else:
            total_2d_yards = carry_2d_yards
            roll_2d_yards = 0.0

        # Convert final spin from rad/s back to RPM for display
        final_backspin_rpm = rad_s_to_rpm(fbspin)
        final_sidespin_rpm = rad_s_to_rpm(fsspin)

        final_spin = (final_backspin_rpm, final_sidespin_rpm)  # Define final_spin here

        return {
            "impact_result": impact,
            "flight_path_yards": flight_path_yards,
            "roll_path_yards": roll_path_yards,
            "final_position_yards": final_position_yards,
            "carry_2d_yards": carry_2d_yards,
            "roll_2d_yards": roll_2d_yards,
            "total_2d_yards": total_2d_yards,
            "final_spin": final_spin  # Use the defined final_spin
        }
