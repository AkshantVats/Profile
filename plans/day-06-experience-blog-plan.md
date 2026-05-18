# Plan A — Experience blog (Calendar Day 6 · Experience 5 of N)

**Status:** Implemented 2026-05-18 on `feat/day-6-blogs`.

**Companion:** AI Learning Day 5 — `day-5-sampling-deterministic-routing.html` (same calendar day).

**Daily thread:** Four Grafana panels on `ai-inference-product` prove cardinality discipline (Experience) and sampling discipline (AI) share one schema.

## Metadata

| Field | Value |
|-------|--------|
| **H1** | Cardinality Is the Silent Killer — RoaringBitmap Lessons |
| **Kicker** | Experience 5 of N |
| **Slug** | `cardinality-is-the-silent-killer-roaringbitmap-lessons.html` |
| **`article:published_time`** | `2026-05-18` |
| **Word target** | 1,400–1,800 |
| **Mermaid** | 3 |

## Bridge

- **P99 inference latency by model** panel on **AI Inference — Product SLOs** (`uid: ai-inference-product`) — ClickHouse `quantile(0.99)(latency_ms)` by `model_id`, not Prometheus label explosion.
- Cross-link AI Day 5 sampling post.
- No G-05 / ticket IDs in prose.

## Outline (shipped)

1. Cold open — scrape lag, `pod` label
2. Silent killer — series = metric + tags; cross-product
3. WhiteFalcon / RoaringBitmap (team vs mine attr-boxes)
4. Cross-product diagram + illustrative labels
5. Prometheus wall + LensAI split
6. Today's `model_id × tenant_id` pipeline
7. Grafana P99 panel bet + observability split diagram
8. AI Day 5 sibling
9. Failure modes + tradeoffs table
10. What stayed
