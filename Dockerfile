# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start both FastAPI and Telegram bot in a single shell command
CMD bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & python bot/telegram_bot.py"
