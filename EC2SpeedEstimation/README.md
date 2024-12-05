# Traffic Speed Estimation in EC2

## Setup and description of our process
This folder contains codes to use EC2 instances to estimate the speeds of traffic from input mp4 videos. To start, using free tier resources, either the file EC2SpeedEstimationSetup.sh has to be executed within the EC2 instance, or EC2SpeedEstimationSetupUserData.sh can be added to the "User Data" section when launching an EC2 instance. This will install dependencies needed. Next, the policy EC2SpeedEstimationPolicy.json will have to be created as an IAM policy and attached to an IAM role, which is then attached to an EC2 instance. This will grant access to input and output buckets specified. In addition, the input and output buckets need to have IAM users listed for access in the bucket policies to allow the user to grab the data in EC2.  

Once the dependencies are installed and access to S3 buckets are granted, you can ssh into the EC2 bucket. The speed_estimation.py file needs to be added and one of the cronjobs from cronjobs.txt has to be added to the crontab to automate running the script. The way we ran this process is that we had 5 EC2 instances with a cronjob to run the .py file every 5 minutes, with each instance using a cronjob offset from the previous by one minute. This made the instances run inference on different files each time in a round robin fashion. This spread out the compute power to avoid overloading one instance and keep up processing the real time data.

## Files

### cronjobs.txt  
This file contains the cronjobs needed for each of the five EC2 instances that were run.

### EC2SpeedEstimationPolicy.json  
This is the IAM policy created for an EC2 instance running this process.

### EC2SpeedEstimationSetup.sh  
This bash script can be run in an EC2 instance to setup the environment with necessary dependencies. The script install pip, cronie for running cronjobs, a software dependency for opencv, and required python libraries.  

### EC2SpeedEstimationSetupUserData.sh  
This bash script is similar to the one above, but is meant to run as a User Data file for initialization in an EC2 instance. The main differences are not using "sudo" as it is ran from the root user by default in User Data, needing systemctl start for crontab and specifying "/home/ec2-user" for the requirements file as I wanted it in a location I knew where it was if needed.  

### requirements.txt  
File containing python dependencies needed.

### speed_estimation.py  
This function uses the ultralytics YOLOv11n model to estimate the speeds of incoming videos. The function lists the input bucket contents from the previous minute, makes sure there isn't already output for those files, then runs the model on each of the videos outputting an annotated video with speeds and a csv with the average traffic speed, number of cars, time of video, and video ID. The video ID is currently specified for the camera we were looking at last, but can be changed to any and automatically changed if the ID is passed to the script as an argument (could be potential future work).
