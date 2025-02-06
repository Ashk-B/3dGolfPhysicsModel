import numpy as np
from impact import ImpactModule
from flight import FlightModule
from bounce_roll import BounceRollModule

class GolfShotSimulation:
    """
    does simulation of a golf shots:
    """
    def __init__(self, impact_params, env_params, ground_params):
        self.impact_params = impact_params
        self.env_params = env_params
        self.ground_params = ground_params

    def run(self):
        # Impact phase.
        impact_module = ImpactModule(**self.impact_params)
        init_conditions = impact_module.compute_initial_conditions()

        # Flight phase.
        flight_module = FlightModule(init_conditions, self.env_params)
        flight_data = flight_module.simulate()
        flight_positions = flight_data['positions']
        flight_final_pos = flight_data['final_state']['position']
        carry_distance = np.linalg.norm(flight_final_pos[[0, 2]])

        # Bounce & Roll phase.
        bounce_module = BounceRollModule(flight_data['final_state'], self.ground_params)
        bounce_data = bounce_module.simulate()
        final_position = bounce_data['final_position']
        total_distance = np.linalg.norm(final_position[[0, 2]])

        # Compute roll distance (distance covered after flight contact).
        roll_distance = total_distance - carry_distance

        results = {
            'initial_conditions': init_conditions,
            'flight_data': flight_data,
            'bounce_data': bounce_data,
            'carry_distance_m': carry_distance,
            'roll_distance_m': roll_distance,
            'total_distance_m': total_distance,
            'smash_factor': init_conditions['ball_speed'] / self.impact_params['club_speed'],
            'launch_angle_deg': init_conditions['launch_angle_deg'],
            'backspin_rads': init_conditions['spin'][1],
            'sidespin_rads': init_conditions['spin'][2]
        }
        return results
