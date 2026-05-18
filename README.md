# Akshant Sharma

Staff Engineer. I build high-throughput distributed systems and the infrastructure layer that sits underneath product features — ingestion engines, storage primitives, real-time event pipelines.

**Blog tooling:** `python scripts/html_to_linkedin_article.py <post.html>` — LinkedIn article export ([scripts/README.md](scripts/README.md)).

Currently building [`infra-ai-streaming`](https://github.com/AkshantVats/infra-ai-streaming) — open-source AI inference observability: Rust ingestion, Kafka, ClickHouse analytics, Grafana dashboards for tenant throughput and model P99.

---

## What I'm Building

**[infra-ai-streaming](https://github.com/AkshantVats/infra-ai-streaming)** `active`

An open-source AI inference observability pipeline built for the event volume and metric cardinality that standard monitoring tools break under.

```
Rust ingestion engine → Kafka → Go consumer → ClickHouse → Grafana
```

- Axum HTTP server with channel-based backpressure; batched events to Kafka via rdkafka
- Go consumer: ClickHouse batch writer (1k events / 500ms), circuit breaker, Redis overflow, DLQ
- Local stack: Redpanda, ClickHouse, Redis, Prometheus, Grafana (`docker compose up`)
- Pipeline self-metrics in OBSERVABILITY.md (ingestion P50/P95/P99, consumer lag, DLQ depth)
- Next: Grafana panels for throughput, P99 by model, cost/hour, consumer lag
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

---

## Open source

**[infra-ai-streaming](https://github.com/AkshantVats/infra-ai-streaming)** — flagship project: high-cardinality LLM inference telemetry from Rust through Kafka to ClickHouse, with Grafana as the proof surface.

This repository is [MIT licensed](LICENSE). To add or update blog posts, see [CONTRIBUTING.md](CONTRIBUTING.md) and [blog/NEW-POST-CHECKLIST.md](blog/NEW-POST-CHECKLIST.md).