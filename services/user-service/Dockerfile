FROM python:3.9-slim

# Install required packages
RUN apt-get update && apt-get install -y curl

# Set working directory
WORKDIR /app

# Copy application code
COPY app.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download and install Filebeat
RUN curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.9.2-linux-x86_64.tar.gz && \
    tar xzvf filebeat-7.9.2-linux-x86_64.tar.gz && \
    mv filebeat-7.9.2-linux-x86_64/filebeat /usr/local/bin/ && \
    rm -rf filebeat-7.9.2-linux-x86_64*

# Copy Filebeat configuration
COPY filebeat.yml /usr/local/etc/filebeat.yml

# Expose application port
EXPOSE 8000

# Set the entrypoint to run Filebeat and the application
CMD ["sh", "-c", "python app.py | filebeat -e -c /usr/local/etc/filebeat.yml"]

