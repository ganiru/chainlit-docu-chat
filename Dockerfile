# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.12.3

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install Ollama
# RUN apt-get update && apt-get install -y curl
# RUN curl https://ollama.ai/install.sh | sh

# Install supervisord
# RUN apt-get install -y supervisor

# Start Ollama in the background and pull the required model
# RUN /usr/local/bin/ollama start & sleep 5 && /usr/local/bin/ollama pull nomic-embed-text
# Copy supervisord configuration
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the port the app runs on
# EXPOSE 8080

# Command to run supervisord
# CMD ["/usr/bin/supervisord"]
CMD python -m chainlit run app.py -h --host 0.0.0.0 --port ${PORT}