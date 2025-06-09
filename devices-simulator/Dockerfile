FROM python:3.13-slim

USER root

WORKDIR /app

# Copy the app code
COPY . .

# Add execution permission to entrypoint
RUN chmod +x /app/entrypoint.sh

# Copy requirements and install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]
