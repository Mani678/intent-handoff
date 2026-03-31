from dataclasses import dataclass, field
from typing import List, Optional
import time
import uuid

@dataclass
class IntentEnvelope:
    task: str
    why: str
    constraints: List[str]
    attempted: List[str]
    confidence: float
    origin_agent: str
    current_agent: str
    hops: int = 0
    created_at: float = field(default_factory=time.time)
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    hop_log: List[dict] = field(default_factory=list)

    def transfer_to(self, next_agent: str, note: str = "") -> 'IntentEnvelope':
        self.hop_log.append({
            "from": self.current_agent,
            "to": next_agent,
            "at": time.time(),
            "note": note
        })
        self.current_agent = next_agent
        self.hops += 1
        return self

    def summary(self) -> str:
        return (
            f"[{self.envelope_id}] Task: {self.task}\n"
            f"  Why: {self.why}\n"
            f"  Constraints: {', '.join(self.constraints)}\n"
            f"  Attempted: {', '.join(self.attempted) if self.attempted else 'none'}\n"
            f"  Confidence: {self.confidence:.2f} | Hops: {self.hops}\n"
            f"  Current agent: {self.current_agent}"
        )