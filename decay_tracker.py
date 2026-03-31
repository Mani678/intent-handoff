import time
from intent_envelope import IntentEnvelope

DECAY_PER_HOP = 0.12
HUMAN_REANCHOR_THRESHOLD = 0.40
MAX_HOPS = 5

class IntentDecayTracker:
    def __init__(self):
        self.history = []

    def evaluate(self, envelope: IntentEnvelope) -> dict:
        decayed_confidence = envelope.confidence - (DECAY_PER_HOP * envelope.hops)
        decayed_confidence = max(0.0, decayed_confidence)

        age_seconds = time.time() - envelope.created_at
        time_decay = min(0.1, age_seconds / 3600)
        final_confidence = max(0.0, decayed_confidence - time_decay)

        status = self._get_status(final_confidence, envelope.hops)

        result = {
            "envelope_id": envelope.envelope_id,
            "original_confidence": envelope.confidence,
            "decayed_confidence": round(final_confidence, 3),
            "hops": envelope.hops,
            "age_seconds": round(age_seconds, 1),
            "status": status,
            "action": self._get_action(status)
        }

        self.history.append(result)
        return result

    def _get_status(self, confidence: float, hops: int) -> str:
        if hops >= MAX_HOPS:
            return "exceeded_max_hops"
        if confidence <= HUMAN_REANCHOR_THRESHOLD:
            return "needs_reanchor"
        if confidence <= 0.60:
            return "degraded"
        return "healthy"

    def _get_action(self, status: str) -> str:
        return {
            "healthy": "proceed",
            "degraded": "proceed_with_caution",
            "needs_reanchor": "route_to_human",
            "exceeded_max_hops": "abort_and_escalate"
        }[status]

    def report(self, result: dict):
        print(f"\n── Intent Decay Report ──────────────────")
        print(f"  Envelope:    {result['envelope_id']}")
        print(f"  Confidence:  {result['original_confidence']:.2f} → {result['decayed_confidence']:.2f}")
        print(f"  Hops:        {result['hops']}")
        print(f"  Age:         {result['age_seconds']}s")
        print(f"  Status:      {result['status']}")
        print(f"  Action:      {result['action']}")
        print(f"─────────────────────────────────────────")