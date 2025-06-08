# IoT Data Platform Simulator 🚀📡

This project simulates a scalable IoT data platform for real-time streaming analytics. It features a Python-based data generator producing synthetic IoT sensor data, ingested via Apache Kafka and processed using Apache Spark Structured Streaming. The processed data is stored in a Delta Lake format on an S3-compatible MinIO bucket. All components are containerized with Docker Compose to be easy to run, extend, and experiment with.

Main stack:

- **Kafka** for event streaming
- **Apache Spark Structured Streaming** for data processing
- **MinIO** as an S3-compatible data lake with Delta Lake
- **Python** everywhere for simplicity and flexibility

---

<br>

## Architecture

1. IoT Simulator (Python)
1. Kafka
1. Spark Job (Spark Structured Streaming)
1. Delta Lake (MinIO, compatible with Amazon S3)

---

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

---

<br>

## Project Structure

```graphql
iot-data-platform-simulator/
│
├── docker-compose.yml
│
├── simulator/                # IoT event generator
│   ├── generator.py          # Sends random JSON events to Kafka
│   └── Dockerfile
│
├── spark-app/                # Spark Structured Streaming job
│   ├── main.py               # Reads from Kafka, writes to Delta Lake
│   └── Dockerfile
```

---

<br>

## Makefile Commands

This project includes a `Makefile` to simplify common Docker Compose tasks.

### Available Commands

| Command        | Description                                  |
| -------------- | -------------------------------------------- |
| `make up`      | Start all services in detached mode          |
| `make down`    | Stop all running containers                  |
| `make build`   | Build/rebuild all services                   |
| `make logs`    | Tail logs from all services                  |
| `make restart` | Restart the environment (`down` + `up`)      |
| `make clean`   | Stop everything and remove volumes + orphans |

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

---

<br>

## Technical Details

### Kafka

Topic: iot-events

Message format: JSON with device_id, temperature, humidity, timestamp

### Spark Structured Streaming

Consumes Kafka topic as a stream

Parses JSON messages using schema

Writes Delta Lake tables to s3a://iot-data/events

Uses checkpointing for fault tolerance

### MinIO

S3-compatible object store used as a local data lake:

Bucket: iot-data

Endpoint: http://localhost:9000

---

<br>

## Live test

1. Open MinIO and create a bucket named iot-data

1. Run everything: docker compose up

1. View simulator logs:

```bash
docker compose logs -f simulator
```

1. Check what Spark is writing to Delta:

```bash
docker exec -it spark-job bash
spark-sql -e "SELECT * FROM delta.`s3a://iot-data/events` LIMIT 10"
```

---

<br>

## License

MIT License — use it, fork it, break it, improve it.

---

<br>

## 👨Author

Manuel Vianello – Cloud Architect, Software Engineer, creative problem solver.
