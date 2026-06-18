#!/usr/bin/env python3
"""Generate fresh 1200×630 blog covers from post HTML (or series-index fallbacks).

Workflow:
  1. Read each post's <h1 class="post-title"> and prose for topic keywords.
  2. Build a per-slug image prompt (rich infographic — not plain text grid).
  3. Generate PNGs:
       Manual: Use Cursor GenerateImage with --print-prompts, save to scripts/cover_generated/
       Batch: python scripts/generate_covers_from_content.py --from-dir
     
  4. This script letterboxes to 1200×630 and writes:
       blog/assets/covers/<slug>.png
       blog/assets/og/<slug>.png

Badges: series name only — no Day X, Experience N, or post numbers on the image.

Does NOT copy scripts/cover_assets_rich/ or user cursor assets; each cover is unique to its post.

Note: OpenAI API integration removed to avoid costs. Use Cursor's built-in GenerateImage tool
or open-source alternatives like Stable Diffusion instead.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

from generate_blog_covers import ALL_SLUGS, SERIES_LABEL, resize_cover, write_cover

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = Path(__file__).resolve().parent / "cover_generated"

# slug → HTML path relative to repo root (None → use series-index title/desc only)
POST_HTML: dict[str, Path | None] = {
    "day-0-series-roadmap": ROOT / "blog/series/ai-learning/day-0-series-roadmap.html",
    "day-1-kv-cache-memory-bandwidth": ROOT
    / "blog/series/ai-learning/day-1-kv-cache-memory-bandwidth.html",
    "day-2-continuous-batching-vllm": ROOT
    / "blog/series/ai-learning/day-2-continuous-batching-vllm.html",
    "day-3-token-budgets-cost-structure": None,  # draft: series-index only
    "day-4-tensor-parallelism-kafka-partitions": ROOT
    / "blog/series/ai-learning/day-4-tensor-parallelism-kafka-partitions.html",
    "day-5-sampling-deterministic-routing": ROOT
    / "blog/series/ai-learning/day-5-sampling-deterministic-routing.html",
    "day-6-quantization-vs-compression-tradeoffs": ROOT
    / "blog/series/ai-learning/day-6-quantization-vs-compression-tradeoffs.html",
    "day-7-prompt-caching-infrastructure-layer": ROOT
    / "blog/series/ai-learning/day-7-prompt-caching-infrastructure-layer.html",
    "day-8-rag-as-infra-pipeline": ROOT
    / "blog/series/ai-learning/day-8-rag-as-infra-pipeline.html",
    "day-9-gpu-memory-management": ROOT
    / "blog/series/ai-learning/day-9-gpu-memory-management.html",
    "day-10-serving-frameworks-queue-schedulers": ROOT
    / "blog/series/ai-learning/day-10-serving-frameworks-queue-schedulers.html",
    "we-killed-redpanda-on-purpose-chaos-as-commit-message": ROOT
    / "blog/series/experience/we-killed-redpanda-on-purpose-chaos-as-commit-message.html",
    "reading-victoriametrics-source-oss-interview-prep": ROOT
    / "blog/series/experience/reading-victoriametrics-source-oss-interview-prep.html",
    "building-tsdb-at-agoda": ROOT / "blog/series/experience/building-tsdb-at-agoda.html",
    "when-percentiles-lie-cross-tier-queries": ROOT
    / "blog/series/experience/when-percentiles-lie-cross-tier-queries.html",
    "seven-million-iot-sensors-failure-modes": ROOT
    / "blog/series/experience/seven-million-iot-sensors-failure-modes.html",
    "five-thousand-geo-events-per-second": ROOT
    / "blog/series/experience/five-thousand-geo-events-per-second.html",
    "cardinality-is-the-silent-killer-roaringbitmap-lessons": ROOT
    / "blog/series/experience/cardinality-is-the-silent-killer-roaringbitmap-lessons.html",
    "ten-thousand-concurrent-requests-eks-patterns-delivery-hero": ROOT
    / "blog/series/experience/ten-thousand-concurrent-requests-eks-patterns-delivery-hero.html",
    "building-ai-inference-observability": ROOT
    / "blog/series/inference-ai-project/building-ai-inference-observability.html",
    "ota-at-scale-at-least-once-is-a-feature": ROOT
    / "blog/series/experience/ota-at-scale-at-least-once-is-a-feature.html",
    "day-11-semantic-caching-vs-exact-match-redis": ROOT
    / "blog/series/ai-learning/day-11-semantic-caching-vs-exact-match-redis.html",
    "day-13-embeddings-as-dense-time-series-ids": ROOT
    / "blog/series/ai-learning/day-13-embeddings-as-dense-time-series-ids.html",
    "day-18-quantization-model-optimization": ROOT
    / "blog/series/ai-learning/day-18-quantization-model-optimization.html",
    "day-19-agent-infrastructure-tools-memory-loops": ROOT
    / "blog/series/ai-learning/day-19-agent-infrastructure-tools-memory-loops.html",
    "day-20-prompt-engineering-infra-optimization": ROOT
    / "blog/series/ai-learning/day-20-prompt-engineering-infra-optimization.html",
    "day-21-production-reliability-llm-apis": ROOT
    / "blog/series/ai-learning/day-21-production-reliability-llm-apis.html",
    "day-22-feature-flags-model-rollouts": ROOT
    / "blog/series/ai-learning/day-22-feature-flags-model-rollouts.html",
    "day-23-evaluations-as-event-streams": ROOT
    / "blog/series/ai-learning/day-23-evaluations-as-event-streams.html",
    "day-24-gpu-scheduling-resource-management": ROOT
    / "blog/series/ai-learning/day-24-gpu-scheduling-resource-management.html",
    "day-25-cost-models-llm-gateways": ROOT
    / "blog/series/ai-learning/day-25-cost-models-llm-gateways.html",
    "day-26-fine-tuning-rag-prompting-infra-cost": ROOT
    / "blog/series/ai-learning/day-26-fine-tuning-rag-prompting-infra-cost.html",
    "day-27-opentelemetry-collector-integration-hub": ROOT
    / "blog/series/ai-learning/day-27-opentelemetry-collector-integration-hub.html",
    "day-28-competitor-teardown-lensai-positioning": ROOT
    / "blog/series/ai-learning/day-28-competitor-teardown-lensai-positioning.html",
    "day-18-supplier-rate-limiting": ROOT
    / "blog/series/experience/day-18-supplier-rate-limiting.html",
    "day-19-kafka-redis-tiering-query-latency": ROOT
    / "blog/series/experience/day-19-kafka-redis-tiering-query-latency.html",
    "day-20-route-consumer-lag-keda": ROOT
    / "blog/series/experience/day-20-route-consumer-lag-keda.html",
    "day-21-launchdarkly-build-vs-buy-flagd": ROOT
    / "blog/series/experience/day-21-launchdarkly-build-vs-buy-flagd.html",
    "day-22-h3-geospatial-indexing-surge-detection": ROOT
    / "blog/series/experience/day-22-h3-geospatial-indexing-surge-detection.html",
    "day-23-osrm-5000-events-eta-infrastructure": ROOT
    / "blog/series/experience/day-23-osrm-5000-events-eta-infrastructure.html",
    "day-24-bigquery-streaming-batch-burst-truth": ROOT
    / "blog/series/experience/day-24-bigquery-streaming-batch-burst-truth.html",
    "day-25-redis-rate-limits-lua-race-conditions": ROOT
    / "blog/series/experience/day-25-redis-rate-limits-lua-race-conditions.html",
    "day-26-systems-outlast-architects-walmart": ROOT
    / "blog/series/experience/day-26-systems-outlast-architects-walmart.html",
    "day-27-redesign-wayfair-2026-eyes": ROOT
    / "blog/series/experience/day-27-redesign-wayfair-2026-eyes.html",
    "day-28-integration-tests-launch-criteria": ROOT
    / "blog/series/experience/day-28-integration-tests-launch-criteria.html",
}

# Short display titles for cover art (strip "Day N of …" prefixes from h1)
TITLE_OVERRIDE: dict[str, str] = {
    "day-0-series-roadmap": "Why I'm Writing This Series",
    "day-1-kv-cache-memory-bandwidth": "The KV Cache Is a\nMemory Bandwidth Problem",
    "day-2-continuous-batching-vllm": "Continuous Batching in vLLM:\nThe Scheduler That Keeps GPUs Busy",
    "day-3-token-budgets-cost-structure": "Token Budgets and\nReal Cost Structure",
    "day-4-tensor-parallelism-kafka-partitions": "Tensor Parallelism Meets\nKafka Partitions",
    "day-5-sampling-deterministic-routing": "Sampling and\nDeterministic Routing",
    "day-6-quantization-vs-compression-tradeoffs": "Quantization vs\nCompression Tradeoffs",
    "day-7-prompt-caching-infrastructure-layer": "Prompt Caching at the\nInfrastructure Layer",
    "day-8-rag-as-infra-pipeline": "RAG as an\nInfrastructure Pipeline",
    "day-9-gpu-memory-management": "GPU Memory Management\nFour Tenants, One VRAM Budget",
    "day-10-serving-frameworks-queue-schedulers": "Serving Frameworks Compared\nas Queue Schedulers",
    "we-killed-redpanda-on-purpose-chaos-as-commit-message": "We Killed Redpanda on Purpose\nChaos as Commit Message",
    "reading-victoriametrics-source-oss-interview-prep": "Reading VictoriaMetrics Source at 11pm\nOSS as Interview Prep",
    "building-tsdb-at-agoda": "1.5 Trillion Events/Day\nTSDB at Agoda",
    "when-percentiles-lie-cross-tier-queries": "When Percentiles Lie:\nCross-Tier Queries in a 1.8T/day TSDB",
    "seven-million-iot-sensors-failure-modes": "Seven Million IoT Sensors\n— Failure Modes Textbooks Skip",
    "five-thousand-geo-events-per-second": "Five Thousand Geo-Events\nPer Second — Shape of the Stream",
    "ten-thousand-concurrent-requests-eks-patterns-delivery-hero": "Ten Thousand Concurrent Requests\n— EKS Patterns That Actually Helped",
    "building-ai-inference-observability": "Building a Production-Grade\nAI Inference Observability Pipeline",
    "ota-at-scale-at-least-once-is-a-feature": "OTA at Scale — At-Least-Once\nIs a Feature, Not a Bug",
    "day-11-semantic-caching-vs-exact-match-redis": "Semantic Caching vs\nExact-Match Redis",
    "day-13-embeddings-as-dense-time-series-ids": "Embeddings as Dense\nTime-Series IDs",
    "day-18-quantization-model-optimization": "Quantization and\nModel Optimization",
    "day-19-agent-infrastructure-tools-memory-loops": "Agent Infrastructure —\nTools, Memory, Loops",
    "day-20-prompt-engineering-infra-optimization": "Prompt Engineering as\nInfra Optimization",
    "day-21-production-reliability-llm-apis": "Production Reliability\nfor LLM APIs",
    "day-22-feature-flags-model-rollouts": "Feature Flags for\nModel Rollouts",
    "day-23-evaluations-as-event-streams": "Evaluations as\nEvent Streams",
    "day-24-gpu-scheduling-resource-management": "GPU Scheduling as\nResource Management",
    "day-25-cost-models-llm-gateways": "Cost Models for\nLLM Gateways",
    "day-26-fine-tuning-rag-prompting-infra-cost": "Fine-Tuning vs RAG vs Prompting —\nInfra Cost View",
    "day-27-opentelemetry-collector-integration-hub": "OpenTelemetry Collector as\nIntegration Hub",
    "day-28-competitor-teardown-lensai-positioning": "Competitor Teardown:\nLensAI Positioning",
    "day-18-supplier-rate-limiting": "Rate Limiting at the\nSupplier Boundary",
    "day-19-kafka-redis-tiering-query-latency": "Kafka + Redis Tiering —\nQuery Latency by Temperature",
    "day-20-route-consumer-lag-keda": "Route Consumer Lag —\nWhy CPU-Based HPA Failed",
    "day-21-launchdarkly-build-vs-buy-flagd": "LaunchDarkly Money —\nWhy We Built flagd Ourselves",
    "day-22-h3-geospatial-indexing-surge-detection": "H3 vs Bounding Boxes —\nGeospatial Indexing That Scales",
    "day-23-osrm-5000-events-eta-infrastructure": "OSRM at 5000 Events/sec —\nWhen ETA Becomes Infrastructure",
    "day-24-bigquery-streaming-batch-burst-truth": "BigQuery Streaming vs Batch —\nBurst Traffic Truth",
    "day-25-redis-rate-limits-lua-race-conditions": "Redis Rate Limits —\nLua Scripts and Race Conditions",
    "day-26-systems-outlast-architects-walmart": "Systems That Outlast\nTheir Architects",
    "day-27-redesign-wayfair-2026-eyes": "What I'd Redesign at Wayfair\nWith 2026 Eyes",
    "day-28-integration-tests-launch-criteria": "Integration Tests —\nThe Only Launch Criteria I Trust",
}

# Topic bullets fed into image-generation prompts
TOPIC_HINTS: dict[str, str] = {
    "day-0-series-roadmap": (
        "30-day learning roadmap timeline, prefill vs decode split, "
        "VRAM/memory hierarchy icons, observability metrics schema sketch"
    ),
    "day-1-kv-cache-memory-bandwidth": (
        "two-phase pipeline PREFILL (parallel, compute-bound) vs DECODE (serial, memory-bound), "
        "KV cache blocks in VRAM, bandwidth arrows, TTFT vs TPOT meters, Redis hot-tier analogy"
    ),
    "day-2-continuous-batching-vllm": (
        "static batching GPU bubbles vs continuous token-step scheduler, "
        "vLLM request slots filling/evicting per decode step, throughput chart recovering utilization"
    ),
    "day-3-token-budgets-cost-structure": (
        "prompt tokens vs completion tokens buckets, asymmetric pricing rate card, "
        "cost_usd validation at ingest gate, variable completion cost dominating bill"
    ),
    "day-4-tensor-parallelism-kafka-partitions": (
        "tensor parallel GPU shards with all-reduce, Kafka partitions to consumer batch writer, "
        "circuit breaker Redis overflow DLQ path to ClickHouse, Triton routing table analogy"
    ),
    "day-5-sampling-deterministic-routing": (
        "consistent hash ring trace_id keep/drop, head vs tail sampling, "
        "four Grafana panels throughput P99 cost lag, Kafka to ClickHouse"
    ),
    "day-6-quantization-vs-compression-tradeoffs": (
        "INT8 vs INT4 weight precision, VRAM arithmetic, eval-fail fallback, "
        "Snappy vs Zstd codec analogy for tensors"
    ),
    "day-7-prompt-caching-infrastructure-layer": (
        "SYSTEM TOOLS RAG prefix blocks with HIT arrow into provider prefix KV cache, "
        "usage tiers CREATE READ FRESH to cost_usd down, TTL countdown, Anthropic OpenAI cache_read tokens"
    ),
    "day-8-rag-as-infra-pipeline": (
        "chunk embed index retrieve rerank generate pipeline, vector DB + object store tiers, "
        "staleness TTL, eval gates, LensAI ingest schema gaps"
    ),
    "day-9-gpu-memory-management": (
        "VRAM bar: weights activations KV cache overhead on A10G 24GB, OOM cliff at 24GB, "
        "batch=1 OK vs batch=4 OOM, four tenants one budget"
    ),
    "day-10-serving-frameworks-queue-schedulers": (
        "three serving framework columns vLLM TGI Ollama as queue schedulers, "
        "request queue with admission arrows, prefill vs decode phases, continuous batching slots, "
        "KV memory pressure meter, serving_framework label on latency_ms panel"
    ),
    "we-killed-redpanda-on-purpose-chaos-as-commit-message": (
        "Kafka Redpanda 3-broker cluster one broker KILLED red dashed box, "
        "recovery gap timeline T0 healthy T1 kill T2 wrong data window T3 restored, chaos engineering"
    ),
    "reading-victoriametrics-source-oss-interview-prep": (
        "four-pass OSS reading map: entrypoints → hot path → backpressure → compare WhiteFalcon, "
        "VictoriaMetrics ingest arrows, Go code window at 11pm clock, time-series blocks, "
        "Staff interview checklist, metrics literacy"
    ),
    "building-tsdb-at-agoda": (
        "Kafka → Rust ingestion → Redis hot tier → S3 Parquet cold tier, "
        "RoaringBitmap inverted index, 1.5T events/day counter, WhiteFalcon query path"
    ),
    "when-percentiles-lie-cross-tier-queries": (
        "WRONG: averaging P95 hot+cold vs CORRECT: merge histogram buckets then compute P95, "
        "Redis hot + S3 cold tiers, Grafana panel mismatch warning"
    ),
    "seven-million-iot-sensors-failure-modes": (
        "Azure IoT Hub → Stream Analytics edge quarantine → fleet rollup vs silent wrong sensor, "
        "7M device identities, poison telemetry DLQ, refrigeration drift while dashboard stays green"
    ),
    "five-thousand-geo-events-per-second": (
        "Order SQS PLACED→RIDER PICKED UP → Route Consumers → OSRM cluster → Route JSON, "
        "5k geo-events/s stream, hot rider partition skew, GBQ + Revisit audit path, dinner-rush lag"
    ),
    "ten-thousand-concurrent-requests-eks-patterns-delivery-hero": (
        "AWS EKS Route Service deployment at dinner-rush peak, dual gauges: CPU low green vs consumer lag high red, "
        "HPA scaling on max consumer lag not CPU theater, Order SQS + Kinesis → Route Consumers → OSRM → Route JSON pipeline, "
        "10k+ concurrent HTTP/RPC, Grafana board green while queue stale, Prometheus metrics adapter arrows"
    ),
    "cardinality-is-the-silent-killer-roaringbitmap-lessons": (
        "RoaringBitmap inverted index tag cross-product explosion, bounded labels vs exploded series, "
        "model_id tenant_id, Grafana P99 by model panel silhouette, Agoda TSDB"
    ),
    "building-ai-inference-observability": (
        "HTTP ingest → Rust Axum + WAL → Kafka → Go consumer → ClickHouse + Redis overflow buffer, "
        "prefill/decode latency fields, tenant rate limits, circuit breaker, Grafana tail"
    ),
    "ota-at-scale-at-least-once-is-a-feature": (
        "Walmart OTA delivery semantics under intermittent networks: staged manifests + durable device acks, "
        "at-least-once retry with idempotent apply keys (device_id + target_version + image hash), "
        "quarantine lane + manifest rollback, and z-score edge anomaly filtering upstream"
    ),
    "day-11-semantic-caching-vs-exact-match-redis": (
        "Exact-match Redis vs semantic embedding ANN cache: byte hash keys vs embedding vectors, "
        "similarity threshold τ tuned like tail-latency SLO, false positive risk + observability, "
        "hybrid recommendation, and anomalies fan-in with z-score latency events"
    ),
    "day-12-embeddings-as-dense-time-series-ids": (
        "Embedding vectors as dense time-series identity, high-dimensional VRAM fingerprints, "
        "cosine similarity vs L2 distance metrics, vector index refresh patterns, "
        "semantic drift detection with centroid anchors"
    ),
    "day-25-cost-models-llm-gateways": (
        "LLM cost model spreadsheet: cache hit rate × cheaper model routing × prompt cache savings, "
        "token economics tracking (input/output/cached tokens), cost_usd validation gate, "
        "LensAI inference economics dashboard, ROI calculation before Rust implementation"
    ),
    "day-25-redis-rate-limits-lua-race-conditions": (
        "Distributed Redis rate limiter: INCR+EXPIRE race condition under concurrent load, "
        "atomic Lua script solution (read-modify-write in single Redis command), "
        "sliding window implementation, Black Friday near-miss timeline, "
        "Wayfair supplier pricing API protection"
    ),
    "supplier-apis-and-token-buckets-wayfair-circuit-breaker": (
        "Token bucket rate limiter protecting supplier APIs, circuit breaker state machine (closed/open/half-open), "
        "fallback cache tier, request throttling at peak traffic, Wayfair supplier integration patterns"
    ),
    "delphi-aletheia-feed-sub-second-price-visibility": (
        "Real-time price feed ingestion pipeline, sub-second latency visibility dashboards, "
        "Delphi Aletheia system architecture, WebSocket price stream, ClickHouse time-series storage, "
        "Grafana tail latency panels"
    ),
    "two-weeks-one-readme-hiring-committees-scroll": (
        "Documentation debt vs hiring signal tension, two-week README sprint before interviews, "
        "hiring committee scroll fatigue, knowledge transfer bottleneck, onboarding velocity metrics, "
        "technical writing as staff signal"
    ),
    "day-13-embeddings-as-dense-time-series-ids": (
        "Embedding vectors as dense time-series identity, high-dimensional VRAM fingerprints, "
        "cosine similarity vs L2 distance metrics, vector index refresh patterns, "
        "semantic drift detection with centroid anchors"
    ),
    "day-18-quantization-model-optimization": (
        "INT8/INT4 quantization techniques, model compression trade-offs, VRAM savings vs accuracy loss, "
        "quantization-aware training, ONNX runtime optimization, TensorRT inference acceleration"
    ),
    "day-19-agent-infrastructure-tools-memory-loops": (
        "Agent tool calling patterns, persistent memory stores (vector DB + Redis), agentic loop architectures, "
        "function schemas, tool retry + backoff strategies, LensAI agent design patterns"
    ),
    "day-20-prompt-engineering-infra-optimization": (
        "Prompt templates as config, versioned prompt registry, A/B testing prompts in prod, "
        "cost reduction through better prompts, latency reduction via shorter prompts, prompt observability metrics"
    ),
    "day-21-production-reliability-llm-apis": (
        "Circuit breakers for LLM providers, fallback chains (primary/secondary models), timeout tuning per model, "
        "retry with exponential backoff, health checks + dead letter queues, SLO tracking for inference latency"
    ),
    "day-22-feature-flags-model-rollouts": (
        "Gradual model rollout patterns (canary/blue-green), feature flags for model switching, tenant-based routing, "
        "shadow traffic for new models, rollback mechanisms, LaunchDarkly for AI/ML deployments"
    ),
    "day-23-evaluations-as-event-streams": (
        "LLM eval pipelines as Kafka streams, online vs offline evaluation, golden dataset management, "
        "regression detection, eval metrics (accuracy/latency/cost), continuous evaluation in production"
    ),
    "day-24-gpu-scheduling-resource-management": (
        "Multi-tenant GPU sharing, resource quotas per tenant, priority queuing for GPU requests, "
        "preemption strategies, Kubernetes GPU scheduling, pod anti-affinity for model replicas"
    ),
    "day-26-fine-tuning-rag-prompting-infra-cost": (
        "Cost comparison matrix: fine-tuning GPU hours vs RAG vector DB hosting vs prompt token overhead, "
        "latency trade-offs, when to fine-tune vs RAG, hybrid approaches, infrastructure implications, LensAI cost model"
    ),
    "day-27-opentelemetry-collector-integration-hub": (
        "OTEL collector as central telemetry router, spans/metrics/logs unification, receiver/processor/exporter pipeline, "
        "sampling strategies, vendor-agnostic observability, LensAI telemetry architecture"
    ),
    "day-28-competitor-teardown-lensai-positioning": (
        "LensAI vs competitors (Datadog LLM, Langfuse, Helicone), feature comparison matrix, pricing models, "
        "integration depth, observability vs monitoring, product differentiation, go-to-market positioning"
    ),
    "day-18-supplier-rate-limiting": (
        "Token bucket rate limiters protecting external supplier APIs, per-supplier rate limits, backoff strategies, "
        "circuit breaker integration, fallback cache tier, Wayfair supplier API protection patterns"
    ),
    "day-19-kafka-redis-tiering-query-latency": (
        "Hot Redis tier + cold Kafka tier for time-series queries, temperature-based data routing, "
        "query latency by tier (sub-10ms hot vs 100ms+ cold), TTL-based eviction, cross-tier query merging, Delivery Hero observability"
    ),
    "day-20-route-consumer-lag-keda": (
        "HPA scaling on consumer lag metrics (not CPU), KEDA ScaledObject for SQS queue depth, dinner-rush lag spikes, "
        "CPU low but queue stale, Prometheus metrics adapter, Route Service scaling patterns"
    ),
    "day-21-launchdarkly-build-vs-buy-flagd": (
        "Build vs buy decision for feature flags, LaunchDarkly cost scaling, flagd (open-source) deployment, "
        "flag evaluation latency, Redis-backed flag store, percentage rollouts, targeting rules, cost savings"
    ),
    "day-22-h3-geospatial-indexing-surge-detection": (
        "H3 hexagonal grid indexing, geospatial surge detection, bounding box limitations, hexagon resolution levels, "
        "rider density heatmaps, spatial query performance, Delivery Hero geo-infrastructure"
    ),
    "day-23-osrm-5000-events-eta-infrastructure": (
        "OSRM cluster for route calculation, 5k geo-events/s throughput, ETA latency budgets, route JSON caching, "
        "hot rider partition skew, Order SQS → Route Consumers pipeline, dinner-rush traffic patterns"
    ),
    "day-24-bigquery-streaming-batch-burst-truth": (
        "BigQuery streaming inserts vs batch loads, burst traffic cost implications, streaming buffer delays, "
        "data freshness SLOs, cost optimization with batch windows, real-time vs near-real-time trade-offs"
    ),
    "day-26-systems-outlast-architects-walmart": (
        "Long-lived system design lessons from Walmart, documentation debt, knowledge transfer patterns, "
        "architecture decision records, system longevity vs team turnover, maintainable complexity"
    ),
    "day-27-redesign-wayfair-2026-eyes": (
        "Wayfair architecture hindsight, supplier API modernization, event-driven redesign, observability gaps filled, "
        "cost optimization opportunities, lessons learned, 2026 technology retrospective"
    ),
    "day-28-integration-tests-launch-criteria": (
        "Integration test suites as launch gates, end-to-end test patterns, smoke tests vs full regression, "
        "test data management, flaky test quarantine, CI/CD integration, launch confidence from test coverage"
    ),
}

ACCENT: dict[str, str] = {
    "day-0-series-roadmap": "neon green #5bd37a",
    "day-1-kv-cache-memory-bandwidth": "neon green #5bd37a",
    "day-2-continuous-batching-vllm": "neon green #5bd37a",
    "day-3-token-budgets-cost-structure": "neon green #5bd37a",
    "day-4-tensor-parallelism-kafka-partitions": "neon green #5bd37a",
    "day-5-sampling-deterministic-routing": "neon green #5bd37a",
    "day-6-quantization-vs-compression-tradeoffs": "neon green #5bd37a",
    "day-7-prompt-caching-infrastructure-layer": "neon green #5bd37a",
    "day-8-rag-as-infra-pipeline": "neon green #5bd37a",
    "day-9-gpu-memory-management": "neon green #5bd37a",
    "day-10-serving-frameworks-queue-schedulers": "neon green #5bd37a",
    "day-11-semantic-caching-vs-exact-match-redis": "neon green #5bd37a",
    "day-12-embeddings-as-dense-time-series-ids": "neon green #5bd37a",
    "day-13-embeddings-as-dense-time-series-ids": "neon green #5bd37a",
    "day-18-quantization-model-optimization": "neon green #5bd37a",
    "day-19-agent-infrastructure-tools-memory-loops": "neon green #5bd37a",
    "day-20-prompt-engineering-infra-optimization": "neon green #5bd37a",
    "day-21-production-reliability-llm-apis": "neon green #5bd37a",
    "day-22-feature-flags-model-rollouts": "neon green #5bd37a",
    "day-23-evaluations-as-event-streams": "neon green #5bd37a",
    "day-24-gpu-scheduling-resource-management": "neon green #5bd37a",
    "day-25-cost-models-llm-gateways": "neon green #5bd37a",
    "day-26-fine-tuning-rag-prompting-infra-cost": "neon green #5bd37a",
    "day-27-opentelemetry-collector-integration-hub": "neon green #5bd37a",
    "day-28-competitor-teardown-lensai-positioning": "neon green #5bd37a",
    "building-tsdb-at-agoda": "electric blue #64b4ff",
    "when-percentiles-lie-cross-tier-queries": "electric blue #64b4ff",
    "seven-million-iot-sensors-failure-modes": "cyan #00d2e6",
    "five-thousand-geo-events-per-second": "amber #f59e0b",
    "cardinality-is-the-silent-killer-roaringbitmap-lessons": "electric blue #64b4ff",
    "ten-thousand-concurrent-requests-eks-patterns-delivery-hero": "electric blue #64b4ff",
    "supplier-apis-and-token-buckets-wayfair-circuit-breaker": "electric blue #64b4ff",
    "delphi-aletheia-feed-sub-second-price-visibility": "electric blue #64b4ff",
    "we-killed-redpanda-on-purpose-chaos-as-commit-message": "electric blue #64b4ff",
    "reading-victoriametrics-source-oss-interview-prep": "electric blue #64b4ff",
    "ota-at-scale-at-least-once-is-a-feature": "electric blue #64b4ff",
    "two-weeks-one-readme-hiring-committees-scroll": "electric blue #64b4ff",
    "day-18-supplier-rate-limiting": "electric blue #64b4ff",
    "day-19-kafka-redis-tiering-query-latency": "electric blue #64b4ff",
    "day-20-route-consumer-lag-keda": "electric blue #64b4ff",
    "day-21-launchdarkly-build-vs-buy-flagd": "electric blue #64b4ff",
    "day-22-h3-geospatial-indexing-surge-detection": "electric blue #64b4ff",
    "day-23-osrm-5000-events-eta-infrastructure": "electric blue #64b4ff",
    "day-24-bigquery-streaming-batch-burst-truth": "electric blue #64b4ff",
    "day-25-redis-rate-limits-lua-race-conditions": "electric blue #64b4ff",
    "day-26-systems-outlast-architects-walmart": "electric blue #64b4ff",
    "day-27-redesign-wayfair-2026-eyes": "electric blue #64b4ff",
    "day-28-integration-tests-launch-criteria": "electric blue #64b4ff",
    "building-ai-inference-observability": "violet #a78bfa",
}


def _strip_day_prefix(title: str) -> str:
    t = re.sub(r"^Day \d+ of [^—]+—\s*", "", title)
    t = re.sub(r"^Day \d+ —\s*", "", t)
    return t.strip()


def parse_title_from_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'<h1[^>]*class="post-title"[^>]*>(.*?)</h1>', text, re.S)
    if m:
        raw = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        return _strip_day_prefix(raw)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return ""


def cover_title(slug: str) -> str:
    if slug in TITLE_OVERRIDE:
        return TITLE_OVERRIDE[slug]
    path = POST_HTML.get(slug)
    if path and path.exists():
        return parse_title_from_html(path)
    return slug.replace("-", " ").title()


def image_prompt(slug: str) -> str:
    badge = SERIES_LABEL[slug]
    title = cover_title(slug).replace("\n", " / ")
    topics = TOPIC_HINTS[slug]
    accent = ACCENT[slug]
    return (
        f"Wide technical blog cover infographic, 16:9 landscape (1200×630), dark navy background #080e1c. "
        f"Top-left rounded pill badge with text exactly: '{badge}'. "
        f"NO day numbers, NO 'Day X of N', NO 'Experience X of N', NO post counters anywhere. "
        f"Large bold white main title (2-3 lines max): '{title}'. "
        f"Rich infographic content reflecting this article: {topics}. "
        f"Include charts, pipeline arrows, icons, glowing {accent} neon accents. "
        f"NOT a boring text grid, NOT stock photography, NOT reused generic AI art. "
        f"Professional systems-engineering blog thumbnail style."
    )


def install_source(slug: str, src: Path) -> None:
    from PIL import Image

    img = Image.open(src).convert("RGB")
    write_cover(slug, img)




def run_from_dir(src_dir: Path, slugs: list[str] | None = None) -> None:
    targets = slugs or ALL_SLUGS
    print(f"Installing covers from {src_dir} → blog/assets/{{covers,og}}/")
    for slug in targets:
        src = src_dir / f"{slug}.png"
        if not src.exists():
            raise FileNotFoundError(f"Missing generated art: {src}")
        install_source(slug, src)




def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print-prompts",
        action="store_true",
        help="Print image generation prompts for all slugs (use with Cursor GenerateImage)",
    )
    parser.add_argument(
        "--from-dir",
        type=Path,
        default=GENERATED_DIR,
        help=f"Directory of <slug>.png sources (default: {GENERATED_DIR})",
    )
    parser.add_argument("--slug", action="append", dest="slugs", help="Only process these slugs")
    parser.add_argument(
        "sources",
        nargs="*",
        help="Optional slug=path pairs to install single files",
    )
    args = parser.parse_args()

    if args.print_prompts:
        print("📝 Image generation prompts for Cursor GenerateImage tool:\n")
        for slug in args.slugs or ALL_SLUGS:
            prompt = image_prompt(slug)
            print(f"=== {slug} ===")
            print(f"Prompt: {prompt}")
            print(f"Save as: scripts/cover_generated/{slug}.png\n")
        return

    if args.sources:
        for item in args.sources:
            if "=" in item:
                slug, path = item.split("=", 1)
            else:
                slug = Path(item).stem
                path = item
            install_source(slug, Path(path))
        return

    run_from_dir(args.from_dir, args.slugs)


if __name__ == "__main__":
    main()
