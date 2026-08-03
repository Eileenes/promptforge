FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 8777

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8777"]
