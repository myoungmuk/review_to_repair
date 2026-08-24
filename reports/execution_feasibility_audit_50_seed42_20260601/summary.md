# Execution Feasibility Audit

- Created UTC: 2026-06-01T06:03:23.765782+00:00
- Sample size: 50
- Seed: 42
- Processed data: `data/processed/crn_all.jsonl`
- Raw data: `data_raw/data_new/codereview_new.jsonl`
- Record CSV: `reports/execution_feasibility_audit_50_seed42_20260601/records.csv`
- Summary JSON: `reports/execution_feasibility_audit_50_seed42_20260601/summary.json`

## Main Counts

| check | count | rate |
| --- | ---: | ---: |
| Repo/review/commit metadata present | 50 | 100.0% |
| Review file path available from GitHub comment | 43 | 86.0% |
| Old snippet exact-matches at least one candidate file | 0 | 0.0% |
| Old snippet exact-matches uniquely | 0 | 0.0% |
| Old snippet matches after trimming line ends | 0 | 0.0% |
| Diff-marker-stripped old code exact-matches at least one candidate file | 4 | 8.0% |
| Diff-marker-stripped old code exact-matches uniquely | 4 | 8.0% |
| Diff-marker-stripped old code matches after trimming line ends | 4 | 8.0% |
| Gold new snippet exact-matches at least one candidate file | 0 | 0.0% |
| Diff-marker-stripped gold new code exact-matches at least one candidate file | 4 | 8.0% |
| Prediction can be patched by unique exact stripped old-code match | 4 | 8.0% |

## Review API Status

| status | count |
| --- | ---: |
| 200 | 43 |
| 403 | 5 |
| 404 | 1 |
| 451 | 1 |

## Language Breakdown

| language | n | path available | unique old match | unique stripped old match | patch feasible |
| --- | ---: | ---: | ---: | ---: | ---: |
| c | 3 | 3 | 0 | 1 | 1 |
| cpp | 4 | 4 | 0 | 0 | 0 |
| csharp | 3 | 3 | 0 | 0 | 0 |
| go | 11 | 9 | 0 | 0 | 0 |
| java | 5 | 5 | 0 | 2 | 2 |
| javascript | 1 | 1 | 0 | 0 | 0 |
| kotlin | 6 | 3 | 0 | 0 | 0 |
| python | 7 | 7 | 0 | 0 | 0 |
| r | 3 | 3 | 0 | 1 | 1 |
| ruby | 3 | 2 | 0 | 0 | 0 |
| scala | 2 | 2 | 0 | 0 | 0 |
| swift | 2 | 1 | 0 | 0 | 0 |

## Interpretation

This audit checks whether execution-based evaluation can be reconstructed from CodeReview-New metadata.
It does not run project tests. A case is counted as patch-feasible only when the diff-marker-stripped old code has a unique exact match in a candidate GitHub file.
Full execution evaluation would still require repository checkout, dependency installation, project-specific test command discovery, and gold-patch sanity checks.
