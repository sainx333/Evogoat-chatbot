# Use a modern Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy all your code into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 7860 for Hugging Face
EXPOSE 7860

# Start both the FastAPI app and (optionally) Telegram bridge
CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 7860"]
