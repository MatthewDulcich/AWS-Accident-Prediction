!pip install ultralytics

# Use a pytorch model

import cv2
from ultralytics.solutions import SpeedEstimator
from pandas import DataFrame
import boto3
from os import remove

# Choose input and output buckets
input_bucket_name = 'jfrechmsml650videos'
output_bucket_name = 'jfrechmsml650output'

# List files in video directory
s3 = boto3.client('s3')
files = s3.list_objects(Bucket = input_bucket_name)
files = [i['Key'] for i in files['Contents']]

# List files already in output directory
written_output_files = s3.list_objects(Bucket=output_bucket_name, Prefix='csv/', Delimiter='/')
written_output_files = [i['Key'].split('csv/')[1] for i in written_output_files['Contents'][1:]]
written_output_files = [i.split('_test')[0] for i in written_output_files]
written_output_files

# Get the new files where no analysis has been done
new_files = [i for i in files if i.split(".")[0] not in written_output_files]

# Run analysis on all new files
for file in new_files:
    #input_video_file = "cctv052x2004080516x01638.avi"
    output_video_file = f"{file.split('.')[0]}_test.avi"
    output_csv = f"{file.split('.')[0]}_test.csv"
    s3.download_file(Bucket = input_bucket_name,
                     Key = file,
                     Filename = file)

    # Load video and get width, height, fps
    cap = cv2.VideoCapture(file)
    #cap = cv2.VideoCapture('cctv052x2004080516x01638.avi')
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # initialize writer for output video
    video_writer = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    # region is [(left,bottom),(right,bottom),(right,top),(left,top)]
    speed_region = [(int(w/3),int(4*h/5)),(w,int(4*h/5)),(w,int(3*h/5)),(int(w/3),int(3*h/5))]
    speed = SpeedEstimator(model="yolo11n.pt", region=speed_region, show=False)

    # Analyze frames of video
    frame_speeds = []
    while cap.isOpened():
        success, im0 = cap.read()

        if success:
            out = speed.estimate_speed(im0)
            # Get only values not equal to 0 and convert to mph
            # 1 km = 0.621371 mi
            frame_speed = [i * 0.621371 for i in speed.spd.values() if i != 0]
            frame_speeds = frame_speeds + frame_speed

            video_writer.write(im0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            continue

        print("Video frame is empty or video processing has been successfully completed.")
        break
    cap.release()
    cv2.destroyAllWindows()

    # Get statistics from video...
    # Get count of cars and average traffic speed
    n_cars = len(speed.trkd_ids)

    # Take the average of all speeds computed in video
    if n_cars == 0 or not frame_speeds: # If no cars or no speeds computed
        traffic_speed = -1
    else:
        traffic_speed = (sum(frame_speeds)/len(frame_speeds)).item()

    # Upload output video to s3
    s3.upload_file(output_video_file, output_bucket_name, f'videos/{output_video_file}')

    # Create output csv and upload to s3
    output = DataFrame([n_cars,traffic_speed],index=['n_cars','traffic_speed']).T
    output.to_csv(output_csv,index=False)
    s3.upload_file(output_csv, output_bucket_name, f'csv/{output_csv}')

    # Remove files downloaded locally as they are saved in s3
    remove(file)
    remove(output_video_file)
    remove(output_csv)
