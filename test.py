import webbrowser
import pandas as pd

# Load the CSV file
df = pd.read_csv('traffic_cameras_metadata.csv')

# Fetch the public video URL from the first row
stream_url = df.loc[0, 'publicVideoURL']

# Open the video stream in the default browser
webbrowser.open(stream_url)
