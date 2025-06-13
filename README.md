# IoT Data Platform Simulator 🚀📡

This project simulates a scalable IoT data platform for real-time streaming analytics. It features a Python-based data generator producing synthetic IoT sensor data, ingested via Apache Kafka and processed using Apache Spark Structured Streaming. The processed data is stored in Apache Iceberg format on an S3-compatible MinIO bucket and explored via Apache Superset. Additionally, Apache Flink is included for potential use in real-time alerting and advanced stream processing scenarios. All components are containerized using Docker Compose, making the platform easy to run, extend, and experiment with.

<br>

## Cloud-Ready Architecture Mapping

This setup demonstrates a portable, modular data platform built with Apache Spark, Apache Flink, Kafka, Iceberg, and Nessie. It is designed to run locally via Docker, but structured in a way that mirrors a cloud-native architecture.

### Local-to-Cloud Service Mapping

| Component             | Local / Dev (Docker)           | Cloud-Ready Equivalent                        |
| --------------------- | ------------------------------ | --------------------------------------------- |
| **Data Catalog**      | Hadoop Catalog                 | AWS Glue / Lake Formation                     |
| **Object Storage**    | MinIO                          | Amazon S3 / Google Cloud Storage / Azure Blob |
| **Batch Processing**  | Apache Spark (Docker)          | AWS EMR / Google Dataproc / Azure Synapse     |
| **Stream Processing** | Apache Flink (Docker, PyFlink) | Flink on Kinesis / Dataflow / Event Hubs      |
| **Messaging**         | Apache Kafka (Docker)          | MSK / PubSub / Azure Event Hubs               |
| **SQL Engine**        | Spark SQL / DuckDB             | Athena / BigQuery / Synapse SQL               |
| **BI / Dashboards**   | Apache Superset                | AWS QuickSight / Looker / Power BI            |

### Why This Matters

By structuring the platform with these components and clear modular boundaries, we demonstrate that:

- **The platform is cloud-agnostic**: it runs anywhere, changes only the underlying services.
- **Code and pipeline logic are reusable** between local/dev and production environments.
- **Real-world data ops features** (e.g., data versioning, branching, rollback) are built-in via Iceberg + Nessie.

<br>

## Project Structure

```graphql
iot-data-platform-simulator/
│
├── docker-compose.yml
│
├── devices-simulator/        # IoT event generator
│   ├── generator.py          # Sends random JSON telemetry to Kafka
│   └── Dockerfile
│
├── spark-stream-processor/   # Spark Structured Streaming job
│   ├── main.py               # Reads from Kafka, writes to Delta Lake
│   └── Dockerfile
```

<br>

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/iot-data-platform-simulator.git
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

### 4. Access the services

MinIO Console: http://localhost:9001
User: minioadmin | Password: minioadmin

Superset UI: http://localhost:8088
User: admin | Password: admin123!

<br>

## Makefile Commands

This project includes a `Makefile` to simplify common Docker Compose tasks.

### Available Commands

| Command                          | Description                                       |
| -------------------------------- | ------------------------------------------------- |
| `make up`                        | Start all services in detached mode               |
| `make down`                      | Stop all running containers                       |
| `make build`                     | Build/rebuild all services                        |
| `make rebuild`                   | Rebuild and start all services + (`build` + `up`) |
| `make logs`                      | Tail logs from all services                       |
| `make logs SERVICE=service_name` | Tail logs from the specified service              |
| `make restart`                   | Restart the environment (`down` + `up`)           |
| `make clean`                     | Stop everything and remove volumes + orphans      |

### Typical Workflow

```bash
make build      # Build containers (only needed after code changes)
make up         # Start the environment
make logs       # See what’s happening
make clean      # Tear down everything and clean volumes
```

### Good to Know

- `make clean` will **delete all volumes**, including MinIO data.
- `make restart` is useful for a quick refresh without losing volumes.
- The `Makefile` assumes Docker Compose v2 (`docker compose`, not `docker-compose`).

<br>

## Technical Details

### Kafka

Topic: iot-telemetry

Message format: JSON with device_id, temperature, humidity, ..., timestamp

### Spark Structured Streaming

Consumes Kafka topic as a stream

Parses JSON messages using schema

Writes data to Apache Iceberg Table s3a://iot-data/telemetry

Uses checkpointing for fault tolerance

### MinIO

S3-compatible object store used as a local data lake:

Bucket: iot-data

- API Endpoint: http://localhost:9000
- UI: http://localhost:9001

For development purpose use the default admin user:
Username: minioadmin
Password: minioadmin

### Apache Superset

- UI: http://localhost:8088

For development purpose use the default admin user created using `docker-compose.yml`:
Username: admin
Password: admin123!

<br>

## License

MIT License — use it, fork it, break it, improve it.

<br>

## Author

Manuel Vianello – Cloud Architect, Software Engineer, creative problem solver.
