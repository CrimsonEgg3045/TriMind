# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Render maps this automatically or sets PORT env var)
EXPOSE 8000

# Command to run the application
# We bind to 0.0.0.0 and use the PORT environment variable if available, fallback to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
