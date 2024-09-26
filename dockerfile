# Dockerfile
# Base image using Python 3.10 or higher (or preferred version)
# Python 3.10+ required for DJango 5.1.1
FROM python:3.12-slim

# Set environment variables to prevent buffering and enable virtual environment usage
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the app directory and set it as working directory
WORKDIR /app

# Install dependencies for LibPostal
RUN apt-get update && apt-get install -y \
    libpostal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make sure it's installed correctly
RUN ldconfig

# Copy requirements.txt to the container and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project to the container
COPY . /app/

# Open the correct port for the Django app
EXPOSE 8000

# Run the Django development server (adjust to production server for deployment)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]