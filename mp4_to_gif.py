from moviepy.editor import VideoFileClip

# Load the MP4 video
video = VideoFileClip("sourdough_timelapse.mp4")

# Convert to GIF and save
video.write_gif("sourdough_timelapse.gif", fps=15)  # Adjust fps for smoother or faster GIF