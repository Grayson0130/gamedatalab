"""Synthetic telemetry, not an industry benchmark. No network or personal data."""
import random
from datetime import date, timedelta

AS_OF = date(2026, 9, 30)
START = date(2026, 7, 1)


def generate(n=1200, seed=42):
    if n < 100:
        raise ValueError('At least 100 users are required')
    rng = random.Random(seed)
    users, events, costs = [], [], []
    for i in range(n):
        uid = f'u{i:06d}'
        installed = START + timedelta(days=rng.randrange(75))
        channel = rng.choice(['organic', 'search', 'creator'])
        variant = rng.choice(['control', 'treatment'])
        users.append((uid, installed.isoformat(), channel, variant))
        engagement = rng.betavariate(2, 3)
        for age in range((AS_OF-installed).days+1):
            active = age == 0 or rng.random() < engagement*(0.28+0.72*0.96**age)
            if not active:
                continue
            day = (installed+timedelta(days=age)).isoformat()
            events.append((f'{uid}-{age}-s', uid, day, 'session', 0))
            if age == 0 and rng.random() < 0.59+0.035*(variant == 'treatment'):
                events.append((f'{uid}-tutorial', uid, day, 'tutorial_complete', 0))
            if rng.random() < 0.055:
                cents = rng.choice([199, 499, 999, 1999])
                events.append((f'{uid}-{age}-p', uid, day, 'purchase', cents))
                if rng.random() < 0.06:
                    events.append((f'{uid}-{age}-r', uid, day, 'refund', -cents))
        costs.append((uid, 0 if channel == 'organic' else rng.choice([150, 225, 350, 500])))
    return users, events, costs
