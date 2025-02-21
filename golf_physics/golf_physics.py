import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Constants
m = 0.04593  # Golf ball mass (kg)
r = 0.021335  # Radius (m)
A = np.pi * r ** 2  # Cross-sectional area (m²)
rho = 1.225  # Air density (kg/m³)
C_d = 0.25  # Drag coefficient
C_l = 0.2  # Lift coefficient (adjust based on spin)
g = 9.81  # Gravity (m/s²)


def trajectory_model(t, state, omega):
    x, y, z, vx, vy, vz = state
    v = np.array([vx, vy, vz])
    speed = np.linalg.norm(v)

    # Drag force (opposite velocity direction)
    F_drag = -0.5 * rho * C_d * A * speed * v if speed > 0 else np.zeros(3)

    # Magnus force (perpendicular to velocity and spin)
    if np.linalg.norm(omega) == 0 or speed == 0:
        F_magnus = np.zeros(3)
    else:
        F_magnus = 0.5 * rho * C_l * A * r * np.cross(v, omega)

    # Gravity force (downward)
    F_gravity = np.array([0.0, 0.0, -m * g])

    # Total acceleration
    a = (F_drag + F_magnus + F_gravity) / m
    return [vx, vy, vz, a[0], a[1], a[2]]


def simulate_golf_shot(v0, launch_angle_deg, spin_rpm, height=0.0, dt=0.01):
    theta = np.radians(launch_angle_deg)
    omega_mag = spin_rpm * (2 * np.pi / 60)  # Convert RPM to rad/s
    omega = np.array([0.0, omega_mag, 0.0])  # Backspin around y-axis

    # Initial velocity components
    vx0 = v0 * np.cos(theta)
    vz0 = v0 * np.sin(theta)
    initial_state = [0, 0, height, vx0, 0, vz0]

    # Stop simulation when ball hits the ground
    def ground_event(t, state):
        return state[2]

    ground_event.terminal = True
    ground_event.direction = -1

    # Solve the ODE
    sol = solve_ivp(trajectory_model, (0, 20), initial_state, args=(omega,),
                    events=ground_event, method='RK45', max_step=dt)

    return sol.t, sol.y[0], sol.y[1], sol.y[2]


def get_float_input(prompt, default=None):
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():
    print("Golf Trajectory Calculator")
    print("--------------------------")
    print("Enter the following parameters (leave empty for defaults where available):")

    while True:
        try:
            # Get user inputs
            v0 = get_float_input("\nInitial velocity (m/s): ")
            launch_angle = get_float_input("Launch angle (degrees): ")
            spin = get_float_input("Spin rate (RPM): ")
            height = get_float_input("Initial height (m) [default=0.0]: ") or 0.0

            # Run simulation
            t, x, y, z = simulate_golf_shot(v0, launch_angle, spin, height)

            # Display results
            print(f"\nResults:")
            print(f"Carry distance: {x[-1]:.2f} meters")
            print(f"Total flight time: {t[-1]:.2f} seconds")

            # Plot option
            plot = input("\nShow trajectory plot? (y/n): ").lower()
            if plot == 'y':
                plt.figure(figsize=(10, 5))
                plt.plot(x, z)
                plt.xlabel('Horizontal Distance (m)')
                plt.ylabel('Height (m)')
                plt.title('Golf Ball Trajectory')
                plt.grid(True)
                plt.show()

            # Continue option
            cont = input("\nRun another simulation? (y/n): ").lower()
            if cont != 'y':
                print("Goodbye!")
                break

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again with valid inputs.\n")


if __name__ == "__main__":
    main()
