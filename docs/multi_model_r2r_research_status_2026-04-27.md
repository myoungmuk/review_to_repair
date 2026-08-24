# Multi-Model Review-to-Repair Research Status

Date: 2026-04-27

This note records the current research status in this machine. It is not a
final 100-example experiment report.

## Current Scope

The experiment remains fixed to the seed=42 CodeReview-New pilot subset:

- Data: `data/processed/crn_pilot100.jsonl`
- Prompt directory: `prompts/crn_pilot100`
- Conditions: `no_review`, `direct`, `gold_location`
- Metrics: `exact_match_line_trim`, `location_overlap_f1`
- Main models:
  - `qwen2.5-coder:7b`
  - `deepseek-coder:6.7b`
  - `codegemma:7b`
- Excluded model:
  - `starcoder2:7b`, because it returned mostly empty outputs under the current Ollama chat backend.

No full 100-example run has been executed in this session.

## Current Machine State

Repository root:

```text
/home/selab/kmm/review_to_repair_crn
```

The multi-model runner and config are present and executable:

- `scripts/run_multi_model_r2r.py`
- `configs/multi_model_r2r_seed42.json`

Current local Ollama model list after copying the user's Windows Ollama model
store to this server:

```text
NAME                   ID              SIZE      MODIFIED
codegemma:7b           0c96700aaada    5.0 GB    28 hours ago
starcoder2:7b          1550ab21b10d    4.0 GB    34 hours ago
deepseek-coder:6.7b    ce298d984115    3.8 GB    34 hours ago
qwen2.5-coder:3b       f72c60cabf62    1.9 GB    6 days ago
qwen2.5-coder:7b       dae161e27b0e    4.7 GB    6 days ago
devstral:24b           9bd74193e939    14 GB     12 days ago
```

The required main models are installed. Extra installed models are not part of
the main experiment unless explicitly approved.

## Model Pull Attempt

The user approved pulling the three main models, with the explicit constraint
that the full run must not be started yet.

Attempted commands:

```bash
ollama pull qwen2.5-coder:7b
ollama pull qwen2.5-coder:7b
ollama pull codegemma:7b
ollama pull deepseek-coder:6.7b
```

All pull attempts failed at the manifest fetch step with registry timeout
errors:

```text
pull model manifest: Get "https://registry.ollama.ai/v2/library/qwen2.5-coder/manifests/7b": dial tcp 104.21.75.227:443: i/o timeout
pull model manifest: Get "https://registry.ollama.ai/v2/library/qwen2.5-coder/manifests/7b": dial tcp 172.67.182.229:443: i/o timeout
pull model manifest: Get "https://registry.ollama.ai/v2/library/codegemma/manifests/7b": dial tcp 104.21.75.227:443: i/o timeout
pull model manifest: Get "https://registry.ollama.ai/v2/library/deepseek-coder/manifests/6.7b": dial tcp 104.21.75.227:443: i/o timeout
```

Interpretation at the time of the pull attempt:

- This is a network or registry access blocker, not an experiment-code failure.
- `devstral:24b` should not be substituted into the main experiment because it is outside the approved model set.

Direct registry check:

```text
curl -I --connect-timeout 10 https://registry.ollama.ai/v2/
curl: (28) Failed to connect to registry.ollama.ai port 443 after 10002 ms: Timeout was reached
```

## Latest Existing Clean Smoke

Existing result directory:

```text
results/multi_model_r2r_seed42_smoke10_all3_np512
```

This was a clean comparable 3-model smoke with shared `--num-predict 512`.

Generation/evaluation integrity:

| model | condition | output_count | generation_errors | extraction_failures | evaluation_failures | valid_evaluations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | no_review | 10 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | direct | 10 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | gold_location | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | no_review | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | direct | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | gold_location | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | no_review | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | direct | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | gold_location | 10 | 0 | 0 | 0 | 10 |

Metrics from this 10-example smoke only:

| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | ---: | ---: | ---: |
| qwen2.5-coder:7b | no_review | 10 | 0.000 | 0.460 |
| qwen2.5-coder:7b | direct | 10 | 0.100 | 0.539 |
| qwen2.5-coder:7b | gold_location | 10 | 0.000 | 0.913 |
| deepseek-coder:6.7b | no_review | 10 | 0.000 | 0.439 |
| deepseek-coder:6.7b | direct | 10 | 0.000 | 0.500 |
| deepseek-coder:6.7b | gold_location | 10 | 0.000 | 0.481 |
| codegemma:7b | no_review | 10 | 0.000 | 0.783 |
| codegemma:7b | direct | 10 | 0.100 | 0.641 |
| codegemma:7b | gold_location | 10 | 0.000 | 0.867 |

Truncation or formatting risk cases from the existing `np512` smoke:

| model | condition | example_id | raw chars | extracted chars | flags |
| --- | --- | --- | ---: | ---: | --- |
| deepseek-coder:6.7b | no_review | `crn-002192` | 1900 | 1900 | `unclosed_code_fence;near_num_predict_char_risk` |
| deepseek-coder:6.7b | gold_location | `crn-002192` | 1728 | 1659 | `unclosed_code_fence` |
| deepseek-coder:6.7b | gold_location | `crn-008823` | 216 | 216 | `unclosed_code_fence` |

