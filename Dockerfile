# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Install Ollama
RUN apt-get update && apt-get install -y curl
RUN curl https://ollama.ai/install.sh | sh

# Install supervisord
RUN apt-get install -y supervisor

# Start Ollama in the background and pull the required model
RUN /usr/local/bin/ollama start & sleep 5 && /usr/local/bin/ollama pull nomic-embed-text

# Copy application code
COPY . /app/

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the port the app runs on
EXPOSE 8080

# Command to run supervisord
CMD ["/usr/bin/supervisord"]