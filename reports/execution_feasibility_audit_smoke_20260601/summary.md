# Execution Feasibility Audit

- Created UTC: 2026-06-01T06:01:59.958159+00:00
- Sample size: 3
- Seed: 42
- Processed data: `data/processed/crn_all.jsonl`
- Raw data: `data_raw/data_new/codereview_new.jsonl`
- Record CSV: `reports/execution_feasibility_audit_smoke_20260601/records.csv`
- Summary JSON: `reports/execution_feasibility_audit_smoke_20260601/summary.json`

## Main Counts

| check | count | rate |
| --- | ---: | ---: |
| Repo/review/commit metadata present | 3 | 100.0% |
| Review file path available from GitHub comment | 3 | 100.0% |
| Old snippet exact-matches at least one candidate file | 0 | 0.0% |
| Old snippet exact-matches uniquely | 0 | 0.0% |
| Old snippet matches after trimming line ends | 0 | 0.0% |
| Diff-marker-stripped old code exact-matches at least one candidate file | 1 | 33.3% |
| Diff-marker-stripped old code exact-matches uniquely | 1 | 33.3% |
| Diff-marker-stripped old code matches after trimming line ends | 1 | 33.3% |
| Gold new snippet exact-matches at least one candidate file | 0 | 0.0% |
| Diff-marker-stripped gold new code exact-matches at least one candidate file | 1 | 33.3% |
| Prediction can be patched by unique exact stripped old-code match | 1 | 33.3% |

## Review API Status

| status | count |
| --- | ---: |
| 200 | 3 |

## Language Breakdown

| language | n | path available | unique old match | unique stripped old match | patch feasible |
| --- | ---: | ---: | ---: | ---: | ---: |
| java | 1 | 1 | 0 | 0 | 0 |
| r | 2 | 2 | 0 | 1 | 1 |

## Interpretation

This audit checks whether execution-based evaluation can be reconstructed from CodeReview-New metadata.
It does not run project tests. A case is counted as patch-feasible only when the diff-marker-stripped old code has a unique exact match in a candidate GitHub file.
Full execution evaluation would still require repository checkout, dependency installation, project-specific test command discovery, and gold-patch sanity checks.
