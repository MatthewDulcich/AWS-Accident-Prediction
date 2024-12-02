import numpy as np
import pandas as pd
import boto3
from datetime import datetime
import io
import csv
import json

# Initialize boto3 S3 client
s3_client = boto3.client('s3')

# Custom Standard Scaler function
def custom_standard_scaler(df, columns):
    for column in columns:
        mean = df[column].mean()
        std = df[column].std()
        df[column] = (df[column] - mean) / std
    return df

# Extract datetime components
def extract_date_info(dt):
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    weekday = dt.weekday()  # 0=Monday, 6=Sunday
    is_weekend = weekday >= 5

    first_day_of_month = dt.replace(day=1)
    week_of_month = (dt.day + first_day_of_month.weekday()) // 7 + 1

    if month in (12, 1, 2):
        season = "Winter"
    elif month in (3, 4, 5):
        season = "Spring"
    elif month in (6, 7, 8):
        season = "Summer"
    else:
        season = "Fall"

    return year, month, day, hour, minute, is_weekend, week_of_month, season

# Preprocess the data
def preprocess_expanded_df(data):
    data = data.drop(columns=["date_time"])
    data["is_weekend"] = data["is_weekend"].astype(int)
    
    season_mapping = {"Winter": 0, "Spring": 1, "Summer": 2, "Fall": 3}
    data["season"] = data["season"].map(season_mapping)
    
    def add_cyclical_features(data, column, max_value):
        data[f"{column}_sin"] = np.sin(2 * np.pi * data[column] / max_value)
        data[f"{column}_cos"] = np.cos(2 * np.pi * data[column] / max_value)
        return data

    data = add_cyclical_features(data, "month", 12)
    data = add_cyclical_features(data, "day", 31)
    data = add_cyclical_features(data, "hour", 24)
    data = add_cyclical_features(data, "minute", 60)
    data = add_cyclical_features(data, "week_of_month", 5)
    data = add_cyclical_features(data, "season", 4)
    data = add_cyclical_features(data, "year", 10)

    columns_to_drop = ["month", "day", "hour", "minute", "week_of_month", "season", "year"]
    data = data.drop(columns=columns_to_drop)
    
    data.loc[data['traffic_speed'] == -1, 'traffic_speed'] = 0

    # Convert columns to numeric and handle any errors
    numerical_columns = ["n_cars", "traffic_speed", "camera_id", "is_weekend"]
    for column in numerical_columns:
        data[column] = pd.to_numeric(data[column], errors='coerce')
        # Replace NaNs created by conversion errors with a default value (e.g., 0 or the mean)
        data[column].fillna(0, inplace=True)
    
    data = custom_standard_scaler(data, numerical_columns)  # Using custom scaler here
    
    return data

# Lambda function handler for CSV input and output
def lambda_handler(event, context):
    try:
        # Read the CSV from the event (assumes base64 encoded data if necessary)
        csv_data = event['body']
        
        # Decode and read CSV data into a pandas DataFrame
        decoded_data = io.StringIO(csv_data)
        df = pd.read_csv(decoded_data)

        # TEMP until we get the full data
        df['date_time'] = pd.to_datetime('2024-11-18 15:45:00')
        df['camera_id'] = '0'
        
        # Process the datetime column without using strptime
        df[['year', 'month', 'day', 'hour', 'minute', 'is_weekend', 'week_of_month', 'season']] = \
            df['date_time'].apply(lambda x: pd.Series(extract_date_info(x)))
        
        # Preprocess the data
        preprocessed_df = preprocess_expanded_df(df)

        # Prepare the data for the RCF model
        input_data = preprocessed_df.to_numpy().astype('float32')

        # Initialize the SageMaker client
        sagemaker_client = boto3.client('sagemaker-runtime')

        # Send the preprocessed data for inference
        input_data_csv = '\n'.join([','.join(map(str, row)) for row in input_data.tolist()])
        
        # Invoke the SageMaker endpoint
        response = sagemaker_client.invoke_endpoint(
            EndpointName='randomcutforest-2024-12-02-03-21-04-859',  # Replace with your endpoint name
            ContentType='text/csv',
            Body=input_data_csv
        )
        
        # Read the result from the response
        result = json.loads(response['Body'].read().decode())
        
        # Extract the scores from the result (assuming the response is structured correctly)
        prediction_results = [score['score'] for score in result['scores']]
        
        # Convert the prediction results into a DataFrame
        results_df = pd.DataFrame(prediction_results, columns=['score'])

        # Convert the DataFrame to CSV
        csv_output = results_df.to_csv(index=False)

        # Specify the S3 bucket and file
        output_bucket = 'dulcichmsml650bucket'
        output_file_name = 'predictions.csv'

        # Check if the file exists on S3
        try:
            s3_response = s3_client.get_object(Bucket=output_bucket, Key=output_file_name)
            existing_csv = s3_response['Body'].read().decode('utf-8')
            existing_df = pd.read_csv(io.StringIO(existing_csv))
            # Append the new data
            final_df = pd.concat([existing_df, results_df], ignore_index=True)
        except s3_client.exceptions.NoSuchKey:
            # If the file does not exist, just use the new data
            final_df = results_df

        # Convert the final DataFrame to CSV
        final_csv = final_df.to_csv(index=False)

        # Upload the final CSV back to S3
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_file_name,
            Body=final_csv,
            ContentType='text/csv'
        )

        # Return the S3 URL for the uploaded CSV
        s3_url = f"s3://{output_bucket}/{output_file_name}"

        return {
            'statusCode': 200,
            'body': f"CSV uploaded successfully to {s3_url}",
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f'Error processing data: {str(e)}'
        }
