# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 (Koyeb defaults to this or custom port)
EXPOSE 8000

# Command to run the application
# We bind to 0.0.0.0 so Koyeb can route traffic to it
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
