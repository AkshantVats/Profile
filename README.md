# Akshant Sharma

Staff Engineer. I build high-throughput distributed systems and the infrastructure layer that sits underneath product features — ingestion engines, storage primitives, real-time event pipelines.

Currently building [`infra-ai-streaming`](https://github.com/AkshantVats/infra-ai-streaming) — an AI inference observability platform in Rust.

---

## What I'm Building

**[infra-ai-streaming](https://github.com/AkshantVats/infra-ai-streaming)** `in progress`

An open-source AI inference observability pipeline built for the event volume and metric cardinality that standard monitoring tools break under.

```
Rust ingestion engine → Kafka → Go consumer → ClickHouse → Grafana
```

- Axum HTTP server with channel-based backpressure and per-tenant rate limiting
- Circuit breaker with Redis overflow buffer and Dead Letter Queue
- Z-score anomaly detection on inference latency per model
- Helm charts with HPA scaling on Kafka consumer lag
- Target: 1M events/min, sub-100ms ingestion P99

---

## Technical Bets

Things I'm doubling down on:

- **Rust** for systems programming where performance guarantees are non-negotiable
- **AI infrastructure** — inference pipelines, LLM observability, cost optimization at the API layer
- **Kafka internals at scale** — partition strategy, consumer group design, backpressure mechanisms
- **ClickHouse** for analytical workloads over high-cardinality event streams
- **Kubernetes** — operators, eBPF-based observability, cost-aware autoscaling

---

## By the Numbers

| Scale | System | Stack |
|---|---|---|
| 1.5T events / day | Time-series database @ Agoda | Rust · Scala · Ceph |
| 7M+ unique sensors | SmartBuildings IoT platform @ Walmart | Azure IoT Hub · Stream Analytics |
| 5,000 geo-events / sec | End-to-end rider tracking @ Delivery Hero | OSRM · AWS EKS · Kinesis |
| 250k+ SKU updates / supplier | Global Pricing Engine @ Wayfair | GCP · Kafka · BigQuery |
| 1M+ daily orders | Logistics platform @ Delivery Hero | AWS EKS · SQS · Kinesis |

---

## Stack

```
Languages    Rust · Go · Java · Scala · Python
Streaming    Kafka · Redpanda · AWS Kinesis · Azure Event Hub
Storage      Ceph · ClickHouse · Redis · BigQuery · PostgreSQL · MongoDB
Infra        Kubernetes · Terraform · Helm · Docker
Cloud        GCP · AWS · Azure
Observability  OpenTelemetry · Prometheus · Grafana · ELK
```

---

## Writing

Technical posts on distributed systems, AI infrastructure, and the gap between the two.

→ [LinkedIn](https://linkedin.com/in/akshantsharma07)

---

## Elsewhere

- LinkedIn — [akshantsharma07](https://linkedin.com/in/akshantsharma07)
- Email — akshant3@gmail.com