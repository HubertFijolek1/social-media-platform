# Architecture Notes

## Overview

The platform consists of multiple microservices, each responsible for a specific domain:

### Microservices

1. **User Service**
   - **Responsibilities**: User registration, authentication, profile management.
   - **Technologies**: FastAPI, PostgreSQL (sharded by user ID).
   - **Endpoints**:
     - `POST /users/register`
     - `POST /users/login`
     - `GET /users/{user_id}`

2. **Tweet Service**
   - **Responsibilities**: Creating, deleting, and retrieving tweets.
   - **Technologies**: FastAPI, PostgreSQL (sharded by tweet ID), Kafka.
   - **Endpoints**:
     - `POST /tweets/`
     - `GET /tweets/{tweet_id}`
     - `DELETE /tweets/{tweet_id}`

3. **Timeline Service**
   - **Responsibilities**: Generating user timelines using a hybrid fanout strategy.
   - **Technologies**: FastAPI, Redis, Kafka.
   - **Endpoints**:
     - `GET /timelines/{user_id}`

4. **Notification Service**
   - **Responsibilities**: Managing notifications for likes, retweets, follows.
   - **Technologies**: FastAPI, Redis, WebSockets.
   - **Endpoints**:
     - `GET /notifications/{user_id}`

5. **Follower Service**
   - **Responsibilities**: Managing follow/unfollow actions.
   - **Technologies**: FastAPI, PostgreSQL.
   - **Endpoints**:
     - `POST /follow/`
     - `POST /unfollow/`
     - `GET /followers/{user_id}`
     - `GET /following/{user_id}`

6. **Search Service**
   - **Responsibilities**: Providing search functionality using ElasticSearch.
   - **Technologies**: FastAPI, ElasticSearch.
   - **Endpoints**:
     - `GET /search/`

7. **Direct Messaging Service**
   - **Responsibilities**: Handling private messages between users.
   - **Technologies**: FastAPI, WebSockets, PostgreSQL.
   - **Endpoints**:
     - `POST /messages/`
     - `GET /messages/{conversation_id}`

## Communication Patterns

- **Synchronous**: RESTful APIs between services for critical operations.
- **Asynchronous**: Kafka for event-driven communication (e.g., new tweet events).

## Data Flow

- **User Registration**:
  - User Service handles registration and stores user data.
- **Tweet Creation**:
  - Tweet Service handles creation, publishes event to Kafka.
  - Timeline Service consumes event, updates timelines.
- **Timeline Retrieval**:
  - Timeline Service retrieves timeline from Redis or regenerates if necessary.
- **Notifications**:
  - Notification Service listens to events and updates users via WebSockets.

## Technologies

- **FastAPI**: High-performance web framework for Python.
- **Nginx**: Serves as a reverse proxy, load balancer, and API gateway.
- **Kafka**: Message broker for asynchronous communication.
- **Redis**: In-memory data store for caching.
- **PostgreSQL**: Relational database with sharding for scalability.
- **ElasticSearch**: Full-text search engine.
- **ELK Stack**: Centralized logging and monitoring.
- **Apache Spark**: Real-time data processing for analytics.
- **Docker & Kubernetes**: Containerization and orchestration.
- **WebSockets**: Real-time communication for notifications and messaging.

## Deployment Strategy

- **Docker Compose**: For local development and testing.
- **Kubernetes**: For production deployment, ensuring scalability and high availability.

## Security Considerations

- **Authentication**: JWT tokens for secure API access.
- **API Gateway**: Nginx enforces authentication and rate limiting.
- **Data Encryption**: SSL/TLS for data in transit.

## Monitoring and Logging

- **ELK Stack**: Collects and visualizes logs from all services.
- **Metrics**: Prometheus and Grafana (planned) for system metrics.

## Future Enhancements

- Implementing Prometheus and Grafana for monitoring.
- Adding CI/CD pipelines.
- Implementing more robust error handling and retries.
