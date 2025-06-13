#!/bin/bash

SPARK_VERSION="${SPARK_VERSION:-3.5.1}"
SPARK_VERSION_SHORT=$(echo "$SPARK_VERSION" | cut -d '.' -f1,2)
SCALA_VERSION="${SCALA_VERSION:-2.12}"
ICEBERG_VERSION="${ICEBERG_VERSION:-1.4.3}"
NESSIE_VERSION="${NESSIE_VERSION:-0.104.1}"

echo "🚀 Starting Spark job with:"
echo "    Spark version: ${SPARK_VERSION}"
echo "    Scala version: ${SCALA_VERSION}"
echo "    Iceberg version: ${ICEBERG_VERSION}"
echo "    Nessie version: ${NESSIE_VERSION}"

spark-submit \
  --packages org.apache.iceberg:iceberg-spark-runtime-${SPARK_VERSION_SHORT}_${SCALA_VERSION}:${ICEBERG_VERSION},org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION},org.projectnessie.nessie-integrations:nessie-spark-extensions-${SPARK_VERSION_SHORT}_${SCALA_VERSION}:${NESSIE_VERSION} \
  --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
  --conf spark.hadoop.fs.s3a.connection.timeout=60000 \
  /app/code/main.py

