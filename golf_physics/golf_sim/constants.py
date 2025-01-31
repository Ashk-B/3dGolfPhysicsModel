# Physical constants
BALL_MASS = 0.04593  # kg (USGA standard)
BALL_RADIUS = 0.021335  # m
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²

# Aerodynamic coefficients (empirical values)
DRAG_COEFFICIENT = 0.25
LIFT_COEFFICIENT = 0.2
MAGNUS_COEFFICIENT = 0.1

# Ground interaction
SURFACE_PROPERTIES = {
    "fairway": {"cor": 0.75, "mu": 0.15},
    "rough": {"cor": 0.35, "mu": 0.45},
    "green": {"cor": 0.60, "mu": 0.10}
}

# Add to constants.py
CLUB_LOFTS = {
    "driver": 9.5,
    "3-wood": 15,
    "5-iron": 25,
    "7-iron": 34,
    "wedge": 56,
    "putter": 3
}