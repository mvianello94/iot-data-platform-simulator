FROM bitnami/spark:3.5.6

USER root

ENV IVY_CACHE_DIR=/opt/ivy-cache
RUN mkdir -p ${IVY_CACHE_DIR} && chmod -R 777 ${IVY_CACHE_DIR}

WORKDIR /app

# Copy the app code
COPY . .

# Add execution permission to entrypoint
RUN chmod +x /app/entrypoint.sh

# Copy requirements and install Python dependencies
# RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]
