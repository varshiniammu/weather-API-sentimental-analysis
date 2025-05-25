from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import sys

# Get job arguments (using standard JOB_NAME)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define schema for weather data
schema = StructType([
    StructField("location", StringType()),
    StructField("country", StringType()),
    StructField("temperature_c", DoubleType()),
    StructField("condition", StringType()),
    StructField("humidity", IntegerType()),
    StructField("wind_kph", DoubleType())
])

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "13.127.109.22:9092") \
    .option("subscribe", "my-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON
parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select(
        col("data.location"),
        col("data.country"),
        col("data.temperature_c"),
        col("data.condition"),
        col("data.humidity"),
        col("data.wind_kph")
    )

# Simple keyword-based sentiment analysis
positive_words = ["sunny", "clear", "bright", "warm", "pleasant", "good", "nice"]
negative_words = ["rain", "storm", "cloudy", "cold", "fog", "snow", "bad", "windy"]

def simple_sentiment(text):
    if text:
        text_lower = text.lower()
        for w in positive_words:
            if w in text_lower:
                return 1.0
        for w in negative_words:
            if w in text_lower:
                return -1.0
    return 0.0

sentiment_udf = udf(simple_sentiment, DoubleType())

sentiment_df = parsed_df.withColumn("sentiment", sentiment_udf(col("condition")))

# Output to S3
output_path = "s3://bucket-name/glue-output/"
checkpoint_path = "s3://bucket-name/checkpoints/"

query = sentiment_df.writeStream \
    .format("csv") \
    .option("path", output_path) \
    .option("checkpointLocation", checkpoint_path) \
    .option("header", "true") \
    .outputMode("append") \
    .start()

query.awaitTermination()
job.commit()
