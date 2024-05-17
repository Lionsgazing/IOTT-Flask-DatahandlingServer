# syntax = docker/dockerfile:1.4
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /server

# Copy only the requirements file to install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Define the command to run your app (you could use CMD here as well)
ENTRYPOINT ["python3"]
CMD ["server.py"]

EXPOSE 8085
