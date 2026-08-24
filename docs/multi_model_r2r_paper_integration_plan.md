# Multi-Model R2R Paper Integration Plan

Date: 2026-04-27

This note records how the ongoing multi-model experiment should update the
current KCC2026 paper draft.

## Current Paper Draft

Current draft PDF:

```text
Untitled Folder/KCC2026강명묵 (6).pdf
```

The current paper is a compact 3-page KCC-style paper.

Current title:

```text
CodeReview-New 기반 Review-to-Repair에서 위치 정보의 역할 진단
```

Current main question:

> In Review-to-Repair, when gold location markers are added to a prompt that
> already contains a review comment, does the increase in location overlap
> convert into an exact-match repair improvement?

Current single-model setting:

- Dataset: CodeReview-New seed=42 100 examples
- Model: `qwen2.5-coder:7b`
- Backend: Ollama
- Temperature: 0.0
- Conditions: `no_review`, `direct`, `gold_location`
- Outputs: 100 examples x 3 conditions = 300
- Metrics: `exact_match_line_trim`, `location_overlap_f1`

Current reported qwen2.5-coder:7b results:

| condition | exact_match_line_trim | location_overlap_f1 |
| --- | ---: | ---: |
| no_review | 0.00 | 0.524 |
| direct | 0.07 | 0.578 |
| gold_location | 0.09 | 0.740 |

Current bootstrap gain summary:

| comparison | metric | gain | 95% CI |
| --- | --- | ---: | --- |
| direct - no_review | Exact | +0.070 | [0.020, 0.120] |
| direct - no_review | Loc.F1 | +0.054 | [-0.016, 0.123] |
| gold_location - direct | Exact | +0.020 | [-0.050, 0.090] |
| gold_location - direct | Loc.F1 | +0.162 | [0.089, 0.235] |

Current conclusion:

- Review comments can improve exact repair in this pilot.
- Gold location markers increase location overlap.
- The location-overlap increase does not reliably convert into exact-match
  repair success.
- Therefore Review-to-Repair failures should not be attributed only to change
  localisation; review understanding and edit generation remain plausible
  bottlenecks.

## Why Multi-Model Is Needed

The current paper's main weakness is that the quantitative evidence is based on
one main model. The multi-model extension should not change the research
question or add new conditions. Its purpose is to check whether the current
diagnostic claim is stable across multiple local code LLMs.

Main model set for the extended experiment:

- `qwen2.5-coder:7b`
- `deepseek-coder:6.7b`
- `codegemma:7b`

Excluded:

- `starcoder2:7b`, because it produced mostly empty outputs under the current
  Ollama chat backend. This is treated as a model-backend compatibility issue,
  not as Review-to-Repair performance.

Do not use as a substitute without explicit approval:

- `devstral:24b`
- `qwen2.5-coder:3b`
- any non-main model

## Target Updated Paper Claim

The updated paper should avoid claiming that gold location generally improves
repair success. The stronger and safer multi-model claim is:

> Across multiple local code LLMs, review comments and gold location information
> change repair behavior, but improvements in changed-line overlap do not
> necessarily translate into exact-match repair success. The conversion from
> localisation improvement to exact repair is model-dependent and should be
> diagnosed separately.

This preserves the current paper's core message while reducing the single-model
threat to validity.

## Completed Experiment For Paper Update

The conservative `np1024` full run has now been completed.

Full result note:

```text
docs/multi_model_r2r_np1024_full_results_2026-04-27.md
```

Result directory:

```text
results/multi_model_r2r_seed42_np1024
```

Final integrity:

- 900/900 outputs
- 900 valid evaluations
- 0 generation errors
- 0 extraction failures
- 0 evaluation failures
- 0 near-cap truncation flags

The earlier smoke command was:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

Smoke pass criteria:

- 3 models x 3 conditions x 10 examples = 90 outputs
- generation errors: 0
- extraction failures: 0
- evaluation failures: 0
- no missing IDs
- no duplicate IDs
- no repeated empty or whitespace-only outputs
- no serious truncation indicators such as repeated `unclosed_code_fence` or
  `near_num_predict_char_risk`

