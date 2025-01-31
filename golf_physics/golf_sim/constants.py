# Club lofts (degrees) - PGA standard
CLUB_LOFTS = {
    "driver": 9.5,
    "3-wood": 15,
    "5-wood": 18,
    "2-iron": 18,
    "3-iron": 21,
    "4-iron": 24,
    "5-iron": 27,
    "6-iron": 30,
    "7-iron": 34,
    "8-iron": 38,
    "9-iron": 42,
    "pitching-wedge": 46,
    "sand-wedge": 56,
    "lob-wedge": 60,
    "putter": 3
}

# Physics constants
BALL_MASS = 0.04593  # kg
BALL_RADIUS = 0.021335  # m
GRAVITY = 9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³
DRAG_COEFFICIENT = 0.25
MAGNUS_COEFFICIENT = 0.1

# Ground interaction (fairway default)
BOUNCE_COR = 0.7  # Coefficient of restitution
GROUND_MU = 0.2   # Friction coefficient