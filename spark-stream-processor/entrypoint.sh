#!/bin/bash

# Versioni configurabili con default
DELTA_VERSION="${DELTA_VERSION:-3.3.2}"
SPARK_VERSION="${SPARK_VERSION:-3.5.6}"
SCALA_VERSION="2.12"

echo "🚀 Starting Spark job with:"
echo "    Delta Lake version: ${DELTA_VERSION}"
echo "    Spark version: ${SPARK_VERSION}"
echo "    Scala version: ${SCALA_VERSION}"

spark-submit \
  --packages io.delta:delta-spark_${SCALA_VERSION}:${DELTA_VERSION},org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION} \
  --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
  --conf spark.hadoop.fs.s3a.connection.timeout=60000 \
   --conf spark.delta.logRetentionDuration=86400000 \
  /app/code/main.py
  # --conf spark.hadoop.fs.s3a.connection.timeout=60000 \
