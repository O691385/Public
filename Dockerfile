# 
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV NAME PMToolkit

# API Keys Needed
# OPENAI_API_KEY
# ANTHROPIC_API_KEY

# Run app.py when the container launches
CMD ["streamlit", "run", "chatprd.py", "--server.port=8501", "--server.address=0.0.0.0"]
