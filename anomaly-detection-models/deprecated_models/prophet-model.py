import pandas as pd
from prophet import Prophet

# Example dataset
data = {
    'ds': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
    'y': [100, 120, 150, 130, 140]  # Number of cars/speed
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Ensure 'ds' column is datetime
df['ds'] = pd.to_datetime(df['ds'])

# Initialize and fit the Prophet model
model = Prophet()

# Fit the model
model.fit(df)

# Create future DataFrame
future = model.make_future_dataframe(periods=30)

# Predict future values
forecast = model.predict(future)

# Plot forecast
model.plot(forecast)

# Plot components (trend, weekly seasonality, yearly seasonality)
model.plot_components(forecast)