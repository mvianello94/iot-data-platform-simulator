FROM bitnami/spark:4.0.0

USER root
COPY main.py /app/main.py

ENV PYSPARK_PYTHON=python3

CMD ["/opt/bitnami/spark/bin/spark-submit", "/app/main.py"]
