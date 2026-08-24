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

Current local Ollama model list:

```text
NAME            ID              SIZE     MODIFIED
devstral:24b    9bd74193e939    14 GB    12 days ago
```

The required main models are not installed on this machine yet.

## Model Pull Attempt

The user approved pulling the three main models, with the explicit constraint
that the full run must not be started yet.

Attempted commands:

```bash
ollama pull qwen2.5-coder:7b
ollama pull codegemma:7b
```

Both failed at the manifest fetch step with registry timeout errors:

```text
pull model manifest: Get "https://registry.ollama.ai/v2/library/qwen2.5-coder/manifests/7b": dial tcp 104.21.75.227:443: i/o timeout
pull model manifest: Get "https://registry.ollama.ai/v2/library/codegemma/manifests/7b": dial tcp 104.21.75.227:443: i/o timeout
```

Interpretation:

- This is a network or registry access blocker, not an experiment-code failure.
- `np768` smoke cannot be run on this machine until the required main models are installed.
- `devstral:24b` should not be substituted into the main experiment because it is outside the approved model set.

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

## Next Required Step

Resolve the Ollama registry/network blocker and install the required main
models:

```bash
ollama pull qwen2.5-coder:7b
ollama pull deepseek-coder:6.7b
ollama pull codegemma:7b
```

After all three models are installed, run the approved pre-full-run smoke:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

Only after the `np768` smoke passes integrity and truncation checks should a
full-run command be proposed. The full 100-example run still requires explicit
user approval.
