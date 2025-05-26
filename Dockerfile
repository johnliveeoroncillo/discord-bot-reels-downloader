# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for downloads
RUN mkdir -p /app/downloads

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run bot.py when the container launches
CMD ["python", "bot.py"]
