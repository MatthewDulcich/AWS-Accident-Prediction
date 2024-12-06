# Lambda Video Processing Function Setup

This guide provides step-by-step instructions for creating the `function.zip` file required to deploy the AWS Lambda function for video processing. The function utilizes the `ffmpeg` library to convert `.ts` files into `.mp4` format.

---

## Prerequisites

Before proceeding, ensure you have the following:

1. **Operating System**:
   - Unix-based OS (macOS/Linux) or a Unix-like environment (e.g., WSL on Windows).
2. **Tools and Dependencies**:
   - `wget` (or a web browser) to download files.
   - Basic familiarity with terminal/command-line operations.
3. **Files Needed**:
   - Your Python script (`lambda_function.py`) containing the Lambda function logic.

---

## Steps to Create `function.zip`

### 1. Download the Static Build of `ffmpeg`

The Lambda function requires a static build of `ffmpeg`. You can download it from [John Van Sickle's ffmpeg page](https://johnvansickle.com/ffmpeg/).

If using a browser:
- Open [https://johnvansickle.com/ffmpeg/](https://johnvansickle.com/ffmpeg/).
- Download the appropriate static build for your system (e.g., Linux, macOS, etc.).

```bash
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz
```

---

### 2. Extract the `ffmpeg` Build

Once the download is complete, extract the tar file to access the `ffmpeg` binary. This will create a folder containing the static `ffmpeg` binary.

```bash
tar -xvf ffmpeg-release-i686-static.tar.xz
```
---

### 3. Prepare the Lambda Function Files

Create a folder named `lambda_function` and copy the necessary files into it.

1. Place the `ffmpeg` binary from the extracted folder into the `lambda_function` directory.
2. Add your `lambda_function.py` script to the same directory.

Ensure the folder contains:
- `ffmpeg`
- `lambda_function.py`

```bash
mkdir lambda_function
cp ffmpeg-<version>-static/ffmpeg lambda_function/
cp /path/to/your/lambda_function.py lambda_function/
```
---

### 4. Package the Files into a ZIP Archive

Navigate to the `lambda_function` directory and create a ZIP archive containing all files.

The resulting file should be named `function.zip` and include:
- `lambda_function.py`
- `ffmpeg`

```bash
cd lambda_function
zip -r ../function.zip .
```

---

### 5. Verify the ZIP File

Check the contents of the `function.zip` archive to ensure it includes all necessary files. If any file is missing, repeat the packaging steps.

```bash
unzip -l ../function.zip
```

---

## Deployment Instructions

Once the `function.zip` file is ready, you can deploy it to AWS Lambda via the console or CLI.

### Deploy via AWS Console:
1. Open the **AWS Lambda console**.
2. Select your function or create a new one.
3. In the **Code** section, click **Upload from > .zip file** and select the `function.zip` file.
4. Save the changes.

### Deploy via AWS CLI:
Upload the `function.zip` file using AWS CLI by specifying your function name and zip file path.

```bash
aws lambda update-function-code --function-name YourLambdaFunctionName --zip-file fileb://function.zip
```

---

## Notes and Tips

1. **Avoid Permission Errors**:
   Ensure the `ffmpeg` binary is executable before adding it to the ZIP file.

2. **Lambda File Size Limits**:
   - Direct upload limit: 50MB.
   - For larger files, upload `function.zip` to an S3 bucket and link it to Lambda OR you may increase the size limit in `Configurations` section of a lambda function

3. **Troubleshooting `ffmpeg`**:
   If the static build of `ffmpeg` doesn’t work as expected, download a different version from [John Van Sickle’s website](https://johnvansickle.com/ffmpeg/).

4. **Keep Dependencies Minimal**:
   Only include necessary files in the `function.zip` archive to reduce its size and improve performance.

---

By following this guide, you can recreate the `function.zip` file as needed for your Lambda function. For further assistance, refer to [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html) or [John Van Sickle's ffmpeg page](https://johnvansickle.com/ffmpeg/).