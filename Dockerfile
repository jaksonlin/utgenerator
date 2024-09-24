# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Create a shell script to act as an entrypoint
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'if [ "$CONTAINER_TYPE" = "celery" ]; then' >> /entrypoint.sh && \
    echo '    python celery_worker.py' >> /entrypoint.sh && \
    echo 'else' >> /entrypoint.sh && \
    echo '    flask run --host=0.0.0.0' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set the entrypoint script to be executed
ENTRYPOINT ["/entrypoint.sh"]