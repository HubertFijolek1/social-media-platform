import logging
import json
import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'user-service',
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

logger = logging.getLogger('user-service')

app = FastAPI()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post('/users/register')
async def register(user: UserRegister):
    # Registration logic (e.g., save to database)
    logger.info('User registration attempted', extra={'request_data': user.dict()})
    return {'status': 'success', 'message': 'User registered successfully'}

@app.post('/users/login')
async def login(user: UserLogin):
    # Authentication logic
    logger.info('User login attempted', extra={'request_data': user.dict()})
    return {'status': 'success', 'message': 'User logged in successfully'}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
