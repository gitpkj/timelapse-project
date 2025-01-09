import cv2
import numpy as np
import os

# Paths
image_folder = "/Users/patrickjohnson/python-projects/timelapse/images"  # Replace with your folder path
output_folder = "/Users/patrickjohnson/python-projects/timelapse/images/bubble_count"  # Replace with your desired output folder

# Get the list of images in the folder
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(".jpg")])

# Load the first image to select the ROI
first_image_path = os.path.join(image_folder, image_files[0])
first_image = cv2.imread(first_image_path)

# Check if the image was loaded
if first_image is None:
    print("Error: Could not load the first image.")
    exit()

# Select ROI interactively
print("Select the region of interest (ROI) and press Enter or Space when done.")
roi = cv2.selectROI("Select ROI", first_image, fromCenter=False, showCrosshair=True)
cv2.destroyAllWindows()

# Get ROI coordinates
x, y, w, h = roi
print(f"Selected ROI coordinates: x={x}, y={y}, w={w}, h={h}")

# Process each image in the folder
for image_file in image_files:
    # Load the current image
    image_path = os.path.join(image_folder, image_file)
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load {image_file}")
        continue

    # Crop the ROI from the current image
    cropped_image = image[y:y + h, x:x + w]

    # Convert to grayscale
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)  # Adjusted kernel size

    # Threshold the image to detect bubbles
    _, thresh = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY_INV)

    # Morphological operations to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and count bubbles based on circularity and area
    bubble_contours = []
    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        area = cv2.contourArea(cnt)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter * perimeter))
        if 10 < area < 500 and 0.5 <= circularity <= 1.0:  # Adjust parameters
            bubble_contours.append(cnt)

    bubble_count = len(bubble_contours)

    # Draw contours on the cropped ROI
    output_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(output_image, bubble_contours, -1, (0, 255, 0), 2)

    # Save the processed image with bubbles outlined
    output_path = os.path.join(output_folder, f"processed_{image_file}")
    cv2.imwrite(output_path, output_image)

    # Print the bubble count for the current image
    print(f"{image_file}: {bubble_count} bubbles detected")

# Finish processing
print(f"Processing complete. Processed images saved to {output_folder}.")
