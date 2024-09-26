import logging
import json
import sys
from fastapi import FastAPI, WebSocket
import uvicorn
from kafka import KafkaConsumer
import threading

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'notification-service',
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

logger = logging.getLogger('notification-service')

app = FastAPI()

# In-memory storage for connected WebSocket clients
connected_users = {}

# Kafka Consumer to listen to events
consumer = KafkaConsumer(
    'notifications',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def consume_notifications():
    for message in consumer:
        notification = message.value
        user_id = notification['user_id']
        if user_id in connected_users:
            websocket = connected_users[user_id]
            # Send notification via WebSocket
            try:
                websocket.send_text(json.dumps(notification))
                logger.info('Notification sent', extra={'notification': notification})
            except Exception as e:
                logger.error(f'Error sending notification: {e}', extra={'user_id': user_id})
                del connected_users[user_id]

# Start Kafka consumer in a separate thread
threading.Thread(target=consume_notifications, daemon=True).start()

@app.websocket("/notifications/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    connected_users[user_id] = websocket
    logger.info('User connected to WebSocket', extra={'user_id': user_id})
    try:
        while True:
            # Keep the connection open
            await websocket.receive_text()
    except Exception as e:
        logger.error(f'WebSocket connection error: {e}', extra={'user_id': user_id})
    finally:
        del connected_users[user_id]
        await websocket.close()
        logger.info('User disconnected from WebSocket', extra={'user_id': user_id})

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
