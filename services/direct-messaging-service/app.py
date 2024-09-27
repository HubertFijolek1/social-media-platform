import logging
import json
import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import uuid
from datetime import datetime
import redis

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'direct-messaging-service',
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

logger = logging.getLogger('direct-messaging-service')

app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Pydantic models
class Message(BaseModel):
    sender_id: str
    recipient_id: str
    content: str

@app.post('/messages/')
async def send_message(message: Message):
    conversation_id = get_conversation_id(message.sender_id, message.recipient_id)
    message_id = str(uuid.uuid4())
    message_data = {
        'message_id': message_id,
        'sender_id': message.sender_id,
        'recipient_id': message.recipient_id,
        'content': message.content,
        'timestamp': datetime.utcnow().isoformat()
    }
    key = f'conversation:{conversation_id}'
    redis_client.rpush(key, json.dumps(message_data))
    logger.info('Message sent', extra={'message': message_data})
    return {'status': 'success', 'message': message_data}

@app.get('/messages/{conversation_id}')
async def get_messages(conversation_id: str):
    key = f'conversation:{conversation_id}'
    messages = redis_client.lrange(key, 0, -1)
    messages = [json.loads(msg) for msg in messages]
    return {'conversation_id': conversation_id, 'messages': messages}

def get_conversation_id(user1, user2):
    # Generate a consistent conversation ID for the pair of users
    return '-'.join(sorted([user1, user2]))

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
