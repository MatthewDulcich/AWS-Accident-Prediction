# AWS-Accident-Prediction
Using AWS resources we estimate the speeds of vehicles and detect any anomalies in traffic flow for real-time traffic cameras around the state of Maryland.

## Subdirectories

### anomaly-detection-models
We determine any anomalies in traffic flow using the AWS provided random cut forest (RCF) model on SageMaker and invoke it to run using AWS endpoints.

### EC2SpeedEstimation
We use EC2 instances to run the YOLOv11 model for object detection and speed estimation within the Maryland traffic cameras. This process is automated to run as long as the instances are running.
