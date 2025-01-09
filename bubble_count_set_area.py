import os
import cv2
import numpy as np
import pandas as pd

# Paths
image_folder = "images"  # Replace with your folder path
output_folder = "images/bubble_count_volume_tracking"  # Folder for processed images
csv_output_path = "bubble_count_volume_tracking.csv"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load image files
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(".jpg")])

# Jar dimensions for volume estimation
jar_height_pixels = 500  # Example height of jar in pixels (calibrated value)
jar_volume_ml = 1000  # Known volume of jar in milliliters

# Prepare CSV file
with open(csv_output_path, "w") as csv_file:
    csv_file.write("Image,BubbleCount,Volume (ml)\n")

# Process each image
for image_file in image_files:
    # Load the current image
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not load {image_file}")
        continue

    # Convert to grayscale and crop ROI
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    gray = cv2.equalizeHist(gray)

    # Apply median blur to reduce noise
    blurred = cv2.medianBlur(gray, 5)

    # Threshold the image to detect bubbles
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours for bubble detection
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and count bubbles based on contour area and circularity
    bubble_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 20 < area < 2000:  # Adjusted area range for bubbles
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if 0.5 < circularity <= 1.2:  # Loosened circularity range for bubbles
                bubble_contours.append(cnt)

    bubble_count = len(bubble_contours)

    # Apply edge detection to find the top of the starter for volume tracking
    edges = cv2.Canny(gray, 50, 150)

    # Detect the top boundary of the starter
    starter_boundary = None
    for y in range(edges.shape[0]):
        if np.any(edges[y, :]):
            starter_boundary = y
            break

    if starter_boundary is None:
        print(f"Error: Could not detect starter boundary in {image_file}")
        continue

    # Calculate the starter height
    starter_height_pixels = edges.shape[0] - starter_boundary

    # Estimate volume based on height
    starter_volume_ml = (starter_height_pixels / jar_height_pixels) * jar_volume_ml

    # Draw the detected boundary and bubble contours on the image
    output_image = image.copy()
    cv2.line(output_image, (0, starter_boundary), (output_image.shape[1], starter_boundary), (0, 255, 0), 2)
    cv2.drawContours(output_image, bubble_contours, -1, (255, 0, 0), 2)

    # Save the processed image
    output_path = os.path.join(output_folder, f"processed_{image_file}")
    cv2.imwrite(output_path, output_image)

    # Write to CSV
    with open(csv_output_path, "a") as csv_file:
        csv_file.write(f"{image_file},{bubble_count},{starter_volume_ml:.2f}\n")

    print(f"{image_file}: Bubble Count = {bubble_count}, Volume = {starter_volume_ml:.2f} ml")

print("Processing complete. Bubble count and volume data saved to CSV and images saved to output folder.")