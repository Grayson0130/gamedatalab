import argparse
import csv
import hashlib
import json
from pathlib import Path
from . import __version__
from .synthetic import generate, AS_OF
from .analytics import database, retention, ltv, experiment_from_db, churn_rows, churn_baseline


def write_csv(path, header, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description='Offline synthetic game analytics lab')
    p.add_argument('--output', type=Path, default=Path('reports/demo'))
    p.add_argument('--users', type=int, default=1200)
    p.add_argument('--seed', type=int, default=42)
    args = p.parse_args()
    try:
        users, events, costs = generate(args.users, args.seed)
        con = database(users, events, costs)
        summary = {'version': __version__, 'synthetic': True, 'seed': args.seed,
                   'users': len(users), 'events': len(events), 'as_of': str(AS_OF),
                   'ltv_horizon': 'D0-D30 inclusive; mature cohorts only',
                   'platform_fee_assumption': 0.30,
                   'ltv': ltv(con, AS_OF), 'experiment': experiment_from_db(con, AS_OF),
                   'churn': churn_baseline(churn_rows(con, AS_OF))}
        ret = retention(con, AS_OF)
    except (ValueError, KeyError) as exc:
        p.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output/'users.csv', ['user_id','install_date','channel','variant'], users)
    write_csv(args.output/'events.csv', ['event_id','user_id','event_date','event_name','revenue_cents'], events)
    write_csv(args.output/'acquisition_costs.csv', ['user_id','cost_cents'], costs)
    write_csv(args.output/'retention.csv', list(ret[0]), [list(r.values()) for r in ret])
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    hashes = {name: hashlib.sha256((args.output/name).read_bytes()).hexdigest()
              for name in ['users.csv','events.csv','acquisition_costs.csv']}
    (args.output/'input-hashes.json').write_text(json.dumps(hashes, indent=2)+'\n', encoding='utf-8')
    lines = ['# Demo results', '', '**Synthetic data — not industry benchmarks.**', '',
             f'Users: {len(users)} · seed: {args.seed} · cutoff: {AS_OF}', '',
             '## Mature-cohort D0–D30 economics', '',
             '| Channel | Installs | Receipts LTV (USD) | CAC (USD) | Contribution ROAS |',
             '| --- | ---: | ---: | ---: | ---: |']
    for r in summary['ltv']:
        roas = 'N/A' if r['contribution_roas'] is None else f"{r['contribution_roas']:.3f}"
        lines.append(f"| {r['channel']} | {r['installs']} | {r['observed_receipts_ltv_usd']:.4f} | {r['cac_usd']:.4f} | {roas} |")
    ex, ch = summary['experiment'], summary['churn']
    lines += ['', '## Fixed-horizon tutorial experiment', '',
              f"Absolute lift: {ex['absolute_lift']:.4f}; 95% CI: {ex['ci95']}; p={ex['p_value']:.4f}.",
              f"SRM p={ex['srm_p_value']:.4f}. {ex['decision']}.", '',
              '## Temporal churn baseline', '',
              f"Train/test users: {ch['train_n']}/{ch['test_n']}; ROC AUC: {ch['roc_auc']}; Brier: {ch['brier']:.4f}.",
              'Risk scores do not identify users who benefit from incentives.', '',
              '## Limits', '',
              'Independent daily activity, simplified refunds/costs, no service cost or tax ledger. No model deployment.',
              'The tutorial treatment effect is programmed into the generator; this is not external evidence.',
              'See [metrics](../../docs/metrics.md) and [experimentation](../../docs/experimentation.md).', '']
    (args.output/'README.md').write_text('\n'.join(lines), encoding='utf-8')
    con.close()
    print(f'Wrote synthetic results to {args.output}')


if __name__ == '__main__':
    main()
