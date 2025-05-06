# filename: codebase/plot_y_equals_x_squared.py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Ensure the output directory exists
import os
database_path = "data/"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Generate data for the plot
x = np.linspace(-10, 10, 500)  # x values from -10 to 10
y = x**2  # y = x^2

# Create the plot
plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'

fig, ax = plt.subplots()
ax.plot(x, y, label=r"$y = x^2$", color="blue", linewidth=2)

# Add labels, title, and grid
ax.set_xlabel(r"$x$", fontsize=12)
ax.set_ylabel(r"$y$", fontsize=12)
ax.set_title(r"Plot of $y = x^2$", fontsize=14)
ax.grid(True)
ax.legend(fontsize=10)

# Adjust axis limits and scaling
ax.relim()
ax.autoscale_view()

# Save the plot
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_filename = database_path + "plot_y_equals_x_squared_" + timestamp + ".png"
plt.savefig(plot_filename, dpi=300)

# Print confirmation
print("Plot of y = x^2 saved successfully as:", plot_filename)