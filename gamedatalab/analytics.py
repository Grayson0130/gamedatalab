"""Metric calculations shared by the CLI and tests. Python standard library."""
import math
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def iso_day(value):
    parsed = date.fromisoformat(str(value))
    if parsed.isoformat() != str(value):
        raise ValueError('Dates must use YYYY-MM-DD format')
    return parsed


def database(users, events, costs):
    # Validate ISO dates explicitly; SQLite's dynamic typing alone is insufficient.
    installs = {u[0]: iso_day(u[1]) for u in users}
    seen = {}
    for event in events:
        eid, uid, day, _, cents = event
        if uid not in installs or iso_day(day) < installs[uid]:
            raise ValueError('Unknown user or event before install')
        if not isinstance(cents, int) or isinstance(cents, bool):
            raise ValueError('Revenue must be integer cents')
        if eid in seen and seen[eid] != event:
            raise ValueError('Conflicting duplicate event identifier')
        seen[eid] = event
    if set(c[0] for c in costs) != set(installs):
        raise ValueError('Acquisition cost coverage must match users')
    if any(not isinstance(c[1], int) or isinstance(c[1], bool) for c in costs):
        raise ValueError('Acquisition costs must be integer cents')
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    con.executescript((ROOT/'sql/schema.sql').read_text())
    with con:
        con.executemany('INSERT INTO users VALUES (?,?,?,?)', users)
        con.executemany('INSERT INTO events VALUES (?,?,?,?,?)', seen.values())
        con.executemany('INSERT INTO acquisition_costs VALUES (?,?)', costs)
    return con


def query(con, filename, params):
    return [dict(r) for r in con.execute((ROOT/'sql'/filename).read_text(), params)]


def retention(con, as_of):
    iso_day(as_of)
    return query(con, 'retention.sql', {'as_of': str(as_of)})


def ltv(con, as_of, horizon=30):
    if not isinstance(horizon, int) or horizon < 0:
        raise ValueError('Horizon must be a non-negative integer')
    iso_day(as_of)
    return query(con, 'ltv.sql', {'as_of': str(as_of), 'horizon': horizon})


def experiment(n_control, successes_control, n_treatment, successes_treatment):
    """Fixed-horizon binary endpoint; normal approximation, 50:50 SRM."""
    counts = (n_control, successes_control, n_treatment, successes_treatment)
    if any(not isinstance(x, int) or isinstance(x, bool) for x in counts):
        raise ValueError('Counts must be integers')
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError('Both variants require users')
    if not 0 <= successes_control <= n_control or not 0 <= successes_treatment <= n_treatment:
        raise ValueError('Success counts out of bounds')
    if min(successes_control, n_control-successes_control,
           successes_treatment, n_treatment-successes_treatment) < 5:
        raise ValueError('Sparse endpoint: use an exact test or a larger sample')
    a, b = successes_control/n_control, successes_treatment/n_treatment
    total = n_control+n_treatment
    chi2 = (n_control-n_treatment)**2/total
    srm_p = math.erfc(math.sqrt(chi2/2))
    pooled = (successes_control+successes_treatment)/total
    se0 = math.sqrt(pooled*(1-pooled)*(1/n_control+1/n_treatment))
    se = math.sqrt(a*(1-a)/n_control+b*(1-b)/n_treatment)
    delta = b-a
    return {'control_n': n_control, 'treatment_n': n_treatment,
            'control_rate': a, 'treatment_rate': b, 'absolute_lift': delta,
            'relative_lift': delta/a,
            'ci95': [max(-1, delta-1.96*se), min(1, delta+1.96*se)],
            'p_value': math.erfc(abs(delta/se0)/math.sqrt(2)),
            'srm_p_value': srm_p, 'valid_allocation': srm_p >= 0.001,
            'decision': 'Investigate SRM before interpretation' if srm_p < 0.001
            else 'Review interval, MDE and guardrails; no automatic launch'}


def experiment_from_db(con, as_of):
    iso_day(as_of)
    groups = {r['variant']: r for r in query(con, 'experiment.sql', {'as_of': str(as_of)})}
    a, b = groups['control'], groups['treatment']
    return experiment(a['n'], a['successes'], b['n'], b['successes'])


def churn_rows(con, as_of):
    iso_day(as_of)
    return query(con, 'churn.sql', {'as_of': str(as_of)})


def auc(labels, scores):
    """Mann-Whitney ROC AUC; average ranks handle tied predictions."""
    if len(labels) != len(scores) or not labels or set(labels)-{0, 1}:
        raise ValueError('Equal-length scores and binary labels required')
    if any(not math.isfinite(s) for s in scores):
        raise ValueError('Scores must be finite')
    pos = sum(labels)
    neg = len(labels)-pos
    if not pos or not neg:
        return None
    ordered = sorted(zip(scores, labels))
    rank_sum, i = 0.0, 0
    while i < len(ordered):
        j = i+1
        while j < len(ordered) and ordered[j][0] == ordered[i][0]:
            j += 1
        rank_sum += ((i+1+j)/2)*sum(y for _, y in ordered[i:j])
        i = j
    return (rank_sum-pos*(pos+1)/2)/(pos*neg)


def churn_baseline(rows):
    # Fixed cohort dates and embargo: all training labels precede test predictions.
    train = [r for r in rows if r['install_date'] <= '2026-08-10']
    test = [r for r in rows if r['install_date'] >= '2026-08-18']
    if not train or not test:
        raise ValueError('Insufficient chronological cohorts')
    buckets = {}
    for r in train:
        b = buckets.setdefault(r['active_days_7'], [0, 0])
        b[0] += r['churned']
        b[1] += 1
    prior = (sum(r['churned'] for r in train)+1)/(len(train)+2)
    scores = [(buckets[r['active_days_7']][0]+1)/(buckets[r['active_days_7']][1]+2)
              if r['active_days_7'] in buckets else prior for r in test]
    y = [r['churned'] for r in test]
    ranked = sorted(range(len(test)), key=lambda i: (-scores[i], test[i]['user_id']))
    k = max(1, math.ceil(len(test)*0.1))
    return {'train_n': len(train), 'test_n': len(test), 'embargo_days': 7,
            'train_install_end': '2026-08-10', 'test_install_start': '2026-08-18',
            'test_prevalence': sum(y)/len(y), 'roc_auc': auc(y, scores),
            'brier': sum((p-t)**2 for p,t in zip(scores,y))/len(y),
            'constant_prior_brier': sum((prior-t)**2 for t in y)/len(y),
            'precision_at_10pct': sum(y[i] for i in ranked[:k])/k,
            'note': 'Synthetic data. Predictive risk is not causal uplift.'}
