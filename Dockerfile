# Use an official Python runtime as a parent image
FROM python:3.12.3

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Command to run the app
CMD python -m chainlit run apppp.py