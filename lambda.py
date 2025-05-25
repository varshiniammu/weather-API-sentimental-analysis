import boto3
from datetime import datetime
import requests
import json
import os
from kafka import KafkaProducer

# Environment variable
API_KEY = os.environ.get("WEATHER_ID")

# Base URL for the Weather API
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# Kafka settings
KAFKA_BROKER = "EC2 public IP"  # 👈 Replace with your EC2 IP
KAFKA_TOPIC = "topic-name"

def get_weather_data(location):
    if not API_KEY:
        return {"error": "❌ WEATHER_ID is missing in environment variables!"}

    url = f"{BASE_URL}?key={API_KEY}&q={location}&aqi=no"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        location_info = data.get("location", {})
        current_weather = data.get("current", {})

        return {
            "location": location_info.get("name", "N/A"),
            "country": location_info.get("country", "N/A"),
            "temperature_c": current_weather.get("temp_c", "N/A"),
            "condition": current_weather.get("condition", {}).get("text", "N/A"),
            "humidity": current_weather.get("humidity", "N/A"),
            "wind_kph": current_weather.get("wind_kph", "N/A")
        }
    else:
        return {"error": f"Failed to fetch data. Status code: {response.status_code}"}

def lambda_handler(event, context):
    # Default locations
    locations = event.get("locations", [
        "India", "London", "New York", "Paris", "Tokyo", "Beijing", "Bangkok", "Dubai",
        "Berlin", "Madrid", "Rome", "Amsterdam", "Los Angeles", "Toronto", "Chicago",
        "San Francisco", "São Paulo", "Buenos Aires", "Lima", "Bogotá",
        "Cape Town", "Nairobi", "Cairo", "Lagos", "Sydney", "Melbourne"
    ])

    weather_data = []

    # Initialize Kafka producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        return {"error": f"❌ Failed to connect to Kafka: {str(e)}"}

    # Process each location
    for location in locations:
        print(f"Processing location: {location}")
        weather = get_weather_data(location)
        weather_data.append(weather)

        # Send to Kafka topic
        try:
            producer.send(KAFKA_TOPIC, value=weather)
        except Exception as e:
            print(f"⚠️ Failed to send to Kafka: {str(e)}")

    producer.flush()

    # Save to S3
    s3_client = boto3.client('s3')
    filename = "weather_raw_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"

    try:
        s3_client.put_object(
            Bucket="bucket-name",
            Key="folder-name" + filename,
            Body=json.dumps(weather_data)
        )
    except Exception as e:
        return {"error": f"❌ Failed to upload to S3: {str(e)}"}

    return {
        "statusCode": 200 if not any("error" in d for d in weather_data) else 500,
        "headers": {"Content-Type": "application/json"},
        "body": weather_data
    }
