# UTGenerator

## Distributed Celery Workers with Docker Swarm

This guide explains how to set up Docker Swarm to distribute Celery workers across multiple machines for the UTGenerator project.

### Prerequisites

- Docker installed on all machines
- Machines can communicate with each other over the network
- One machine designated as the Swarm manager

### Setup Docker Swarm

1. Initialize the Swarm on the manager node:

   ```bash
   docker swarm init --advertise-addr <MANAGER-IP>
   ```

   This command will output a token for worker nodes to join the swarm.

2. Join worker nodes to the swarm:

   On each worker machine, run the command provided by the swarm init output:

   ```bash
   docker swarm join --token <TOKEN> <MANAGER-IP>:2377
   ```

3. Verify the swarm:

   On the manager node, run:

   ```bash
   docker node ls
   ```

   This should list all nodes in the swarm.

### Create an Overlay Network

Create a network for your services to communicate:

```bash
docker network create --driver overlay utgenerator-network
```

### Deploy the Stack

1. Ensure your `docker-compose.yml` file is set up for swarm mode. Here's an example:

   ```yaml
   version: '3.8'

   services:
     frontend:
       image: utgenerator/frontend:latest
       ports:
         - "80:80"
       networks:
         - utgenerator-network
       deploy:
         replicas: 1
         placement:
           constraints: [node.role == manager]

     flask_app:
       image: utgenerator/flask_app:latest
       ports:
         - "5000:5000"
       env_file:
         - .env
       volumes:
         - ${MODEL_PATH}:/app/models
         - ${UPLOAD_FOLDER}:/app/uploads
         - ${DOWNLOAD_FOLDER}:/app/downloads
       networks:
         - utgenerator-network
       deploy:
         replicas: 1
         placement:
           constraints: [node.role == manager]

     celery_worker:
       image: utgenerator/celery_worker:latest
       command: python celery_worker.py
       env_file:
         - .env
       volumes:
         - ${MODEL_PATH}:/app/models
         - ${UPLOAD_FOLDER}:/app/uploads
         - ${DOWNLOAD_FOLDER}:/app/downloads
       networks:
         - utgenerator-network
       deploy:
         replicas: 3
         placement:
           max_replicas_per_node: 1

     redis:
       image: "redis:latest"
       command: redis-server --appendonly yes
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
       networks:
         - utgenerator-network
       deploy:
         replicas: 1
         placement:
           constraints: [node.role == manager]

   volumes:
     redis_data:

   networks:
     utgenerator-network:
       external: true
   ```

2. Deploy the stack:

   On the manager node, run:

   ```bash
   docker stack deploy -c docker-compose.yml utgenerator
   ```

3. Verify the deployment:

   ```bash
   docker service ls
   ```

   This will show all services and their replica counts.

### Scaling Celery Workers

To scale the number of Celery workers:

```bash
docker service scale utgenerator_celery_worker=5
```

his scales the celery_worker service to 5 replicas across the swarm.

### Monitoring

Monitor the swarm and services:
```bash
docker service ps utgenerator_celery_worker
```

This shows the status of each Celery worker replica.

### Considerations

- Ensure all nodes have access to necessary volumes (MODEL_PATH, UPLOAD_FOLDER, DOWNLOAD_FOLDER).
- For production, consider using a managed Redis service or a Redis cluster for better reliability.
- Adjust placement constraints and replica counts based on your specific needs and machine capabilities.

### Troubleshooting

- If services fail to start, check logs:

```bash
docker service logs utgenerator_celery_worker
```

- Ensure all environment variables are correctly set in the .env file on the manager node.

By following this guide, you should be able to set up a distributed Celery worker system using Docker Swarm for the UTGenerator project.