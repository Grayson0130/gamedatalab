# Demo results

**Synthetic data — not industry benchmarks.**

Users: 1200 · seed: 42 · cutoff: 2026-09-30

## Mature-cohort D0–D30 economics

| Channel | Installs | Receipts LTV (USD) | CAC (USD) | Contribution ROAS |
| --- | ---: | ---: | ---: | ---: |
| creator | 313 | 4.2096 | 3.0327 | 0.972 |
| organic | 332 | 3.6136 | 0.0000 | N/A |
| search | 347 | 4.5686 | 3.1066 | 1.029 |

## Fixed-horizon tutorial experiment

Absolute lift: 0.0663; 95% CI: [0.011671447671591784, 0.12086519907791038]; p=0.0176.
SRM p=0.8625. Review interval, MDE and guardrails; no automatic launch.

## Temporal churn baseline

Train/test users: 664/423; ROC AUC: 0.7396825396825397; Brier: 0.1111.
Risk scores do not identify users who benefit from incentives.

## Limits

Independent daily activity, simplified refunds/costs, no service cost or tax ledger. No model deployment.
The tutorial treatment effect is programmed into the generator; this is not external evidence.
See [metrics](../../docs/metrics.md) and [experimentation](../../docs/experimentation.md).
