import logging
import json
import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from kafka import KafkaProducer
from datetime import datetime

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'tweet-service',
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

logger = logging.getLogger('tweet-service')

app = FastAPI()

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pydantic models
class TweetCreate(BaseModel):
    user_id: str
    content: str

@app.post('/tweets/')
async def create_tweet(tweet: TweetCreate):
    tweet_data = {
        'user_id': tweet.user_id,
        'tweet_id': str(datetime.utcnow().timestamp()),
        'content': tweet.content,
        'timestamp': datetime.utcnow().isoformat()
    }
    logger.info('New tweet created', extra={'tweet': tweet_data})
    # Publish tweet to Kafka
    producer.send('tweets', tweet_data)
    producer.flush()
    return {'status': 'success', 'tweet': tweet_data}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
