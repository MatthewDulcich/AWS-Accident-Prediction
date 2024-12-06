# AWS-Accident-Prediction
Using AWS resources we estimate the speeds of vehicles and detect any anomalies in traffic flow for real-time traffic cameras around the state of Maryland.

## Subdirectories

### anomaly-detection-models
We determine any anomalies in traffic flow using the AWS provided random cut forest (RCF) model on SageMaker and invoke it to run using AWS endpoints. For detailed setup instructions, refer to [anomaly-detection-models README](anomaly-detection-models/README.md)

### EC2SpeedEstimation
We use EC2 instances to run the YOLOv11 model for object detection and speed estimation within the Maryland traffic cameras. This process is automated to run as long as the instances are running. For detailed setup instructions, refer to [EC2SpeedEstimation README](EC2SpeedEstimation/README.md)

### Lambda Video Processing
This subdirectory contains the Lambda function for processing `.ts` video files and converting them into `.mp4` format using `ffmpeg`. It uses an event-driven architecture with S3 triggers to automate video preprocessing, making the files compatible with downstream tasks like speed estimation and anomaly detection. For detailed setup instructions, refer to the [Lambda Video Processing README](Lambda%20Video%20Processing/README.md).

###