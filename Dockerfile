# Use official Python 3.11 base image
FROM python:3.11

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    python3-dev \
    libatlas-base-dev \
    libboost-python-dev \
    libboost-system-dev \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . /app/

# Pre-install dlib-bin (binary wheel) before installing other Python dependencies
RUN pip install dlib-bin==19.24.6

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the main application
CMD ["python", "/app/face_detection.py"]