## Research Interpretation So Far

The existing smoke supports the diagnostic framing but is not a final result:

- Review comments and gold location information change model behavior.
- Higher location overlap does not reliably convert into exact repair success.
- The pattern is model-specific:
  - qwen shows a large gold-location location-F1 increase in the smoke, but no exact-match gain under gold location.
  - deepseek has no exact-match success in the 10-example smoke and shows truncation/formatting risk under `np512`.
  - codegemma has high location overlap in `no_review` and `gold_location`, but direct review does not improve location F1 in this tiny smoke.

Because the sample size is only 10 examples, these observations should be used
only as smoke-test diagnostics and motivation for the full experiment, not as
paper-level conclusions.

## np768 Smoke Update

The Ollama model blocker was resolved by copying the user's local Windows
Ollama model store to this server. The main three models are now available:

- `qwen2.5-coder:7b`
- `deepseek-coder:6.7b`
- `codegemma:7b`

A clean retry smoke was completed at:

```text
results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1
```

Detailed result note:

```text
docs/multi_model_r2r_np768_smoke_results_2026-04-27.md
```

Summary:

- Expected outputs: 90
- Actual outputs: 90
- Backend-generated outputs: 90
- Generation errors: 0
- Extraction failures: 0
- Evaluation failures: 0
- Valid evaluations: 90
- Remaining risk flag: one short `unclosed_code_fence` in `deepseek-coder:6.7b`
  `gold_location` for `crn-008823`; no near-cap truncation flag.

This smoke supports using `--num-predict 768` for the full run, but the full
run still requires explicit user approval.

## np1024 Smoke Update

At the user's request, a second 10-example smoke was completed with
`--num-predict 1024` and no full run was started.

Result directory:

```text
results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab
```

Detailed result note:

```text
docs/multi_model_r2r_np1024_smoke_results_2026-04-27.md
```

Summary:

- Expected outputs: 90
- Actual outputs: 90
- Generation errors: 0
- Extraction failures: 0
- Evaluation failures: 0
- Valid evaluations: 90
- Empty raw outputs: 0
- Empty extracted outputs: 0
- Near generation cap risk: 0
- Remaining risk flag: the same short `unclosed_code_fence` in
  `deepseek-coder:6.7b` `gold_location` for `crn-008823`.

The `np1024` smoke was structurally clean and effectively matched the clean
`np768` smoke. This confirms that `1024` is safe, but it does not show that
`1024` is necessary.

## np1024 Full Run Update

The user approved the conservative `np1024` full run. It has been completed.

Result directory:

```text
results/multi_model_r2r_seed42_np1024
```

Detailed result note:

```text
docs/multi_model_r2r_np1024_full_results_2026-04-27.md
```

Final integrity:

- Expected outputs: 900
- Actual outputs: 900
- Backend-generated rows: 900
- Generation errors: 0
- Extraction failures: 0
- Evaluation failures: 0
- Valid evaluations: 900

Main paper-ready results:

| model | no_review exact | direct exact | gold_location exact | no_review loc F1 | direct loc F1 | gold_location loc F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.070 | 0.090 | 0.503 | 0.567 | 0.748 |
| deepseek-coder:6.7b | 0.000 | 0.020 | 0.010 | 0.480 | 0.550 | 0.558 |
| codegemma:7b | 0.000 | 0.050 | 0.060 | 0.622 | 0.689 | 0.804 |
| macro_average | 0.000 | 0.047 | 0.053 | 0.535 | 0.602 | 0.703 |

Macro gain summary:

- `direct - no_review` exact gain: `+0.047`, 95% CI `[0.023, 0.073]`
- `direct - no_review` location-F1 gain: `+0.067`, 95% CI `[0.026, 0.109]`
- `gold_location - direct` exact gain: `+0.007`, 95% CI `[-0.027, 0.043]`
- `gold_location - direct` location-F1 gain: `+0.102`, 95% CI `[0.064, 0.139]`

Truncation diagnostics:

- Empty raw outputs: 0
- Empty extracted outputs: 0
- Near generation cap risk: 0
- Remaining suspicious cases: 5 short `unclosed_code_fence` flags from
  `deepseek-coder:6.7b`; none are near-cap truncation cases.

Backend note:

- CodeGemma generation triggered transient Ollama backend crashes during the
  initial full-run pass.
- Failed empty-output rows were backed up, removed from the active JSONL files,
  and regenerated with resume.
- `scripts/run_local_predictions.py` now supports optional
  `OLLAMA_NUM_CTX`; the final recovery pass used `OLLAMA_NUM_CTX=8192`.

## Next Required Step

Use the full-run result files to revise the KCC2026 paper tables and claims.
The main conclusion should move from a single-model qwen diagnostic to a
three-model diagnostic: gold location improves location overlap, but the added
exact-match gain over direct review is small and uncertain at the macro level.
