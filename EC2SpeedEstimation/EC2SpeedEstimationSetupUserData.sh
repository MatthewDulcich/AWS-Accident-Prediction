#! /bin/bash

# Install pip on EC2 instance.
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
rm get-pip.py

echo 'export PATH=~/.local/bin:$PATH' >> ~/.bash_profile

source ~/.bash_profile

# Install cronie for crontab
yum install cronie cronie-anacron -y
systemctl start crond.service

# Library needed for opencv
yum install mesa-libGL -y

# Create requirements.txt
# Use CPU only pytorch for t2.micro instance without any GPUs and not enough
# space for full pytorch
# Need numpy < 2.0
echo "--extra-index-url https://download.pytorch.org/whl/cpu" > /home/ec2-user/requirements.txt
echo "numpy==1.23.0" >> /home/ec2-user/requirements.txt
echo "opencv-python" >> /home/ec2-user/requirements.txt
echo "ultralytics" >> /home/ec2-user/requirements.txt
echo "boto3" >> /home/ec2-user/requirements.txt

# Install requirements for speed estimation
pip install -r /home/ec2-user/requirements.txt
