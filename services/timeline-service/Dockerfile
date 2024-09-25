FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app.py .
COPY filebeat.yml /etc/filebeat/filebeat.yml

# Install Filebeat
RUN curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.9.2-linux-x86_64.tar.gz && \
    tar xzvf filebeat-7.9.2-linux-x86_64.tar.gz && \
    mv filebeat-7.9.2-linux-x86_64/filebeat /usr/local/bin/

# Expose port
EXPOSE 8000

# Start the application and Filebeat
CMD ["sh", "-c", "filebeat -e & python app.py"]
