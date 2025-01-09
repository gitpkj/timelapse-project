import cv2

# Callback function to display coordinates
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button click
        print(f"Coordinates: ({x}, {y})")
        # Display the coordinates on the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f"({x}, {y})", (x, y), font, 0.5, (255, 0, 0), 1)
        cv2.imshow('image', img)

# Read the image
img = cv2.imread('/Users/patrickjohnson/python-projects/timelapse/images/image_0001.jpg')

# Display the image
cv2.imshow('image', img)

# Set mouse callback function to capture click events
cv2.setMouseCallback('image', click_event)

# Wait for a key press and close the window
cv2.waitKey(0)
cv2.destroyAllWindows()
