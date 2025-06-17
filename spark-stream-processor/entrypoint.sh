#!/bin/bash

SPARK_VERSION="${SPARK_VERSION:-3.5.1}"
SPARK_VERSION_SHORT=$(echo "$SPARK_VERSION" | cut -d '.' -f1,2)
SCALA_VERSION="${SCALA_VERSION:-2.12}"

echo "🚀 Starting Spark job with:"
echo "    Spark version: ${SPARK_VERSION}"
echo "    Scala version: ${SCALA_VERSION}"

spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_${SCALA_VERSION}:${SPARK_VERSION} \
  --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
  /app/code/main.py



