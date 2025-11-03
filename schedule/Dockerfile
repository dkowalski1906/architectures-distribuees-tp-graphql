# Use a lightweight Python 3.11 image based on Alpine Linux
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file to the working directory
COPY requirements.txt /app

# Install Python dependencies listed in requirements.txt
RUN pip install -r requirements.txt

# grpc compilation of proto files or copy of generated files
COPY schedule/schedule_pb2.py schedule/schedule_pb2_grpc.py /app/

# Copy the rest of the service code into the container
COPY schedule/ /app/

# Run the Python gRPC server when the container starts
CMD ["python", "-u", "schedule.py"]