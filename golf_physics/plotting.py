import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

def plot_trajectory(flight_positions, bounce_positions=None):
    """
    Plots the 3D trajectory of the ball.
    """
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the flight trajectory.
    ax.plot(flight_positions[:, 0], flight_positions[:, 2], flight_positions[:, 1],
            label='Flight', color='blue', linewidth=2)

    # Plot the bounce & roll trajectory if provided.
    if bounce_positions is not None:
        ax.plot(bounce_positions[:, 0], bounce_positions[:, 2], bounce_positions[:, 1],
                label='Bounce & Roll', color='red', linewidth=2)

    ax.set_xlabel('X (m)')
    ax.set_ylabel('Z (m)')
    ax.set_zlabel('Y (m)')
    ax.set_title('Golf Ball Trajectory')
    ax.legend()
    # Optional: adjust the view (e.g., a "behind the ball" perspective).
    ax.view_init(elev=15, azim=-60)
    plt.show()
