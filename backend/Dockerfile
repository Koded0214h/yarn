FROM python:3.11-slim

# Install system audio and build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    libasound2 \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir livekit-agents livekit-plugins-silero livekit-plugins-spitch livekit-plugins-google

# Copy the rest of the application
COPY . .

# Run the voice agent in production mode
CMD ["python", "voice_agent.py", "start"]
