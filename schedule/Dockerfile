FROM python:3.11-slim

WORKDIR /app

# creates a user no-root called appuser
RUN adduser --disabled-password --gecos "" appuser || true

# copy the requirements file in the workdir
COPY requirements.txt /app/requirements.txt

# install the Python requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# copy the app files and directories
COPY . /app
RUN chown -R appuser:appuser /app

USER appuser

# environment variable to default (editable with "-e" during the execution)
ENV USE_DOCKER=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# run the application
CMD ["python", "schedule/schedule.py"]