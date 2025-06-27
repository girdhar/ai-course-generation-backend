# Use official Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app to the container
COPY . .

# Expose port (change if needed)
EXPOSE 8000

# Command to run your app (change as per your framework)
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
