import cv2
import numpy as np
import os

# Paths
image_folder = "/Users/patrickjohnson/python-projects/timelapse/images"  # Replace with your folder path
output_folder = "/Users/patrickjohnson/python-projects/timelapse/images/bubble_count"  # Replace with your desired output folder
csv_output_path = "/Users/patrickjohnson/python-projects/timelapse/bubble_count.csv"

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

# Prepare CSV file
with open(csv_output_path, "w") as csv_file:
    csv_file.write("Image,BubbleCount\n")

# Process each image
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
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    # Threshold the image to detect bubbles
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and count bubbles based on contour area
    bubble_contours = [cnt for cnt in contours if 50 < cv2.contourArea(cnt) < 1500]
    bubble_count = len(bubble_contours)

    # Draw contours on the cropped ROI
    output_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(output_image, bubble_contours, -1, (0, 255, 0), 2)

    # Save the processed image with bubbles outlined
    output_path = os.path.join(output_folder, f"processed_{image_file}")
    cv2.imwrite(output_path, output_image)

    # Write to CSV
    with open(csv_output_path, "a") as csv_file:
        csv_file.write(f"{image_file},{bubble_count}\n")

    print(f"{image_file}: {bubble_count} bubbles detected")

# Finish processing
print(f"Processing complete. Processed images saved to {output_folder}.")