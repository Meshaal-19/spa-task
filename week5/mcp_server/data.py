INCIDENT = {
    "id": "INC-2024-001",
    "title": "API Gateway 502 spike",
    "description": (
        "Users reporting intermittent 502 Bad Gateway errors on the checkout API. "
        "Error rate jumped from 0.1% to 14.3% at 14:32 UTC immediately after a deployment."
    ),
    "started_at": "2024-07-24T14:32:00Z",
    "severity": "high",
    "service": "checkout-service",
}

LOGS = [
    {"timestamp": "2024-07-24T14:31:55Z", "severity": "info",    "message": "Deployment started: checkout-service v2.4.1"},
    {"timestamp": "2024-07-24T14:32:03Z", "severity": "error",   "message": "Connection pool exhausted: db-primary-1"},
    {"timestamp": "2024-07-24T14:32:05Z", "severity": "error",   "message": "502 Bad Gateway: upstream checkout-service timed out after 30s"},
    {"timestamp": "2024-07-24T14:32:06Z", "severity": "warning", "message": "Health check failing: checkout-service pod checkout-7f9d4-xkp2m"},
    {"timestamp": "2024-07-24T14:32:10Z", "severity": "error",   "message": "502 Bad Gateway: upstream checkout-service timed out after 30s"},
    {"timestamp": "2024-07-24T14:32:12Z", "severity": "info",    "message": "Auto-scaler triggered: checkout-service scaling 3 → 6 pods"},
    {"timestamp": "2024-07-24T14:32:45Z", "severity": "warning", "message": "Memory usage at 92%: checkout-service pod checkout-7f9d4-xkp2m"},
    {"timestamp": "2024-07-24T14:33:01Z", "severity": "error",   "message": "OOMKilled: checkout-service pod checkout-7f9d4-xkp2m"},
    {"timestamp": "2024-07-24T14:33:15Z", "severity": "info",    "message": "Rollback initiated: checkout-service reverting to v2.4.0"},
    {"timestamp": "2024-07-24T14:34:02Z", "severity": "info",    "message": "Rollback complete: checkout-service v2.4.0 healthy"},
]

METRICS = {
    "error_rate": [
        {"time": "14:30", "value_pct": 0.1},
        {"time": "14:31", "value_pct": 0.2},
        {"time": "14:32", "value_pct": 14.3},
        {"time": "14:33", "value_pct": 11.7},
        {"time": "14:34", "value_pct": 0.3},
    ],
    "latency_p99_ms": [
        {"time": "14:30", "value_ms": 210},
        {"time": "14:31", "value_ms": 215},
        {"time": "14:32", "value_ms": 8340},
        {"time": "14:33", "value_ms": 6120},
        {"time": "14:34", "value_ms": 230},
    ],
    "pod_count": [
        {"time": "14:30", "value": 3},
        {"time": "14:31", "value": 3},
        {"time": "14:32", "value": 3},
        {"time": "14:33", "value": 6},
        {"time": "14:34", "value": 6},
    ],
}
