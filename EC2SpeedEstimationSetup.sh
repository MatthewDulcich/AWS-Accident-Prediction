#! /bin/bash

# Install pip on EC2 instance.
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
rm get-pip.py

echo 'export PATH=~/.local/bin:$PATH' >> ~/.bash_profile

source ~/.bash_profile

# Install cronie for crontab
sudo yum install cronie cronie-anacron

# Library needed for opencv
sudo yum install mesa-libGL

# Create requirements.txt
# Use CPU only pytorch for t2.micro instance without any GPUs and not enough
# space for full pytorch
# Need numpy < 2.0
echo "--extra-index-url https://download.pytorch.org/whl/cpu" > requirements.txt
echo "numpy==1.23.0" >> requirements.txt
echo "opencv-python" >> requirements.txt
echo "ultralytics" >> requirements.txt
echo "boto3" >> requirements.txt

# Install requirements for speed estimation
pip install -r requirements.txt
