import pandas as pd

# Load bubble and height data
bubble_height_file = 'bubble_height_data.csv'
try:
    bubble_height_data = pd.read_csv(bubble_height_file)
    print(f"Loaded {bubble_height_file}:\n", bubble_height_data.head())
except FileNotFoundError:
    print(f"Error: {bubble_height_file} not found. Exiting script.")
    exit()

# Load temperature and humidity data
temperature_humidity_file = 'data_log.csv'
try:
    temperature_humidity_data = pd.read_csv(temperature_humidity_file)
    print(f"Loaded {temperature_humidity_file}:\n", temperature_humidity_data.head())
except FileNotFoundError:
    print(f"Error: {temperature_humidity_file} not found. Exiting script.")
    exit()

# Check if datasets have the same number of rows
if len(bubble_height_data) == len(temperature_humidity_data):
    # Combine datasets row-by-row
    combined_data = pd.concat([bubble_height_data.reset_index(drop=True),
                               temperature_humidity_data.reset_index(drop=True)], axis=1)
    print("Combined data:\n", combined_data.head())

    # Save combined dataset
    output_file = 'combined_starter_data.csv'
    combined_data.to_csv(output_file, index=False)
    print(f"Combined data saved to {output_file}")
else:
    print(f"Row mismatch: {bubble_height_file} has {len(bubble_height_data)} rows, "
          f"{temperature_humidity_file} has {len(temperature_humidity_data)} rows. Cannot combine.")