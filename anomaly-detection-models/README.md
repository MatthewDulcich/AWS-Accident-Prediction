Within this folder we have a few main files. First we have full_process.ipynb which is the Sagemaker Notebook that we used to make the model. It has the full preprocessing steps, the model training, the endpoint deployment, and the endpoint invoking.
Next we have the folder for the lambda_function. In this folder we have the code to deploy in the function as well as the policies that need to be attached to the role to make it work.
For the policies we have the S3 and Sagemaker policies that must be attached to get this to work.

In order for us to pull from the Speed Estimation bucket, we must add an automation to the bucket to send a notification to lambda whenever the bucket has a file added to it.

Setup:
As you go through the process add the given policies to roles for the given services and adjust the resource names and role names as needed 
1. Setup sagemaker notebook and upload the full_process.ipynb notebook 
	a. run the notebook, make sure to use the correct endpoint name in the invoke_endpoint code block near the bottom
	b. copy the endpoint name
2. Setup a lambda function to python 3.10
	a. add the aws layer for python3.10 for pandas
	b. up the memory allowed for the lambda function to 256
3. Setup the S3 bucket
