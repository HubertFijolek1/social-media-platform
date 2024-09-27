import logging
import json
import sys
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import redis

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'follower-service',
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

logger = logging.getLogger('follower-service')

app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Pydantic models
class FollowAction(BaseModel):
    follower_id: str
    followee_id: str

@app.post('/followers/follow')
async def follow(action: FollowAction):
    # Add follow relationship
    redis_client.sadd(f'following:{action.follower_id}', action.followee_id)
    redis_client.sadd(f'followers:{action.followee_id}', action.follower_id)
    logger.info('User followed another user', extra={'action': action.dict()})
    return {'status': 'success', 'message': f'{action.follower_id} is now following {action.followee_id}'}

@app.post('/followers/unfollow')
async def unfollow(action: FollowAction):
    # Remove follow relationship
    redis_client.srem(f'following:{action.follower_id}', action.followee_id)
    redis_client.srem(f'followers:{action.followee_id}', action.follower_id)
    logger.info('User unfollowed another user', extra={'action': action.dict()})
    return {'status': 'success', 'message': f'{action.follower_id} has unfollowed {action.followee_id}'}

@app.get('/followers/{user_id}')
async def get_followers(user_id: str):
    followers = redis_client.smembers(f'followers:{user_id}')
    followers = [follower.decode('utf-8') for follower in followers]
    return {'user_id': user_id, 'followers': followers}

@app.get('/following/{user_id}')
async def get_following(user_id: str):
    following = redis_client.smembers(f'following:{user_id}')
    following = [followee.decode('utf-8') for followee in following]
    return {'user_id': user_id, 'following': following}

def get_followers_list(user_id):
    followers = redis_client.smembers(f'followers:{user_id}')
    return [follower.decode('utf-8') for follower in followers]

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
