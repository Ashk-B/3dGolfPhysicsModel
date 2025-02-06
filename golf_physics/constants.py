import numpy as np

GRAVITY = np.array([0, -9.81, 0])           # m/s², downward
BALL_RADIUS = 0.02135                       # m, standard golf ball radius (~42.67 mm diameter)
BALL_MASS = 0.04593                         # kg, standard golf ball mass
BALL_AREA = np.pi * BALL_RADIUS**2          # m², cross-sectional area
DEFAULT_DRAG_COEFF = 0.25                   # dimensionless
DEFAULT_MAGNUS_COEFF = 1e-4                 # tuning parameter for Magnus (lift) force
DEFAULT_SMASH_FACTOR = 1.45                 # typical value for driver shots
TIME_STEP = 0.005                           # seconds (integration dt)
