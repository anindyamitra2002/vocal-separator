FROM python:3.9

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg, git)
USER root
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy requirements and install Python dependencies
COPY --chown=user:user requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user -U demucs

# Copy app code
COPY --chown=user:user . .

EXPOSE 8000

CMD ["python", "server.py"]   