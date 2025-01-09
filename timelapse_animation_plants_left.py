import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# File Paths
data_log_path = "/Users/patrickjohnson/python-projects/timelapse/data_log.csv"
image_folder = "/Users/patrickjohnson/python-projects/timelapse/images"
output_video = "/Users/patrickjohnson/python-projects/timelapse/timelapse_with_graph.mp4"

# Load CSV Data
df = pd.read_csv(data_log_path)
df.rename(columns={
    'Timestamp': 'time',
    'Temperature (°F)': 'temperature',
    'Humidity (%)': 'humidity'
}, inplace=True)

# Sort Data and Ensure Correct Formatting
df['time'] = pd.to_datetime(df['time'])
df.sort_values('time', inplace=True)

# Ensure Images Are Sorted Correctly
image_files = sorted([f for f in os.listdir(image_folder) if f.startswith("image_") and f.endswith(".jpg")])
df = df.iloc[:len(image_files)]  # Limit data to the number of images
df['image_paths'] = [f"{image_folder}/{img}" for img in image_files]

# Initialize Video Writer
frame = cv2.imread(df['image_paths'].iloc[0])
height, width, layers = frame.shape
fps = 10  # Adjust fps for desired playback speed
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# Font for Overlay
font_path = "/Library/Fonts/Arial.ttf"  # Adjust for your system
font = ImageFont.truetype(font_path, 36)

# Initialize Graph Figure
fig, ax = plt.subplots(figsize=(5, 8))  # Adjust graph size
canvas = FigureCanvas(fig)
x_data, temp_data, hum_data = [], [], []

# Process Each Frame
for idx, row in df.iterrows():
    # Read the timelapse frame
    frame = cv2.imread(row['image_paths'])
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Update Graph Data
    x_data.append(idx)
    temp_data.append(row['temperature'])
    hum_data.append(row['humidity'])

    # Clear and Update Graph
    ax.clear()
    ax.plot(x_data, temp_data, marker='o', color='blue', label="Temperature (°F)")
    ax.plot(x_data, hum_data, marker='s', color='green', label="Humidity (%)")
    ax.set_xlim(0, len(df))  # Adjust the range dynamically
    ax.set_ylim(0, max(max(temp_data), max(hum_data)) + 10)  # Adjust dynamically
    ax.set_xlabel("Frame Number", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.legend()
    ax.set_title("Temperature & Humidity Over Time", fontsize=14)

    # Render the Graph to Image
    canvas.draw()
    graph_image = np.frombuffer(canvas.tostring_argb(), dtype='uint8')  # Use `tostring_argb`
    graph_image = graph_image.reshape(canvas.get_width_height()[::-1] + (4,))
    graph_image = np.roll(graph_image, -1, axis=2)  # Reorder ARGB to RGBA
    graph_image = Image.fromarray(graph_image[..., :3])  # Drop the alpha channel

    # Overlay the Graph
    graph_width, graph_height = graph_image.size
    graph_x = 10  # Move the graph to the left side
    graph_y = 0  # Adjust vertical position of the graph
    pil_image.paste(graph_image, (graph_x, graph_y))

    # Convert Back to OpenCV
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    video.write(frame)

    if idx % 10 == 0:  # Print progress every 10 frames
        print(f"Processed frame {idx + 1}/{len(df)}")

# Release Video Writer
video.release()
print(f"Timelapse with graph saved as {output_video}")
