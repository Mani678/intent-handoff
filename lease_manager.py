import time
import threading
from intent_envelope import IntentEnvelope

LEASE_DURATION_SECONDS = 30

class LeaseManager:
    def __init__(self):
        self.leases = {}
        self.lock = threading.Lock()

    def claim(self, envelope: IntentEnvelope, agent: str) -> dict:
        with self.lock:
            envelope_id = envelope.envelope_id
            now = time.time()

            # Check if lease exists and is still valid
            if envelope_id in self.leases:
                lease = self.leases[envelope_id]
                if lease['status'] == 'completed':
                    return {
                        'granted': False,
                        'reason': 'already_completed',
                        'held_by': lease['agent']
                    }
                if lease['status'] == 'leased' and now < lease['expires_at']:
                    return {
                        'granted': False,
                        'reason': 'lease_active',
                        'held_by': lease['agent'],
                        'expires_in': round(lease['expires_at'] - now, 1)
                    }

            # Grant the lease
            self.leases[envelope_id] = {
                'agent': agent,
                'status': 'leased',
                'claimed_at': now,
                'expires_at': now + LEASE_DURATION_SECONDS,
                'envelope_id': envelope_id
            }

            return {
                'granted': True,
                'agent': agent,
                'expires_at': round(LEASE_DURATION_SECONDS),
                'reason': 'lease_granted'
            }

    def renew(self, envelope: IntentEnvelope, agent: str) -> dict:
        with self.lock:
            envelope_id = envelope.envelope_id
            now = time.time()

            if envelope_id not in self.leases:
                return {'renewed': False, 'reason': 'no_lease_found'}

            lease = self.leases[envelope_id]
            if lease['agent'] != agent:
                return {'renewed': False, 'reason': 'not_your_lease', 'held_by': lease['agent']}

            lease['expires_at'] = now + LEASE_DURATION_SECONDS
            return {'renewed': True, 'agent': agent, 'expires_in': LEASE_DURATION_SECONDS}

    def complete(self, envelope: IntentEnvelope, agent: str) -> dict:
        with self.lock:
            envelope_id = envelope.envelope_id

            if envelope_id not in self.leases:
                return {'completed': False, 'reason': 'no_lease_found'}

            lease = self.leases[envelope_id]
            if lease['agent'] != agent:
                return {'completed': False, 'reason': 'not_your_lease'}

            lease['status'] = 'completed'
            return {'completed': True, 'agent': agent}

    def release_expired(self) -> list:
        with self.lock:
            now = time.time()
            released = []
            for envelope_id, lease in self.leases.items():
                if lease['status'] == 'leased' and now > lease['expires_at']:
                    lease['status'] = 'expired'
                    released.append(envelope_id)
            return released

    def status(self, envelope: IntentEnvelope) -> dict:
        envelope_id = envelope.envelope_id
        if envelope_id not in self.leases:
            return {'status': 'unclaimed'}
        lease = self.leases[envelope_id]
        now = time.time()
        return {
            'status': lease['status'],
            'agent': lease['agent'],
            'expires_in': max(0, round(lease['expires_at'] - now, 1)) if lease['status'] == 'leased' else None
        }