import cv2
import mss
import numpy as np
from ultralytics.solutions import SpeedEstimator
from numpy import mean
from pandas import DataFrame
import time

# Parameters
output_video_file = "test.mp4"
output_csv = "test.csv"

# Screen capture region (adjust coordinates as needed)
screen_region = {
    "top": 100,  # Replace with the top coordinate of the browser window
    "left": 100,  # Replace with the left coordinate of the browser window
    "width": 1280,  # Replace with the width of the region to capture
    "height": 720  # Replace with the height of the region to capture
}

# highlights the region to be captured
cv2.namedWindow("Screen Capture")
cv2.moveWindow("Screen Capture", 40, 30)
cv2.setWindowProperty("Screen Capture", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.createTrackbar("Top", "Screen Capture", screen_region["top"], 1000, lambda x: screen_region.update(top=x))
cv2.createTrackbar("Left", "Screen Capture", screen_region["left"], 1000, lambda x: screen_region.update(left=x))
cv2.createTrackbar("Width", "Screen Capture", screen_region["width"], 1000, lambda x: screen_region.update(width=x))
cv2.createTrackbar("Height", "Screen Capture", screen_region["height"], 1000, lambda x: screen_region.update(height=x))

# Initialize SpeedEstimator and video writer
speed_region = [(int(screen_region["width"]/3), int(4*screen_region["height"]/5)),
                (screen_region["width"], int(4*screen_region["height"]/5)),
                (screen_region["width"], 0),
                (int(screen_region["width"]/3), 0)]
speed = SpeedEstimator(model="yolo11n.pt", region=speed_region, show=False)

fps = 20  # Define the frames per second for output video
video_writer = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, 
                               (screen_region["width"], screen_region["height"]))

frame_speeds = []

# Start screen capture
with mss.mss() as sct:
    while True:
        # Capture the defined screen region
        screen = np.array(sct.grab(screen_region))
        im0 = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)  # Convert from BGRA to BGR for OpenCV

        # Run inference using SpeedEstimator
        out = speed.estimate_speed(im0)

        # Get only values not equal to 0 and convert to mph
        # 1 km = 0.621371 mi
        frame_speed = [i * 0.621371 for i in speed.spd.values() if i != 0]
        frame_speeds.extend(frame_speed)

        # Write frame to output video
        video_writer.write(im0)

        # Display the captured screen (optional)
        cv2.imshow("Screen Capture", im0)
        
        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        # Small delay to control FPS (adjust as needed)
        time.sleep(1 / fps)

print("Screen capture has been successfully completed.")
video_writer.release()
cv2.destroyAllWindows()

# Get count of cars and average traffic speed
n_cars = len(speed.trkd_ids)
traffic_speed = mean(frame_speeds)

# Save results to CSV
results = DataFrame({'n_cars': n_cars, 'traffic_speed': traffic_speed}, index=[0])
results.to_csv(output_csv, index=False)
print("Results saved to", output_csv)
