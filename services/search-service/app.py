import logging
import json
import sys
from fastapi import FastAPI, Query
import uvicorn
from elasticsearch import Elasticsearch

# Configure logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'service': 'search-service',
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

logger = logging.getLogger('search-service')

app = FastAPI()

# Connect to Elasticsearch
es = Elasticsearch(hosts=["elasticsearch:9200"])

@app.get('/search/')
async def search(q: str = Query(..., min_length=1), index: str = 'tweets'):
    logger.info('Search query received', extra={'query': q, 'index': index})
    try:
        response = es.search(
            index=index,
            body={
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["content", "username"]
                    }
                }
            }
        )
        results = [hit['_source'] for hit in response['hits']['hits']]
        return {'results': results}
    except Exception as e:
        logger.error(f'Error executing search: {e}')
        return {'error': str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
