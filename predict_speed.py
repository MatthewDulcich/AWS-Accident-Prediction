import cv2
from ultralytics.solutions import SpeedEstimator
from numpy import mean
from pandas import DataFrame

# Choose video and create name for output files
input_video_file = ".avi"
output_video_file = ".avi"
output_csv = ".csv"

# Load video and get width, height, fps
cap = cv2.VideoCapture(input_video_file)
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# initialize writer for output video
video_writer = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# region is [(left,top),(right,top),(right,bottom),(left,bottom)]
speed_region = [(int(w/3),int(4*h/5)),(w,int(4*h/5)),(w,0),(int(w/3),0)]
speed = SpeedEstimator(model="yolo11n.pt", region=speed_region, show=False)

frame_speeds=[]
while cap.isOpened():
    success, im0 = cap.read()

    if success:
        out = speed.estimate_speed(im0)
        # Get only values not equal to 0 and convert to mph
        # 1 km = 0.621371 mi
        frame_speed = [i*0.621371 for i in speed.spd.values() if i != 0]
        frame_speeds = frame_speeds + frame_speed

        video_writer.write(im0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    print("Video frame is empty or video processing has been successfully completed.")
    break

cap.release()
cv2.destroyAllWindows()

# Get count of cars and average traffic speed
n_cars = len(speed.trkd_ids)
# Take the average of all speeds computed in video
traffic_speed = mean(frame_speeds)

# Save results
results = DataFrame({'n_cars':n_cars,'traffic_speed':traffic_speed},index=[0])
results.to_csv(output_csv,index=False)
