# Use a lightweight Python 3.11 image based on Alpine Linux
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file to the working directory
COPY requirements.txt /app

# Install Python dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# Copy the application source code into the container
COPY booking/ /app/

# Run the Python application when the container starts
CMD ["python", "-u", "booking.py"]