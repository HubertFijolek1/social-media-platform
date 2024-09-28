from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StringType, TimestampType

KAFKA_TOPIC = 'tweets'
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'

schema = StructType() \
    .add("user_id", StringType()) \
    .add("tweet_id", StringType()) \
    .add("content", StringType()) \
    .add("timestamp", StringType())

spark = SparkSession.builder \
    .appName("TweetAnalytics") \
    .getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

tweets_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

tweets_df = tweets_df.withColumn("timestamp", col("timestamp").cast(TimestampType()))

tweet_counts = tweets_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(
        window(col("timestamp"), "1 minute", "30 seconds"),
        col("user_id")
    ).count()

query = tweet_counts \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
