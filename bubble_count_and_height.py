import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# File Paths
data_log_path = "/Users/patrickjohnson/python-projects/timelapse/data_log.csv"
image_folder = "/Users/patrickjohnson/python-projects/timelapse/images"
output_video = "/Users/patrickjohnson/python-projects/timelapse/timelapse_with_graphs.mp4"
output_folder = "/Users/patrickjohnson/python-projects/timelapse/annotated_images"
bubble_height_csv = "/Users/patrickjohnson/python-projects/timelapse/bubble_height_data.csv"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load Data

def load_and_prepare_data(data_log_path, bubble_height_csv, image_folder):
    # Load temperature and humidity data
    df = pd.read_csv(data_log_path)
    df.rename(columns={
        'Timestamp': 'time',
        'Temperature (°F)': 'temperature',
        'Humidity (%)': 'humidity'
    }, inplace=True)
    df['time'] = pd.to_datetime(df['time'])
    df.sort_values('time', inplace=True)

    # Ensure Images Are Sorted Correctly
    image_files = sorted([f for f in os.listdir(image_folder) if f.startswith("image_") and f.endswith(".jpg")])
    df = df.iloc[:len(image_files)]
    df['image_paths'] = [os.path.join(image_folder, img) for img in image_files]

    # Load bubble count and height data
    if os.path.exists(bubble_height_csv):
        bubble_df = pd.read_csv(bubble_height_csv)
        bubble_df.rename(columns={'Image': 'image_file', 'Starter Height (Pixels)': 'starter_height', 'Bubble Count': 'bubble_count'}, inplace=True)
        df = df.merge(bubble_df, left_on='image_paths', right_on='image_file', how='left')
    else:
        df['starter_height'] = 0
        df['bubble_count'] = 0

    return df

# Visualization and Timelapse Generation

def update_graph_data(row, x_data, temp_data, hum_data, bubble_data, height_data):
    x_data.append(len(x_data))
    temp_data.append(row['temperature'])
    hum_data.append(row['humidity'])
    bubble_data.append(row['bubble_count'])
    height_data.append(row['starter_height'])

def render_graph(ax, x_data, y_data, label, color, ylabel, title):
    ax.clear()
    ax.plot(x_data, y_data, marker='o', color=color, label=label)
    ax.set_xlim(0, len(x_data))
    ax.set_xlabel("Frame Number", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend()

def create_timelapse(df, output_video, width, height):
    fps = 10
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(6, 15))
    canvas = FigureCanvas(fig)
    x_data, temp_data, hum_data, bubble_data, height_data = [], [], [], [], []

    for idx, row in df.iterrows():
        frame = cv2.imread(row['image_paths'])

        update_graph_data(row, x_data, temp_data, hum_data, bubble_data, height_data)

        render_graph(ax1, x_data, temp_data, "Temperature (°F)", "blue", "Temperature (°F)", "Temperature Over Time")
        ax1.plot(x_data, hum_data, marker='s', color='green', label="Humidity (%)")
        ax1.legend()

        render_graph(ax2, x_data, bubble_data, "Bubble Count", "red", "Bubble Count", "Bubbles Over Time")
        render_graph(ax3, x_data, height_data, "Starter Height", "purple", "Starter Height (pixels)", "Starter Height Over Time")

        canvas.draw()
        graph_image = np.frombuffer(canvas.tostring_argb(), dtype='uint8')
        graph_image = graph_image.reshape(canvas.get_width_height()[::-1] + (4,))
        graph_image = np.roll(graph_image, -1, axis=2)
        graph_image = cv2.cvtColor(graph_image[..., :3], cv2.COLOR_RGB2BGR)

        graph_height, graph_width, _ = graph_image.shape
        frame[-graph_height:, -graph_width:] = graph_image

        video.write(frame)

        if idx % 10 == 0:
            print(f"Processed frame {idx + 1}/{len(df)}")

    video.release()
    print(f"Timelapse with graphs saved as {output_video}")

# Main Execution
if __name__ == "__main__":
    df = load_and_prepare_data(data_log_path, bubble_height_csv, image_folder)

    first_frame = cv2.imread(df['image_paths'].iloc[0])
    height, width, _ = first_frame.shape

    create_timelapse(df, output_video, width, height)