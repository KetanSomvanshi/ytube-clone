# YTube Clone

Simple python app to sync youtube videos meta data to a local database.

## Running the application
Complete application is dockerized and docker-compose can be used to run the application.
To handle environment variables config/.env file needs to be created. config/env.sample provided for reference.
If you create config/.env file by copying config/env.sample, you just need to update api_key
```bash
cd docker && docker compose up
```

## Features implemented 
1. Async fetch of recent youtube videos meta through celery workers and celery scheduler
2. Paginated GET API to get videos metadata
3. Search across title and description fields using postgres ts_vector, ts_query, and GIN indexing. Partial matching also works with this approach(bonus feature).
4. Admin APIs to add or delete google API keys when the quota is over. If multiple keys are provided randomly any key would be used per request. If no key is provided default key will be used. - Bonus feature.

[API Documentation](https://documenter.getpostman.com/view/15455073/2s935uGLgU)
PS : All apis are protected by basic authentication. Username and password can be configured in config/.env file.

## Design Components
### Celery Scheduler and Worker
celery scheduler is used to periodically schedule the sync. Sync frequency is configurable through env variables. Single instance of Scheduler is sufficient for application and workers can be horizontally scaled.
### Redis and Task queue
Redis is used as a key-value storage db as well as an async task queue for celery. db0 is used for queue and db1 for key-value storage.
### Postgres DB
Postgres DB is holding YTVideoMeta data in a table. Postgres DB can be sharded based on published_at timestamps and horizontally scaled.
Plain text search is also implemented over postgres DB using a combination of ts_vector,ts_query, and GIN indexing. However for better performance ElasticSearch like search db can be used.

## Design Diagram
![Screenshot 2023-02-12 at 22 53 15](https://user-images.githubusercontent.com/81796188/218327606-ce6a6e60-78f8-46f1-af04-29ddcf949013.png)
