# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.12.3

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install -r /app/requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Expose the port the app runs on
EXPOSE 8080

CMD python -m chainlit run app2.py -h --host 0.0.0.0 --port ${PORT}