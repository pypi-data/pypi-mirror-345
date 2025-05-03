"""This module plots the boundary condition in matplotlib."""

import numpy as np
import matplotlib.pyplot as plt


# define atime span from 0 to t_max
pulse = 0.008  # non-zero pulse duration
t_max = 0.007999  # seconds
n_steps = 1000  # number of dt intervals
ts = np.linspace(0.000001, t_max, n_steps)

# define the angular acceleration function
alpha_max = 8000  # rad/s^2, peak angular acceleration


# calculate the alpha value
def alpha(t):
    """Generates the angular acceleration pulse."""
    if 0.0 <= t <= pulse:
        return alpha_max * np.exp(1 - 1 / (1 - (2 * t / pulse - 1) ** 2))
    return 0.0


ys = np.vectorize(alpha)(ts)

# compute the integral of alpha(t) using cumulative trapezoidal integration
ys_int = np.zeros_like(ys)
for i in range(1, len(ts)):
    ys_int[i] = np.trapz(ys[: i + 1], ts[: i + 1])  # cumulative

# create the plot
width = 4  # inches
height = 8  # inches
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(width, height), sharex=True)

# ax1.plot(ts, ys, label="angular acceleration", color="blue")
ax1.plot(ts, ys, color="blue")
ax1.set_title("Angular Acceleration versus Time")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Angular Acceleration (rad/s^2)")
ax1.grid()
# ax1.legend()

# ax2.plot(ts, ys_int, label="angular velocity", color="blue")
ax2.plot(ts, ys_int, color="blue")
ax2.set_title("Angular Velocity versus Time")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Angular Velocity (rad/s)")
ax2.grid()
# ax2.legend()

# adjust layout to prevent overlap
plt.tight_layout()

breakpoint()

plt.show()
