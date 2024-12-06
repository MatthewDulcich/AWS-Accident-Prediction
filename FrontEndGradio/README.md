### Setting up the EC2
Follow steps 3-5 for the following article to set up your EC2 instance (https://abdulrahman-almutlaq.medium.com/deploying-gradio-on-aws-a-beginners-quick-start-guide-85a01f269945)

### Running the server
1. Within the EC2 instance commandline, run front_end.py within the main folder itself. Make sure that the EC2 instance and the corresponding S3 bucket has the exact file structure given.
EC2:
    -master.csv
    -avi_videos
     -- 
    -videos
     -- 
    -track_s3_predicitons.py
    -get_video_bucket.py

S3 bucket:
    -predictions.csv
    -avi_videos
      --
    -videos
      --

2. The code will return the URL as http://0.0.0.0:<server-port>. On your browser, in the top bar input it as http://<elastic-ip-address>:<server-port> (e.g if your elastic ip is 153.12.14.2 and the url is http://0.0.0.0:7860, the browser url should be  http://153.12.14.2:7860)