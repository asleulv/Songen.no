# Use the official Python 3.11 image (slim version to keep it lightweight)
FROM python:3.11-slim

# Set environment variables so Python behaves well in Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the work directory inside the container
WORKDIR /code

# Install the system tools needed for MariaDB (the "kitchen" tools)
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements list and install them
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project code into the container
COPY . /code/