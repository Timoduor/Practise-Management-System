# Use an official Python image as a base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock to the working directory
COPY Pipfile Pipfile.lock /app/

# Install dependencies
RUN pipenv install --system --deploy

# Copy the entire project to the working directory
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Set the default command to start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
