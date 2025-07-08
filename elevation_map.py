from ridge_map import RidgeMap
import matplotlib.pyplot as plt


#boundingbox.klokantech.com
# Define the bounding box coordinates for Mt. Shasta
# boundingbox.klokantech.com

mt_shasta_bbox = (-122.5, 41.25, -122.0, 41.5)
kp_bbox = (99.944000,9.653216,100.095406,9.806165)
#http://bboxfinder.com/#9.653216,99.944000,9.806165,100.095406

# Create the RidgeMap instance
rm = RidgeMap(kp_bbox)

# Get elevation data
values = rm.get_elevation_data(num_lines=150)
print (values)
# Preprocess data
values = rm.preprocess(values=values, lake_flatness=.5, water_ntile=0, vertical_ratio=100)

# Plot the map
rm.plot_map(values=values, label='Koh Pha ngan', 
                label_y=0.1, label_x=0.55, label_size=40, 
                linewidth=1, line_color=plt.get_cmap('copper'), 
                kind='elevation')
plt.show()