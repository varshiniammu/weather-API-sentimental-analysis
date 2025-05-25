CREATE OR REPLACE DATABASE weather_analysis;
USE DATABASE weather_analysis;


CREATE OR REPLACE SCHEMA sentimental_schema;
USE SCHEMA sentimental_schema;


CREATE OR REPLACE TABLE new_tables (
    condition STRING,
    country STRING,
    humidity FLOAT,
    location STRING,
    sentiment STRING,
    temperature_c FLOAT,
    wind_kph FLOAT
);


CREATE OR REPLACE FILE FORMAT weather_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  ESCAPE_UNENCLOSED_FIELD = NONE
  NULL_IF = ('NULL', 'null')
  TRIM_SPACE = TRUE;


 CREATE OR REPLACE STAGE sentiment_stage
  URL = 's3://bucket-name/output/'
  CREDENTIALS = (
    AWS_KEY_ID = 'aws-accesskey-id'
    AWS_SECRET_KEY = 'aws-secretkey-id'
  )
  FILE_FORMAT = weather_format;

CREATE OR REPLACE TASK load_s3_task
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = 'USING CRON */5 * * * * UTC'  
AS
COPY INTO new_tables
FROM @sentiment_stage
FILE_FORMAT = (FORMAT_NAME = 'weather_format')
ON_ERROR = 'CONTINUE';


ALTER TASK load_s3_task RESUME;
LIST @sentiment_stage;
SELECT * FROM new_tables;
