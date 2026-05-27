from prometheus_client import (
    Counter,
    Gauge,
    Histogram
)


# =========================
# REQUEST METRICS
# =========================

TOTAL_REQUESTS = Counter(

    "total_requests",

    "Total AI requests"
)

FAILED_REQUESTS = Counter(

    "failed_requests",

    "Failed AI requests"
)


# =========================
# PROVIDER METRICS
# =========================

PROVIDER_FAILURES = Counter(

    "provider_failures",

    "Provider failures",

    ["provider"]
)

PROVIDER_LATENCY = Histogram(

    "provider_latency_ms",

    "Provider latency",

    ["provider"]
)


# =========================
# WEBSOCKET METRICS
# =========================

ACTIVE_WEBSOCKETS = Gauge(

    "active_websockets",

    "Active websocket connections"
)


# =========================
# QUEUE METRICS
# =========================

CHAT_QUEUE_DEPTH = Gauge(

    "chat_queue_depth",

    "Chat queue depth"
)

EMBEDDING_QUEUE_DEPTH = Gauge(

    "embedding_queue_depth",

    "Embedding queue depth"
)