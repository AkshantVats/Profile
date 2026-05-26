#!/usr/bin/env python3
"""Generate fresh 1200×630 blog covers from post HTML (or series-index fallbacks).

Workflow:
  1. Read each post's <h1 class="post-title"> and prose for topic keywords.
  2. Build a per-slug image prompt (rich infographic — not plain text grid).
  3. Generate PNGs via Cursor GenerateImage (or any 1200×630 source), then:
       python scripts/generate_covers_from_content.py --install <slug>.png ...
     or copy manually into scripts/cover_generated/<slug>.png and run --from-dir.

  4. This script letterboxes to 1200×630 and writes:
       blog/assets/covers/<slug>.png
       blog/assets/og/<slug>.png

Badges: series name only — no Day X, Experience N, or post numbers on the image.

Does NOT copy scripts/cover_assets_rich/ or user cursor assets; each cover is unique to its post.
"""
from __future__ import annotations

import argparse
import re
import shutil
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
    "we-killed-redpanda-on-purpose-chaos-as-commit-message": "electric blue #64b4ff",
    "reading-victoriametrics-source-oss-interview-prep": "electric blue #64b4ff",
    "building-tsdb-at-agoda": "electric blue #64b4ff",
    "when-percentiles-lie-cross-tier-queries": "electric blue #64b4ff",
    "seven-million-iot-sensors-failure-modes": "cyan #00d2e6",
    "five-thousand-geo-events-per-second": "amber #f59e0b",
    "ten-thousand-concurrent-requests-eks-patterns-delivery-hero": "electric blue #64b4ff",
    "cardinality-is-the-silent-killer-roaringbitmap-lessons": "electric blue #64b4ff",
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
        help="Print GenerateImage prompts for all slugs and exit",
    )
    parser.add_argument(
        "--from-dir",
        type=Path,
        default=GENERATED_DIR,
        help=f"Directory of <slug>.png sources (default: {GENERATED_DIR})",
    )
    parser.add_argument("--slug", action="append", dest="slugs")
    parser.add_argument(
        "sources",
        nargs="*",
        help="Optional slug=path pairs to install single files",
    )
    args = parser.parse_args()

    if args.print_prompts:
        for slug in args.slugs or ALL_SLUGS:
            print(f"\n=== {slug} ===\n{image_prompt(slug)}\n")
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
