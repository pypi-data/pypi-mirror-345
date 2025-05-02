import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def animate(file_name):
    data = np.load(file_name)
    t_full, C_full = data["t_full"], data["C_full"]
    Domain_Length, Source_Intensity = data["Domain_Length"].item(), data["Source_Intensity"].item()
    Grid_Space = data["Grid_Space"]

    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2)
    ax.set_xlim(0, Domain_Length)
    ax.set_ylim(0, Source_Intensity * 1.1)
    ax.set_xlabel('x [m]')
    ax.set_ylabel('Concentration [g/l]')

    def init():
        line.set_data([], [])
        return line,

    def update(frame):
        line.set_data(Grid_Space, C_full[:, frame])
        ax.set_title(f't = {t_full[frame]:.0f} s')
        return line,

    ani = FuncAnimation(fig, update, frames=range(0, len(t_full), 10), init_func=init, blit=True)
    plt.show()
