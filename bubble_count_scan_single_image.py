import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image
image_path = "/Users/patrickjohnson/python-projects/timelapse/images/bubble_count/processed_image_0058.jpg"  # Replace with the path to your image
image = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply a Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (11, 11), 0)

# Apply adaptive thresholding to highlight the bubbles
thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter out small contours based on area
bubble_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]

# Draw the contours on the original image
output_image = image.copy()
cv2.drawContours(output_image, bubble_contours, -1, (0, 255, 0), 2)

# Count the bubbles
bubble_count = len(bubble_contours)

# Display the results
print(f"Number of air bubbles detected: {bubble_count}")

# Show the original and processed images
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

plt.subplot(1, 2, 2)
plt.title(f"Detected Bubbles: {bubble_count}")
plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

plt.show()
