#!/bin/bash

# Stop any running containers
echo "Stopping any existing containers..."
docker compose down

# Build the Docker containers
echo "Building containers..."
docker compose build

# Start containers in detached mode
echo "Starting containers..."
docker compose up -d db web frontend

# Wait for the database container to initialize (optional but recommended)
echo "Waiting for database to start..."
sleep 10  # Adjust the time if needed

# Run Django makemigrations
echo "Running makemigrations..."
docker compose exec web python manage.py makemigrations

# Run Django migrations
echo "Running migrations..."
docker compose exec web python manage.py migrate

# Collect static files (if applicable)
echo "Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

# Optionally create a superuser (only if required)
# Uncomment and adjust if you'd like an automated superuser creation
# docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Show logs
echo "Starting logs for web and frontend services..."
docker compose logs -f web frontend