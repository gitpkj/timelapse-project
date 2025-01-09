import pandas as pd
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_file, save
import plotly.express as px

# Load data
data = pd.read_csv("combined_starter_data.csv")
print("Data loaded successfully:")
print(data.head())

# Add a Time column if needed
if 'Time' not in data.columns:
    data['Time'] = range(len(data))

# Matplotlib Example
plt.style.use('ggplot')
data.plot(x='Time', y='Starter Height (Pixels)', title='Starter Height Over Time')
plt.xlabel("Time (Hours)")
plt.ylabel("Starter Height (Pixels)")
plt.show()

# Plotly Example
fig = px.line(data, x='Time', y='Starter Height (Pixels)', title='Starter Height Over Time')
fig.show()

# Bokeh Example
output_file("bokeh_starter_height.html", title="Starter Height and Temperature Over Time")

# Create Bokeh figure
p = figure(title="Starter Height and Temperature Over Time",
           x_axis_label='Time (Hours)', y_axis_label='Starter Height (Pixels)',
           width=800, height=400, tools="pan,box_zoom,reset")

# Add lines for Starter Height and Temperature
p.line(data['Time'], data['Starter Height (Pixels)'], legend_label="Starter Height (Pixels)", line_width=2, color="blue")
p.line(data['Time'], data['Temperature (°F)'], legend_label="Temperature (°F)", line_width=2, color="red")

# Customize legend
p.legend.title = "Metrics"
p.legend.location = "top_left"
p.legend.click_policy = "hide"

# Show and save Bokeh plot
save(p)
show(p)