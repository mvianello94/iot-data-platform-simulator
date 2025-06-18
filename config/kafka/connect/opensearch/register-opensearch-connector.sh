#!/bin/bash
curl -X POST -H "Content-Type: application/json" --data @/tmp/opensearch-sink-config.json http://localhost:8083/connectors || true