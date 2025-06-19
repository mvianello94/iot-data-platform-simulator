# IoT Data Platform Simulator 🚀📡

This project simulates a scalable IoT data platform for real-time streaming analytics. It includes:

- A Python-based generator of synthetic IoT sensor data
- Apache Kafka for Data Ingestion
- Apache Spark Structured Streaming and Python for processing
- Apache Iceberg on MinIO as the Data Lake
- OpenSearch for indexing and search
- Grafana for data visualization
- Optional: Apache Flink for real-time alerting and advanced stream processing

Everything is orchestrated using Docker Compose to be easily run locally while reflecting a cloud-native architecture.

---

## 🧭 Cloud-Ready Architecture Mapping

This local setup emulates a cloud-native deployment, with swappable components for cloud-managed equivalents.

### Local ↔ Cloud Service Mapping

| Category          | Local (Docker)             | Cloud-Ready Equivalent                        |
| ----------------- | -------------------------- | --------------------------------------------- |
| Data Catalog      | Nessie (REST API)          | AWS Glue / Lake Formation                     |
| Object Storage    | MinIO                      | Amazon S3 / Google Cloud Storage / Azure Blob |
| Batch Processing  | Apache Spark               | EMR / Dataproc / Azure Synapse                |
| Stream Processing | Apache Flink (optional)    | Flink on Kinesis / Dataflow / Event Hubs      |
| Messaging         | Apache Kafka               | MSK / PubSub / Azure Event Hubs               |
| Data Lake Format  | Apache Iceberg             | Iceberg on S3/Blob with Glue/Hive             |
| Search & Indexing | OpenSearch                 | OpenSearch / Elasticsearch                    |
| SQL Engine        | Spark SQL / Trino / DuckDB | Athena / BigQuery / Synapse SQL               |
| BI & Dashboards   | Grafana                    | QuickSight / Looker / Power BI                |

---

## 📁 Project Structure

```plaintext
iot-data-platform-simulator/
│
├── docker-compose.yml
├── Makefile
│
├── iot-data-generator/          # IoT data generator (Python)
│   ├── generator.py             # Sends random JSON to Kafka
│   └── Dockerfile
│
├── spark-stream-processor/      # Spark Structured Streaming jobs
│   ├── ingest_transform.py      # From Kafka 'iot-telemetry' to 'iot-transformed'
│   ├── to_iceberg.py            # From 'iot-transformed' to Iceberg
│   ├── to_opensearch.py         # From 'iot-transformed' to OpenSearch
│   └── Dockerfile
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/mvianello94/iot-data-platform-simulator.git
cd iot-data-platform-simulator
```

### 2. Build

```bash
make build
```

### 3. Launch

```bash
make up
```

### 4. SignIn into Grafana

[http://localhost:3000](http://localhost:3000)
Username: admin
Password: admin

### 5. Visualize and analyze IoT data

Compare different datasources on pre-built dashboards:

- IoT Data (Iceberg DataSource)
- IoT Data (OpenSearch DataSource)

### 5. Clean

```bash
make clean
```

---

## 🌐 Access Services

| Service        | URL                                              | Username / Password         |
| -------------- | ------------------------------------------------ | --------------------------- |
| **MinIO**      | [http://localhost:9001](http://localhost:9001)   | `minioadmin` / `minioadmin` |
| **OpenSearch** | [http://localhost:5601](http://localhost:5601)   | `admin` / `admin`           |
| **Grafana**    | [http://localhost:3000](http://localhost:3000)   | `admin` / `admin`           |
| **Nessie UI**  | [http://localhost:19120](http://localhost:19120) | N/A                         |

---

## 🛠️ Makefile Commands

| Command                             | Description                                  |
| ----------------------------------- | -------------------------------------------- |
| `make up`                           | Start all services                           |
| `make up SERVICE=service_name`      | Start the specified service                  |
| `make down`                         | Stop all running containers                  |
| `make down SERVICE=service_name`    | Stop the specified service                   |
| `make build`                        | Build/rebuild all services                   |
| `make build SERVICE=service_name`   | Build/rebuild the specified service          |
| `make rebuild`                      | Rebuild and start all services               |
| `make rebuild SERVICE=service_name` | Rebuild and start the specified service      |
| `make logs`                         | Tail logs from all services                  |
| `make logs SERVICE=service_name`    | Tail logs from the specified service         |
| `make restart`                      | Restart the environment                      |
| `make clean`                        | Stop everything and remove volumes + orphans |

📌 **Note**: `make clean` will **delete all volumes**, including MinIO data.

---

## ⚙️ Technical Overview

### Kafka

- Topics:

  - `iot-raw-telemetry` (raw events)
  - `iot-processed-telemetry` (transformed events)

- RAW Data Format: JSON with fields like:

```json
{
  "device_id": "test",
  "temperature": 21,
  "humidity": 80,
  "timestamp": "...",
  ...
}
```

- Processed Data Format: JSON with fixed fields:

```json
{
  "device_id": "test",
  "event_time": "...",
  "variable_id": "temperature",
  "string_val": "21",
  "double_val": 21.0
}
```

### Kafka Consumers

Three separate Kafka consumers:

1. `spark-stream-processor`: Spark Job reads from `iot-raw-telemetry`, transforms events, writes to `iot-processed-telemetry` (using Spark Structured Streaming)
2. `spark-to-iceberg-processor`: Spark Job reads from `iot-processed-telemetry`, writes to Iceberg on `s3a://iot-data/warehouse` (using Spark Structured Streaming)
3. `iot-data-to-opensearch`: Simple Python script reads from `iot-processed-telemetry`, indexes into OpenSearch

Checkpointing is used in all jobs for fault tolerance.

### MinIO

Acts as the local S3-compatible data lake

- Bucket: `iot-data`
- API: `http://localhost:9000`
- UI: `http://localhost:9001`
- Default user: `minioadmin` / `minioadmin`

### Nessie (REST API)

Catalog API: enables branching, versioning, rollback for Iceberg tables

### OpenSearch

Used for real-time indexing and full-text queries

### Grafana

- Connected to Trino for querying Iceberg tables
- Also visualizes OpenSearch data
- Dashboards configurable to explore sensor trends

---

## 📜 License

MIT License — use it, fork it, break it, improve it.

---

## 👨‍💻 Author

**Manuel Vianello**
Software Engineer • Cloud Architect • Creative Problem Solver
[GitHub](https://github.com/mvianello94) — [LinkedIn](https://linkedin.com/in/manuel-vianello-339626155)
