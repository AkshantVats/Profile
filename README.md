# Akshant Sharma

Systems-focused Software Engineer with nearly 9 years architecting large-scale distributed systems, cloud-native platforms, and mission-critical backend infrastructure.

Currently building **Inferix** — an open-source AI control plane (observe → route → detect drift → retrain). Flagship code: [`infra-ai-streaming`](https://github.com/AkshantVats/infra-ai-streaming).

**Blog tooling:** `python scripts/html_to_linkedin_article.py <post.html>` — LinkedIn article export ([scripts/README.md](scripts/README.md)).

---

## Experience

| Company | Role | Tenure |
|---|---|---|
| **Wayfair** · Bengaluru | Sr. Software Engineer III · PAS & Pricing Promotions | Nov 2024 – Mar 2026 |
| **Agoda** · Bangkok | Sr. Software Engineer · Core Infrastructure · WhiteFalcon TSDB | Apr 2024 – Sep 2024 |
| **Delivery Hero** · Berlin | Sr. Software Engineer · Global Logistics Platform | Jun 2021 – Mar 2024 |
| **Walmart Labs** · Bengaluru | Software Engineer II · WeIoT SmartBuildings | Aug 2018 – May 2021 |
| **Integration Wizards** · Bengaluru | IoT Lead · Industrial IoT Platform | Mar 2017 – Aug 2018 |

---

## What I'm Building

**[infra-ai-streaming](https://github.com/AkshantVats/infra-ai-streaming)** `active` · LensAI / Inferix observability spine

```
Rust ingestion engine → Kafka → Go consumer → ClickHouse → Grafana
```

- Axum HTTP server with channel-based backpressure; batched events to Kafka via rdkafka
- Go consumer: ClickHouse batch writer, circuit breaker, Redis overflow, DLQ
- Local stack: Redpanda, ClickHouse, Redis, Prometheus, Grafana (`docker compose up`)
- Target: 1M events/min, sub-100ms ingestion P99

---

## Technical Bets

- **Rust** for systems programming where performance guarantees are non-negotiable
- **AI infrastructure** — inference pipelines, LLM observability, cost optimization at the API layer
- **Kafka internals at scale** — partition strategy, consumer group design, backpressure mechanisms
- **ClickHouse** for analytical workloads over high-cardinality event streams
- **Kubernetes** — operators, eBPF-based observability, cost-aware autoscaling

---

## By the Numbers

| Scale | System | Stack |
|---|---|---|
| 1.5T events / day | WhiteFalcon TSDB @ Agoda | Rust · Scala · Kafka · Ceph |
| 7M+ unique sensors | SmartBuildings IoT @ Walmart | Azure IoT Hub · Stream Analytics |
| 5,000 geo-events / sec | Rider tracking @ Delivery Hero | OSRM · AWS EKS · Kinesis |
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

→ [Blog](https://akshantvats.github.io/Profile/blog/) · [LinkedIn](https://linkedin.com/in/akshantsharma07)

---

## Elsewhere

- LinkedIn — [akshantsharma07](https://linkedin.com/in/akshantsharma07)
- Email — akshant3@gmail.com
- Profile — [akshantvats.github.io/Profile](https://akshantvats.github.io/Profile/)

---

## Open source

**[infra-ai-streaming](https://github.com/AkshantVats/infra-ai-streaming)** — flagship project: high-cardinality LLM inference telemetry from Rust through Kafka to ClickHouse, with Grafana as the proof surface.

This repository is [MIT licensed](LICENSE). To add or update blog posts, see [CONTRIBUTING.md](CONTRIBUTING.md) and [blog/NEW-POST-CHECKLIST.md](blog/NEW-POST-CHECKLIST.md).
