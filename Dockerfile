# Use the official Python 3.10 slim image as a base image
FROM python:3.10-slim

# Set environment variables for better build caching
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUF 1

WORKDIR /app

# Copy only the requirements.txt file first
COPY requirements.txt /app/

# Install Python dependencies if requirements.txt has changed
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . /app

# Build the package
RUN python setup.py sdist bdist_wheel
RUN pip install --no-cache-dir .

# Expose the application port 
EXPOSE 8000

# Define data directory and default node type
ENV DATA_DIR=/data
ENV NODETYPE=admin
ENV QDRANT_HOST=http://localhost:6333

# Command to run the applicatio
CMD ["python", "main.py", "--data-dir", "$DATA_DIR", "--nodetype", "$NODETYPE"]
