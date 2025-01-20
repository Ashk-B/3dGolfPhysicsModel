import math

def rpm_to_rad_s(rpm):
    # Convert Revolutions Per Minute to radians per second
    return rpm * (2 * math.pi) / 60


def rad_s_to_rpm(rad_s):
    # convert radians per second to Revolutions Per Minute
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
    # initial conditions of the golf ball after impact

    # Calculate ball speed using smash factor
    launch_speed = club_speed_mps * base_smash_factor

    # Debug: Print launch speed
    print(f"Launch Speed: {launch_speed:.2f} m/s")

    # Calculate launch angles
    launch_angle_vert = club_loft_deg  # add calculation with respect to angle of attack
    launch_angle_horiz = club_face_angle_deg

    # Calculate spin rates based on gear ratios and offsets
    loft_factor = (club_loft_deg / 10.0)  # change to also take into account angle of attack

    backspin_rpm = (club_speed_mps * vert_gear_rpm_cm * loft_factor) / ball_compression_rating
    sidespin_rpm = (club_speed_mps * toe_gear_rpm_cm * loft_factor) / ball_compression_rating

    # Adjust spin rates based on offsets
    backspin_adjust_factor = 1.0
    sidespin_adjust_factor = 0.5

    # If face is perfectly square and offsets are zero, no sidespin
    if club_face_angle_deg == 0 and horizontal_offset_cm == 0:
        sidespin_rpm = 0.0
    else:
        # sidespin based on face angle
        # Open Face makes left-to-right sidespin
        # Closed Face makes right-to-left sidespin
        face_angle_factor = club_face_angle_deg / 10.0
        sidespin_rpm += face_angle_factor * 200.0

        # adjust based on horizontal offset
        sidespin_rpm += horizontal_offset_cm * sidespin_adjust_factor

    backspin_rpm += vertical_offset_cm * backspin_adjust_factor

    # Cap spin rates to realistic maximums
    MAX_BACKSPIN_RPM = 50000  # Upper limit for irons
    MAX_SIDESPIN_RPM = 3000  # Reduced for more realistic sidespin

    backspin_rpm = min(backspin_rpm, MAX_BACKSPIN_RPM)
    sidespin_rpm = max(min(sidespin_rpm, MAX_SIDESPIN_RPM), -MAX_SIDESPIN_RPM)  # Allow negative sidespin

    # Debug: Print initial spin rates
    print(f"Initial Spin Rates -> Backspin: {backspin_rpm:.2f} RPM, Sidespin: {sidespin_rpm:.2f} RPM")

    return {
        "launch_speed": launch_speed,
        "launch_angle_vert": launch_angle_vert,
        "launch_angle_horiz": launch_angle_horiz,
        "backspin_rpm": backspin_rpm,
        "sidespin_rpm": sidespin_rpm
    }


def calculate_air_density(temperature_c, humidity, elevation_m):
    # calculate air density based on temperature, humidity, and elevation using the ideal gas law

    R_d = 287.05  # J/(kg·K) for dry air
    R_v = 461.495  # J/(kg·K) for water vapor
    T = temperature_c + 273.15  # Convert to Kelvin

    # Calculate pressure at elevation using barometric formula
    P0 = 101325  # Standard sea level pressure in Pascals
    P = P0 * math.exp(-elevation_m / 8400)  # Simplified barometric formula

    # Calculate saturation vapor pressure using Tetens formula
    e_s = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5)) * 100  # in Pascals

    # Actual vapor pressure
    e = humidity * e_s

    # Partial pressures
    P_d = P - e
    P_v = e

    # Air density calculation
    rho = (P_d / (R_d * T)) + (P_v / (R_v * T))
    return rho
