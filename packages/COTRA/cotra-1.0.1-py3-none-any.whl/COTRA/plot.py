import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def CvS(files, *comments):
    # If not a list, make it a list
    if not isinstance(files, list):
        files = [files]
    
    # If not a list, make it a list
    if not isinstance(comments, list):
        comments = [comments]

    # List to hold the loaded data
    data_list = []

    # Load each file and extract variables
    for f in files:
        data = np.load(f)
        t_full = data["t_full"]
        C_full = data["C_full"]
        Domain_Length = data["Domain_Length"].item()  # Convert scalar array to a Python scalar
        Source_Intensity = data["Source_Intensity"].item()
        Grid_Space = data["Grid_Space"]
        data_list.append((t_full, C_full, Domain_Length, Source_Intensity, Grid_Space))

    # Assume all files share the same time grid; use the first file's t_full.
    t_full = data_list[0][0]
    num_time_steps = len(t_full)

    # Initial time step to plot
    initial_time_step = 10

    # Create the figure and the main axes for plotting
    fig, ax = plt.subplots(figsize=(8, 5))
    plt.subplots_adjust(bottom=0.25)  # Make space at the bottom for the slider

    # Plot initial concentration profiles for each output
    lines = []
    for idx, (t_full, C_full, Domain_Length, Source_Intensity, Grid_Space) in enumerate(data_list):
        concentration_profile = C_full[:, initial_time_step]
        line, = ax.plot(Grid_Space, concentration_profile, label=f'{comments[idx]}')
        lines.append(line)

    ax.set_xlabel('x [m]')
    ax.set_ylabel('Concentration [g/l]')
    ax.set_title(f'Concentration Profiles at Time {t_full[initial_time_step]:.0f} s')
    ax.legend()

    # Create a slider axis below the main plot
    slider_ax = plt.axes([0.15, 0.1, 0.7, 0.05])
    time_slider = Slider(slider_ax, 'Time Index', 0, num_time_steps - 1, valinit=initial_time_step, valstep=1)

    # Update function to change the plot based on the slider's value
    def update(val):
        time_step = int(time_slider.val)
        for idx, (t_full, C_full, Domain_Length, Source_Intensity, Grid_Space) in enumerate(data_list):
            # Update the y-data for each plot line
            lines[idx].set_ydata(C_full[:, time_step])
        ax.set_title(f'Concentration Profiles at Time {t_full[time_step]:.0f} s')
        fig.canvas.draw_idle()

    # Register the update function with the slider
    time_slider.on_changed(update)

    plt.show()

def CvT(files, *comments):
    # If not a list, make it a list
    if not isinstance(files, list):
        files = [files]
    
    # If not a list, make it a list
    if not isinstance(comments, list):
        comments = [comments]
    # List to hold the loaded data
    data_list = []

    # Load each file and extract variables
    for f in files:
        data = np.load(f)
        t_full = data["t_full"]
        C_full = data["C_full"]
        Domain_Length = data["Domain_Length"].item()  # Convert scalar array to a Python scalar
        Source_Intensity = data["Source_Intensity"].item()
        Grid_Space = data["Grid_Space"]
        data_list.append((t_full, C_full, Domain_Length, Source_Intensity, Grid_Space))

    # Get array of concentration in time at a given point in space
    point = 0.29  # Example point in space (in meters)

    # Assume all files share the same time and space grids
    t_full = data_list[0][0]
    Grid_Space = data_list[0][4]
    num_time_steps = len(t_full)
    min_x = Grid_Space.min()
    max_x = Grid_Space.max()

    # Create the figure and the main axes for plotting
    fig, ax = plt.subplots(figsize=(8, 5))
    plt.subplots_adjust(bottom=0.25)  # Make space at the bottom for the slider

    # Plot concentration in time at the selected spatial point for each dataset
    lines = []
    for idx, (t_full, C_full, Domain_Length, Source_Intensity, Grid_Space) in enumerate(data_list):
        point_index = np.argmin(np.abs(Grid_Space - point))
        concentration_evolution = C_full[point_index, :]  # Concentration over time at this point
        line, = ax.plot(t_full, concentration_evolution, label=f'{comments[idx]}')
        lines.append(line)

    ax.set_ylim(0, 1.1 * np.max(C_full))  # Set y-limits based on the maximum concentration
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Concentration [g/l]')
    ax.set_title(f'Concentration vs Time at x = {point:.2f} m')
    ax.legend()

    # Create a slider axis below the main plot
    slider_ax = plt.axes([0.15, 0.1, 0.7, 0.05])
    x_slider = Slider(slider_ax, 'x [m]', min_x, max_x, valinit=point)

    # Update function to change the plot based on the slider's value
    def update(val):
        point = x_slider.val
        point_index = np.argmin(np.abs(Grid_Space - point))
        for idx, (_, C_full, _, _, _) in enumerate(data_list):
            concentration_evolution = C_full[point_index, :]
            lines[idx].set_ydata(concentration_evolution)
        ax.set_title(f'Concentration vs Time at x = {point:.2f} m')
        fig.canvas.draw_idle()

    # Register the update function with the slider
    x_slider.on_changed(update)

    plt.show()
