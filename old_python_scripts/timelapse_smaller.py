import cv2
import os

# Define the directory containing images and the output video file
image_folder = '/home/pi/timelapse/'  # Replace with your folder path
output_video = '/home/pi/timelapse/timelapse.mp4'

# Get a list of all image files in the directory, sorted by filename
images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
images.sort()

# Read the first image to get frame size
first_image_path = os.path.join(image_folder, images[0])
frame = cv2.imread(first_image_path)
height, width, layers = frame.shape

# Define the codec and create VideoWriter object
fps = 30  # Frames per second
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
video = cv2.VideoWriter(output_video, fourcc, fps, (1920, 1080))  # Adjusted size for resized frames

# Loop through all images and add them to the video
total_images = len(images)
for idx, image in enumerate(images):  # Add progress tracking
    image_path = os.path.join(image_folder, image)
    frame = cv2.imread(image_path)  # Read the image

    # Resize the image to 1920x1080
    frame = cv2.resize(frame, (1920, 1080))

    video.write(frame)  # Add the resized image to the video

    # Print progress
    print(f"Processing image {idx + 1} of {total_images}")

# Release the video writer object
video.release()
print(f"Timelapse video saved as {output_video}")
