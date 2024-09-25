FROM nginx:latest

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy SSL certificates - later
# COPY certs/ /etc/ssl/certs/
# COPY private/ /etc/ssl/private/

# Copy any additional files (e.g., .htpasswd for basic auth) - later
# COPY .htpasswd /etc/nginx/.htpasswd
