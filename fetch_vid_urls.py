import requests
import pandas as pd

# URL that returns the JSON data for all cameras
json_url = "https://chartexp1.sha.maryland.gov/CHARTExportClientService/getCameraMapDataJSON.do"

# Fetch the JSON response
response = requests.get(json_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = response.json()
    
    # Extract the camera data
    camera_data = data.get('data', [])
    
    # Create a DataFrame to store all the camera metadata, with an index column
    df = pd.DataFrame(camera_data)
    df.index = range(1, len(df) + 1)  # Adding index starting from 1
    
    # Print or display the DataFrame
    print(df.head())  # Display the first few rows of the DataFrame

    # Optionally, save the DataFrame to a CSV file with index
    df.to_csv('traffic_cameras_metadata.csv', index_label='Index')
else:
    print("Failed to fetch the JSON data")
