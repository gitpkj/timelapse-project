import imageio.v2 as iio
writer = iio.get_writer("test.mp4", fps=24, codec="libx264")
writer.close()
print("FFmpeg plugin is working correctly!")