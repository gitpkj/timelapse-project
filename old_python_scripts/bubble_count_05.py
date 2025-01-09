import cv2
import numpy as np

# Load the processed image (ensure it's the correct path)
image_path = "/Users/patrickjohnson/python-projects/timelapse/images/bubble_count/processed_image_0004.jpg"  # Replace with the path to your image
image = cv2.imread(image_path)

# Convert to grayscale
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding (adjust values if needed)
_, binary_image = cv2.threshold(gray_image, 80, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter contours based on area and circularity
bubble_count = 0
for contour in contours:
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    if perimeter > 0:
        circularity = 4 * np.pi * (area / (perimeter ** 2))
    else:
        circularity = 0  # Avoid division by zero

    # Adjust thresholds for area and circularity
    if 10 < area < 1500 and 0.5 <= circularity <= 1.0:  
        bubble_count += 1  # Increment the bubble counter

        # Optional: Highlight the contour in green
        cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)

# Display the result
print(f"Number of bubbles detected: {bubble_count}")

# Save or display the image with highlighted bubbles
cv2.imshow("Bubbles Detected", image)
cv2.waitKey(0)  # Press any key to close the window
cv2.destroyAllWindows()
