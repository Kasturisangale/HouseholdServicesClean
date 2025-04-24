# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Update the system packages to ensure latest security patches
RUN apt-get update && apt-get upgrade -y

# Set the working directory inside the container
WORKDIR /app

# Copy the backend folder to the container
COPY backend/ /app/backend/

RUN chmod -R 777 /app/backend/instance

# Install the required Python dependencies (from backend/requirements.txt)
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the frontend folder to the container (with already installed node_modules)
COPY frontend/ /app/frontend/

# Expose the port your app will run on (Flask typically uses 5000)
EXPOSE 5000

# Command to run the backend application (app.py is directly in backend, not in an 'app' folder)
CMD ["python", "/app/backend/app.py"]
