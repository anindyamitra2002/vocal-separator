FROM python:3.10

# Install system dependencies (ffmpeg, git, sudo)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --user -U demucs

# Copy app code
COPY . .

EXPOSE 8000

CMD ["python", "server.py"]   