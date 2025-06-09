#!/bin/bash

# spark-submit \
#   --packages io.delta:delta-spark_2.13:4.0.0,org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 \
#   --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
#   --conf "spark.executor.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
#   /app/main.py

spark-submit \
  --packages io.delta:delta-spark_2.13:4.0.0,org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 \
  --conf "spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp" \
  /app/main.py
  # --conf spark.hadoop.fs.s3a.connection.timeout=60000 \
