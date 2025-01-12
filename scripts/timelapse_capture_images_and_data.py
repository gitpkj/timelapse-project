import os
import serial
import time
import subprocess
import csv

# Define paths for the photo counter and logs
counter_file = "../photo_counter.txt"  # Adjusted for the new directory structure
csv_file = "../data_log.csv"          # Adjusted for the new directory structure
error_log_file = "../error_log.txt"  # Adjusted for the new directory structure

# Load the photo counter from the file
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        photo_counter = int(f.read().strip())
else:
    photo_counter = 1  # Start from 1 if the file doesn't exist

# Configure Serial connection with Arduino
try:
    print("Initializing serial connection...")
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=2)  # Use the correct port
    arduino.flush()
    print("Serial connection established.")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    with open(error_log_file, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Serial connection error: {e}\n")
    exit()

def capture_photo():
    global photo_counter
    try:
        print("Capturing photo...")
        # Generate a sequential filename
        filename = f"/home/pi/timelapse/image_{photo_counter:04d}.jpg"
        subprocess.run(["libcamera-still", "-o", filename], check=True)
        print(f"Photo captured: {filename}")
        photo_counter += 1  # Increment the counter
        
        # Save the updated counter to the file
        with open(counter_file, "w") as f:
            f.write(str(photo_counter))
    except subprocess.CalledProcessError as e:
        print(f"Error capturing photo: {e}")
        with open(error_log_file, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Photo capture error: {e}\n")

# Ensure the CSV file is ready
try:
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write header if the file is empty
        if file.tell() == 0:
            writer.writerow(["Timestamp", "Temperature (°F)", "Humidity (%)"])
except Exception as e:
    print(f"Error creating CSV file: {e}")
    with open(error_log_file, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - CSV file error: {e}\n")
    exit()

# Main loop
print("Waiting for data from Arduino...")
while True:
    try:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            print(f"Raw data received: {line}")
            if line:
                try:
                    # Parse the temperature in Fahrenheit and humidity
                    temp_f, humidity = line.split(",")
                    temp_f = float(temp_f)
                    humidity = float(humidity)

                    print(f"Temperature: {temp_f}°F, Humidity: {humidity}%")
                    
                    # Capture a photo
                    capture_photo()
                    
                    # Get the current timestamp
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Append data to CSV file
                    with open(csv_file, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([timestamp, temp_f, humidity])
                        print(f"Logged data: {timestamp}, {temp_f}°F, {humidity}%")
                except ValueError:
                    print(f"Invalid data format: {line}")
                    with open(error_log_file, "a") as log_file:
                        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Invalid data: {line}\n")
        else:
            print("No data received. Waiting for the next Arduino transmission...")
        # Synchronize with Arduino's 5-minute interval (300 seconds)
        time.sleep(5)  # Optional slight buffer for data consistency
    except Exception as e:
        print(f"Error in main loop: {e}")
        with open(error_log_file, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Main loop error: {e}\n")
        break

