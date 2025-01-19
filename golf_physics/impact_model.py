import math

def rpm_to_rad_s(rpm):
    """Convert Revolutions Per Minute to radians per second."""
    return rpm * (2 * math.pi) / 60


def rad_s_to_rpm(rad_s):
    """Convert radians per second to Revolutions Per Minute."""
    return rad_s * 60 / (2 * math.pi)


def compute_impact(
        club_speed_mps: float,
        club_loft_deg: float,
        club_face_angle_deg: float,
        horizontal_offset_cm: float,
        vertical_offset_cm: float,
        ball_compression_rating: float,
        base_cor: float,
        base_smash_factor: float,
        toe_gear_rpm_cm: float,
        vert_gear_rpm_cm: float
) -> dict:
    """
    Compute the initial conditions of the golf ball after impact.

    Parameters:
        club_speed_mps (float): Club speed in meters per second.
        club_loft_deg (float): Club loft angle in degrees.
        club_face_angle_deg (float): Club face angle in degrees (negative for closed).
        horizontal_offset_cm (float): Horizontal offset from center in centimeters.
        vertical_offset_cm (float): Vertical offset from center in centimeters.
        ball_compression_rating (float): Ball compression rating.
        base_cor (float): Coefficient of Restitution.
        base_smash_factor (float): Base smash factor.
        toe_gear_rpm_cm (float): Toe gear ratio (RPM per cm).
        vert_gear_rpm_cm (float): Vertical gear ratio (RPM per cm).

    Returns:
        dict: Contains launch speed, launch angles, and spin rates.
    """
    # Calculate ball speed using smash factor
    launch_speed = club_speed_mps * base_smash_factor

    # Calculate launch angles
    launch_angle_vert = club_loft_deg
    launch_angle_horiz = club_face_angle_deg

    # Calculate spin rates based on gear ratios and offsets
    # Introduce scaling factors based on club loft
    loft_factor = (club_loft_deg / 10.0)  # Example scaling factor

    backspin_rpm = (club_speed_mps * vert_gear_rpm_cm * loft_factor) / ball_compression_rating
    sidespin_rpm = (club_speed_mps * toe_gear_rpm_cm * loft_factor) / ball_compression_rating

    # Adjust spin rates based on offsets
    backspin_adjust_factor = 1.0  # Reduced from 2.0 to prevent excessive spin
    sidespin_adjust_factor = 0.5  # Reduced from 1.0 to prevent excessive spin

    # If face is square and offsets are zero, eliminate sidespin
    if club_face_angle_deg == 0 and horizontal_offset_cm == 0:
        sidespin_rpm = 0.0
    else:
        sidespin_rpm += horizontal_offset_cm * sidespin_adjust_factor

    backspin_rpm += vertical_offset_cm * backspin_adjust_factor

    # Cap spin rates to realistic maximums
    MAX_BACKSPIN_RPM = 7000
    MAX_SIDESPIN_RPM = 5000

    backspin_rpm = min(backspin_rpm, MAX_BACKSPIN_RPM)
    sidespin_rpm = min(sidespin_rpm, MAX_SIDESPIN_RPM)

    # Debug: Print initial spin rates
    print(f"Initial Spin Rates -> Backspin: {backspin_rpm:.2f} RPM, Sidespin: {sidespin_rpm:.2f} RPM")

    return {
        "launch_speed": launch_speed,
        "launch_angle_vert": launch_angle_vert,
        "launch_angle_horiz": launch_angle_horiz,
        "backspin_rpm": backspin_rpm,
        "sidespin_rpm": sidespin_rpm
    }
