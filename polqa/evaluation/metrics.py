from typing import List, Dict
import math

def percentiles(values: List[float], ps=(50, 90, 95)) -> Dict[str, float]:
    if not values:
        return {"p50": 0.0, "p90": 0.0, "p95": 0.0}
    values_sorted = sorted(values)
    def q(p):
        if len(values_sorted) == 1:
            return values_sorted[0]
        k = (len(values_sorted)-1) * (p/100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return values_sorted[int(k)]
        d0 = values_sorted[f] * (c-k)
        d1 = values_sorted[c] * (k-f)
        return d0 + d1
    return {f"p{p}": q(p) for p in ps}

def summarize_run_metrics(latencies: List[float], failures: int, total: int, consistency_at_k: float) -> Dict:
    failure_rate = (failures / total) if total > 0 else 0.0
    return {"consistency_at_k": consistency_at_k, "failure_rate": failure_rate,
            "latency_sec": percentiles(latencies)}
