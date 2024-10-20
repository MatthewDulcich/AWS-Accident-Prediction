import cv2
from ultralytics import solutions

filename='' # Insert path to video here
output_filename='output_speeds.avi' # Insert path for an output annotated video with speeds

cap = cv2.VideoCapture(filename)

assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

video_writer = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Get pixel region where you want to calculate speed
# [(low_x,high_y),(high_x,high_y),(high_x,low_y),(low_x,low_y)]
speed_region = [(int(w/3),int(4*h/5)),(w,int(4*h/5)),(w,0),(int(w/3),0)]

# Initalize YOLO model for speed detection of cars
speed = solutions.SpeedEstimator(model="yolo11n.pt", region=speed_region, show=True)

while cap.isOpened():
    success, im0 = cap.read()
    # If frame was read, estimate speeds in frame and write annotated frame to video
    if success:
        out = speed.estimate_speed(im0)
        video_writer.write(im0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    print("Video frame is empty or video processing has been successfully completed.")
    break

cap.release()
cv2.destroyAllWindows()
