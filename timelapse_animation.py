import matplotlib
matplotlib.use('Agg')  # Use Agg backend for rendering off-screen
import numpy as np
import imageio.v2 as iio
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

# Load data
print("Loading data from combined_starter_data.csv")
data = pd.read_csv("combined_starter_data.csv")
print("Data loaded successfully:")
print(data.head())

# Settings
output_filename = "sourdough_timelapse.mp4"
canvas_width, canvas_height = 1600, 912  # Adjusted height to be divisible by 16
x_range = list(range(len(data)))  # Static x-axis range

# Precompute axis limits
starter_height_max = data["Starter Height (Pixels)"].max()
bubble_count_max = data["Bubble Count"].max()
temperature_max = data["Temperature (°F)"].max()
temperature_min = data["Temperature (°F)"].min()
humidity_max = data["Humidity (%)"].max()
humidity_min = data["Humidity (%)"].min()

# Setup figure layout
print("Setting up the figure layout...")
fig = plt.figure(figsize=(16, 9))  # Create a figure with a 16:9 aspect ratio
gs = fig.add_gridspec(8, 6)  # Define an 8x6 grid (more rows for finer vertical control)

# Adjusting subplot allocation
ax_img = fig.add_subplot(gs[:, :4])  # Jar image spans all rows and the first 4 columns
ax_height = fig.add_subplot(gs[1:3, 4:6])  # Starter height graph spans 2 rows (taller) and the last 2 columns
ax_bubble = fig.add_subplot(gs[3:5, 4:6])  # Bubble count graph spans 2 rows (taller) and the last 2 columns
ax_temp_hum = fig.add_subplot(gs[5:7, 4:6])  # Temperature and humidity graph spans 2 rows (taller) and the last 2 columns

# Set static axis limits
ax_height.set_xlim(0, len(data) - 1)
ax_height.set_ylim(0, starter_height_max + 10)
ax_bubble.set_xlim(0, len(data) - 1)
ax_bubble.set_ylim(0, bubble_count_max + 5)
ax_temp_hum.set_xlim(0, len(data) - 1)
ax_temp_hum.set_ylim(
    min(temperature_min, humidity_min) - 5, max(temperature_max, humidity_max) + 5
)

# Generate frames
print("Generating timelapse frames...")
frames = []
for idx, row in tqdm(data.iterrows(), total=len(data), desc="Processing frames"):
    ax_img.clear()
    ax_height.clear()
    ax_bubble.clear()
    ax_temp_hum.clear()

    # Display the image
    img_path = row["Image"]
    try:
        img = iio.imread(f"images/{img_path}")
        ax_img.imshow(img)
        ax_img.axis("off")
    except FileNotFoundError:
        ax_img.text(0.5, 0.5, f"Image {img_path} not found", fontsize=12, ha="center", va="center")
        ax_img.axis("off")

    # Plot data incrementally
    ax_height.plot(x_range[:idx + 1], data["Starter Height (Pixels)"][:idx + 1], label="Starter Height (Pixels)")
    ax_height.set_xlim(0, len(data) - 1)  # Re-enforce static limits
    ax_height.set_ylim(200, starter_height_max + 10)
    ax_height.set_title("Starter Height Over Time")
    ax_height.legend(fontsize=10, loc='upper left')  # Fix legend to the top-left corner

    ax_bubble.plot(x_range[:idx + 1], data["Bubble Count"][:idx + 1], label="Bubble Count", color="orange")
    ax_bubble.set_xlim(0, len(data) - 1)  # Re-enforce static limits
    ax_bubble.set_ylim(0, bubble_count_max + 5)
    ax_bubble.set_title("Bubble Count Over Time")
    ax_bubble.legend(fontsize=10, loc='upper left')  # Fix legend to the top-left corner

    ax_temp_hum.plot(x_range[:idx + 1], data["Temperature (°F)"][:idx + 1], label="Temperature (°F)", color="red")
    ax_temp_hum.plot(x_range[:idx + 1], data["Humidity (%)"][:idx + 1], label="Humidity (%)", color="blue")
    ax_temp_hum.set_xlim(0, len(data) - 1)  # Re-enforce static limits
    ax_temp_hum.set_ylim(
        min(temperature_min, humidity_min) - 5, max(temperature_max, humidity_max) + 5
    )
    ax_temp_hum.set_title("Temperature & Humidity Over Time")
    ax_temp_hum.legend(fontsize=10, loc='lower left')  # Fix legend to the top-left corner

    fig.tight_layout()
    fig.canvas.draw()

    # Convert figure to NumPy array (using ARGB format)
    buffer = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    buffer = buffer.reshape(fig.canvas.get_width_height()[::-1] + (4,))
    buffer = buffer[:, :, [1, 2, 3]]  # Convert ARGB to RGB
    frames.append(buffer)

# Save video
print("Writing video...")
with iio.get_writer(output_filename, fps=24, codec="libx264") as writer:
    for frame in tqdm(frames, desc="Saving frames"):
        writer.append_data(frame)

print(f"Timelapse video saved as {output_filename}")