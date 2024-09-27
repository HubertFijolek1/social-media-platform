import logging
import json
import sys
from fastapi import FastAPI
import uvicorn
from kafka import KafkaConsumer
import threading
import redis

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'timeline-service',
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'funcName': record.funcName,
            'lineno': record.lineno,
        }
        return json.dumps(log_record)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(JsonFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger('timeline-service')

app = FastAPI()

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'tweets',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

def consume_tweets():
    for message in consumer:
        tweet = message.value
        user_id = tweet['user_id']
        # Get followers (simplified)
        followers = get_followers(user_id)
        for follower_id in followers:
            key = f'timeline:{follower_id}'
            redis_client.lpush(key, json.dumps(tweet))
            redis_client.ltrim(key, 0, 99)  # Keep latest 100 tweets
        logger.info('Tweet added to timelines', extra={'tweet': tweet})

def get_followers(user_id):
    # Placeholder function
    return ['user1', 'user2', 'user3']

# Start Kafka consumer in a separate thread
threading.Thread(target=consume_tweets, daemon=True).start()

@app.get('/timelines/{user_id}')
async def get_timeline(user_id: str):
    key = f'timeline:{user_id}'
    timeline = redis_client.lrange(key, 0, -1)
    timeline = [json.loads(tweet) for tweet in timeline]
    return {'timeline': timeline}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