Final full-run size:

```text
3 models x 3 conditions x 100 examples = 900 outputs
```

## Paper Tables After Full Run

For the 3-page KCC format, avoid too many large tables. Prefer one compact main
table and one compact gain table.

Recommended main result table:

| model | no_review exact | direct exact | gold exact | no_review Loc.F1 | direct Loc.F1 | gold Loc.F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.070 | 0.090 | 0.503 | 0.567 | 0.748 |
| deepseek-coder:6.7b | 0.000 | 0.020 | 0.010 | 0.480 | 0.550 | 0.558 |
| codegemma:7b | 0.000 | 0.050 | 0.060 | 0.622 | 0.689 | 0.804 |
| macro average | 0.000 | 0.047 | 0.053 | 0.535 | 0.602 | 0.703 |

Recommended gain table:

| model | direct-no_review Exact | gold-direct Exact | direct-no_review Loc.F1 | gold-direct Loc.F1 |
| --- | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.070 | 0.020 | 0.064 | 0.181 |
| deepseek-coder:6.7b | 0.020 | -0.010 | 0.070 | 0.008 |
| codegemma:7b | 0.050 | 0.010 | 0.067 | 0.116 |
| macro average | 0.047 | 0.007 | 0.067 | 0.102 |

If space is tight, report confidence intervals only in text for the most
important comparisons:

- `gold_location - direct` on `location_overlap_f1`
- `gold_location - direct` on `exact_match_line_trim`

Full-run macro confidence intervals:

- `direct - no_review` exact: `+0.047`, 95% CI `[0.023, 0.073]`
- `direct - no_review` Loc.F1: `+0.067`, 95% CI `[0.026, 0.109]`
- `gold_location - direct` exact: `+0.007`, 95% CI `[-0.027, 0.043]`
- `gold_location - direct` Loc.F1: `+0.102`, 95% CI `[0.064, 0.139]`

## Paper Sections To Revise

### Abstract

Replace single-model wording with multi-model wording. Keep the core result:
location overlap improves more clearly than exact repair success.

### Section 1 Introduction

Current framing can stay. Add one sentence that the experiment checks whether
the diagnostic pattern is model-specific or visible across multiple local code
LLMs.

### Section 4.1 Experiment Summary

Replace:

```text
모델은 qwen2.5-coder:7b이며 ...
총 생성 수는 300개 출력
```

With:

```text
모델은 qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b 세 가지이며 ...
총 생성 수는 900개 출력(3 models x 3 conditions x 100 examples)
```

Also state that all models use the same prompt files, data subset, decoding
temperature, and generation cap.

### Section 4.3 Results

Replace current single-model table with the multi-model table. The discussion
should focus on:

- whether direct improves exact over no_review per model;
- whether gold_location improves Loc.F1 over direct per model;
- whether gold_location improves exact over direct per model;
- whether macro-level trends match or hide model-specific behavior.

### Section 5 Discussion

Change from:

```text
qwen2.5-coder:7b 실험에서 ...
```

To:

```text
세 코드 LLM 비교에서 ...
```

The discussion should emphasize model-specific conversion gaps:

- A model may move edits closer to the gold location without producing exact
  target code.
- Location information may help localisation but still leave review semantics
  and edit generation unresolved.
- Exact match remains conservative and should be discussed as such.

### Section 6 Conclusion

Remove or soften the single-model limitation. Replace it with:

- still a 100-example pilot;
- still snippet-level / hunk-level, not full-file localisation;
- still exact-match-centered;
- but no longer limited to one main model.

## Current Blocker

The local machine could not reach the Ollama registry:

```text
curl: (28) Failed to connect to registry.ollama.ai port 443 after 10002 ms: Timeout was reached
```

This was resolved by copying the user's Windows Ollama model store to the
server. The main three models are now available and the clean `np768` smoke was
completed at:

```text
results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1
```

Detailed smoke result note:

```text
docs/multi_model_r2r_np768_smoke_results_2026-04-27.md
```

The full 100-example run was later approved by the user and completed at:

```text
results/multi_model_r2r_seed42_np1024
```
