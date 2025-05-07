# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Install Poetry
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock files to the container
COPY uv.lock uv.lock

# Copy the rest of the application code into the container
COPY . .

# Install dependencies
RUN uv sync

# Specify the command to run on container start
CMD ["uv", "run", "python", "main.py"]