import cv2
import numpy as np
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Paths
image_folder = "../images"  # Adjusted to move up from scripts/ to the images/ folder
output_folder = "../processed_images"
data_log_path = "../data_log.csv"
csv_output_path = "../combined_starter_data.csv"
os.makedirs(output_folder, exist_ok=True)

# Step 1: Manual Selection of Points
def select_points(image_path):
    image = cv2.imread(image_path)
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Select Points", image)

    print("Click to select points along the top of the starter. Press 'q' when done.")
    cv2.imshow("Select Points", image)
    cv2.setMouseCallback("Select Points", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return np.array(points, dtype=np.float32)

# Step 2: Select the Jar Area
def select_jar_area(image_path):
    image = cv2.imread(image_path)
    print("Select the jar area by dragging a rectangle around it.")
    roi = cv2.selectROI("Select the Jar Area", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()
    return roi

# Step 3: Track Points and Analyze Each Frame
def process_images(folder_path, initial_points, jar_roi, data_log, csv_output_path, output_folder):
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpg')])
    prev_frame = cv2.imread(os.path.join(folder_path, image_files[0]), cv2.IMREAD_GRAYSCALE)
    points = initial_points.reshape(-1, 1, 2)

    jar_x, jar_y, jar_w, jar_h = jar_roi

    with open(csv_output_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Image", "Starter Height (Pixels)", "Bubble Count", "Temperature (°F)", "Humidity (%)"])

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(folder_path, image_file)
            current_frame = cv2.imread(image_path)
            gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Track points using Lucas-Kanade Optical Flow
            new_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_frame, gray_frame, points, None)

            # Filter valid points
            status = status.flatten()
            valid_points = new_points[status == 1].reshape(-1, 2)

            if len(valid_points) > 0:
                avg_y = np.mean(valid_points[:, 1])
                height = current_frame.shape[0] - avg_y

                # Crop the jar area for bubble counting
                jar_cropped_region = gray_frame[jar_y:jar_y + jar_h, jar_x:jar_x + jar_w]
                crop_bottom = int(avg_y - jar_y)
                jar_cropped_region = jar_cropped_region[crop_bottom:, :]

                # Bubble counting
                blurred = cv2.GaussianBlur(jar_cropped_region, (11, 11), 0)
                thresh = cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
                )

                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                bubble_contours = [cnt for cnt in contours if 50 < cv2.contourArea(cnt) < 1500]
                bubble_count = len(bubble_contours)

                # Get temperature and humidity data for this frame
                temperature = data_log.iloc[i]["Temperature (°F)"] if i < len(data_log) else "N/A"
                humidity = data_log.iloc[i]["Humidity (%)"] if i < len(data_log) else "N/A"

                # Annotate the image
                annotated_image = current_frame.copy()
                jar_annotated = annotated_image[jar_y:jar_y + jar_h, jar_x:jar_x + jar_w]
                cv2.drawContours(jar_annotated[crop_bottom:, :], bubble_contours, -1, (0, 255, 0), 2)
                for point in valid_points:
                    cv2.circle(annotated_image, tuple(point.astype(int)), 5, (0, 0, 255), -1)

                output_path = os.path.join(output_folder, f"processed_{image_file}")
                cv2.imwrite(output_path, annotated_image)

                writer.writerow([image_file, height, bubble_count, temperature, humidity])

                print(f"{image_file}: Height = {height:.2f}, Bubble Count = {bubble_count}, Temperature = {temperature}, Humidity = {humidity}")

            prev_frame = gray_frame
            points = valid_points.reshape(-1, 1, 2) if len(valid_points) > 0 else points

# Main Execution
if __name__ == "__main__":
    sample_image_path = os.path.join(image_folder, "image_0001.jpg")
    data_log = pd.read_csv(data_log_path)
    initial_points = select_points(sample_image_path)
    jar_roi = select_jar_area(sample_image_path)
    process_images(image_folder, initial_points, jar_roi, data_log, csv_output_path, output_folder)

    print(f"Processing complete. Data saved to {csv_output_path}. Processed images saved to {output_folder}.")