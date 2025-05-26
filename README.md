# 🌦️ Real-Time Weather Sentiment Analysis Pipeline

This project implements a real-time data pipeline that ingests weather data from an API, stores it in Amazon S3, streams it via Kafka, processes it using PySpark for sentiment analysis, and visualizes the results with Power BI, using Snowflake as the analytics layer.


## 🔧 Technologies Used

- Weather API
- Amazon S3
- EC2
- Apache Kafka
- Apache Spark (PySpark)
- Snowflake
- Power BI

## 🔄 Data Flow


[Weather API]
      ↓
[Amazon S3 Bucket: to_processed/]
      ↓
[EC2 Python Script → Kafka Topic]
      ↓
[PySpark Streaming: Sentiment Analysis]
      ↓
[Amazon S3 Bucket: processed/sentiments/]
      ↓
[Snowflake Data Warehouse]
      ↓
[Power BI Dashboard]



## 🧠 Sentiment Analysis Logic

The sentiment score is calculated using a custom Python-based algorithm without relying on external libraries like TextBlob, NLTK, or transformers.

### How it works:
- The algorithm analyzes the presence of predefined positive and negative words.
- Each word contributes to a sentiment score.
- Final sentiment is determined based on the computed polarity:

- Positive: score > 0.1  
- Neutral: -0.1 ≤ score ≤ 0.1  
- Negative: score < -0.1


## 📊 Example Output
| Weather Condition | Sentiment Score |
| ----------------- | --------------- |
| Sunny             | 0.78            |
| Clear             | 0.72            |
| Partly cloudy     | 0.35            |
| Mist              | -0.23           |
| Overcast          | -0.41           |
| Rain              | -0.58           |
| Thunderstorm      | -0.75           |
| Snow              | 0.10            |
| Fog               | -0.30           |
| Drizzle           | -0.40           |
| Hot and humid     | -0.55           |
| Cool breeze       | 0.60            |



## 📂 Project Files

- [lambda_kafka.py](lambda.py) — AWS Lambda function code that fetches weather from the Weather API and pushes data to Kafka on EC2.
- [glue.py](glue.py) — AWS Glue script that reads weather data from Kafka, performs sentiment analysis, and writes results to S3.
- [snowflake.sql](snowflake.sql) — SQL script used to create tables and load data into Snowflake from S3.



## ⚙️ Configuration Setup

Before running the project, make sure to configure the following:

- *AWS Credentials:*
  - AWS_ACCESS_KEY_ID — Your AWS Access Key ID
  - AWS_SECRET_ACCESS_KEY — Your AWS Secret Access Key
  - These credentials are needed for AWS Lambda, Glue, and S3 access.

- *AWS Lambda Environment Variables:*
  - NEWS_API_KEY — Your News API key to fetch news data.
  - KAFKA_BROKER — Kafka broker address (e.g., ec2-public-ip:9092).

- *AWS Glue:*
  - Ensure the Glue job has the correct IAM role permissions to read from Kafka and write to S3.
  - - Configure the Glue job as a *streaming job* to continuously process incoming Kafka data.
  - Upload the required *JAR dependencies* to an S3 bucket, then reference their paths in the job configuration under --extra-jars. Example JARs include:
    - spark-sql-kafka-0-10_2.12.jar
    - kafka-clients.jar
    - Any other compatible Kafka and Spark JARs for your Glue version.
  - Add the JAR S3 path like this in the job’s parameters:

- *Snowflake:*
  - Configure Snowflake connection parameters (username, password, account, warehouse, database, schema).
  - Set up a Snowflake task to load data from S3 every 5 minutes.

- *Power BI:*
  - Connect Power BI to your Snowflake data warehouse.
  - (Note: Power BI refresh is manual.)

- *EC2 Instance (Kafka Broker):*
  - Kafka is hosted on an EC2 instance.
  - Make sure:
    - Kafka is installed and running on *port 9092*.
    - EC2 security group allows *inbound TCP traffic on port 9092*.
    - Kafka is configured to advertise the *public IP address*.


 Automation Triggers:
  - Lambda Trigger: Create a CloudWatch EventBridge rule to trigger the Lambda function every **15 minutes.
  - *Snowflake Task: Set up to run every **5 minutes* to load newly arrived S3 data.
  - *Glue Streaming Job: Automatically picks up new Kafka data as it arrives.
 

🔐 Security & Monitoring

Use IAM Roles for S3/Kafka/EC2 access.

Enable CloudWatch for logging EC2 and Spark jobs.

Monitor Kafka metrics and Spark UI.

Use Snowflake usage dashboards and Power BI alerts.



## Architecture Diagram

![Architecture](architecture.jpge)

## ✅ Conclusion

This project demonstrates a robust, cloud-native data pipeline for real-time weather sentiment analysis. By integrating services like Amazon S3, Kafka, PySpark, Snowflake, and Power BI, it showcases end-to-end data engineering — from ingestion to insightful visualization.The custom-built sentiment analysis logic ensures flexibility and independence from third-party NLP libraries, allowing for tailored analysis of weather descriptions.Weather for academic purposes, production-grade pipelines, or learning modern data workflows, this architecture provides a scalable and adaptable foundation.

