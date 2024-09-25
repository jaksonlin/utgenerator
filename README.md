# UTGenerator

## build

```
    docker-compose build
    docker tag utgenerator_flask_app utgenerator/flask_app:latest
    docker tag utgenerator_celery_worker utgenerator/celery_worker:latest
    docker stack deploy -c docker-compose.yml utgenerator