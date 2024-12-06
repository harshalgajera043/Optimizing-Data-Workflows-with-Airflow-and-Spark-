
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Function to initialize Spark session
def init_spark():
    return SparkSession.builder \
        .appName("Airflow-Spark Pipeline") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

# Step 1: Data Ingestion
def ingest_data():
    spark = init_spark()
    # Simulated input dataset (Replace with actual source e.g., S3, HDFS)
    data = [
        {"id": 1, "value": 100, "category": "A"},
        {"id": 2, "value": 200, "category": "B"},
        {"id": 3, "value": 150, "category": "A"},
        {"id": 4, "value": 300, "category": "C"},
    ]
    df = spark.createDataFrame(data)
    df.write.mode("overwrite").parquet("/tmp/processed_data/input.parquet")

# Step 2: Data Processing
def process_data():
    spark = init_spark()
    # Load the data
    df = spark.read.parquet("/tmp/processed_data/input.parquet")
    # Perform transformation
    processed_df = df.groupBy("category").sum("value").withColumnRenamed("sum(value)", "total_value")
    processed_df.write.mode("overwrite").parquet("/tmp/processed_data/output.parquet")

# Step 3: Generate Insights
def generate_insights():
    spark = init_spark()
    # Load processed data
    processed_df = spark.read.parquet("/tmp/processed_data/output.parquet")
    # Display insights (can be exported to dashboards or databases)
    processed_df.show()

# Airflow DAG definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    'spark_pipeline_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Ingest data
    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data
    )

    # Task 2: Process data
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data
    )

    # Task 3: Generate insights
    insights_task = PythonOperator(
        task_id='generate_insights',
        python_callable=generate_insights
    )

    # Task Dependencies
    ingest_task >> process_task >> insights_task
