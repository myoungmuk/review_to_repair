# Multi-Model Review-to-Repair Handoff

Last updated: 2026-04-27

This document hands off the current state of the Review-to-Repair multi-model experiment so it can be continued on another machine without relying on chat history.

## 1. Research Scope

The experiment extends the existing single-model Review-to-Repair pilot into a multi-code-LLM diagnostic experiment.

Keep fixed:

- Dataset: CodeReview-New pilot subset, 100 examples.
- Seed: 42.
- Conditions: `no_review`, `direct`, `gold_location`.
- Metrics: `exact_match_line_trim`, `location_overlap_f1`.
- Evaluation level: snippet-level / hunk-level CodeReview-New data.

Do not add these in this phase:

- `predicted_location`
- `no_review+gold_location`
- new datasets
- new metrics
- changed definitions of the three existing conditions

Research message:

> Review-to-Repair에서 리뷰 코멘트와 정답 위치 정보는 모델의 수정 행동을 바꾸지만, 위치 중첩 향상이 정확 수정 성공으로 충분히 전환되는지는 모델별로 진단해야 한다.

## 2. Main Model Decision

Main experiment model set:

- `qwen2.5-coder:7b`
- `deepseek-coder:6.7b`
- `codegemma:7b`

Excluded model:

- `starcoder2:7b`

Exclusion reason:

- `starcoder2:7b` returned mostly empty outputs, usually `"\n"`, under the current Ollama chat backend.
- This was treated as a model-backend/call compatibility issue, not as Review-to-Repair model performance.
- It must not be included in paper metrics, macro averages, or main full-run comparisons.

Fallback candidate:

- `qwen2.5-coder:3b`
- This is only a fallback if `codegemma:7b` is unavailable.
- Do not use it in the main full run unless explicitly approved.

Observed Ollama models on the laptop during this work:

- `qwen2.5-coder:7b`
- `qwen2.5-coder:3b`
- `deepseek-coder:6.7b`
- `starcoder2:7b`
- `codegemma:7b`

On a new desktop, check again:

```bash
ollama list
```

If required models are missing, pull them manually:

```bash
ollama pull qwen2.5-coder:7b
ollama pull deepseek-coder:6.7b
ollama pull codegemma:7b
```

Do not automatically pull large models from the experiment script.

## 3. Important Files

Code and config added or changed:

- `configs/multi_model_r2r_seed42.json`
- `scripts/run_multi_model_r2r.py`
- `scripts/run_local_predictions.py`
- `README.md`
- `.gitignore`
- `docs/multi_model_r2r_handoff.md`
- `docs/codex_jupyterlab_continuation_prompt.md`
- `docs/multi_model_r2r_research_status_2026-04-27.md`
- `docs/multi_model_r2r_paper_integration_plan.md`
- `docs/multi_model_r2r_np768_smoke_results_2026-04-27.md`
- `docs/multi_model_r2r_np1024_smoke_results_2026-04-27.md`
- `docs/multi_model_r2r_np1024_full_results_2026-04-27.md`

Existing experiment components used by the new script:

- Data loading / common utilities: `scripts/common.py`
- CRN subset preparation: `scripts/prepare_crn_subset.py`
- Prompt generation: `scripts/make_prompts.py`
- Existing local generation helper: `scripts/run_local_predictions.py`
- Existing exact-match evaluation: `scripts/evaluate_predictions.py`
- Existing gain bootstrap reference: `scripts/bootstrap_gain.py`

Main data and prompts:

- Gold data: `data/processed/crn_pilot100.jsonl`
- Prompt directory: `prompts/crn_pilot100`
- Conditions:
  - `prompts/crn_pilot100/no_review_prompts.jsonl`
  - `prompts/crn_pilot100/direct_prompts.jsonl`
  - `prompts/crn_pilot100/gold_location_prompts.jsonl`

Note: the currently open IDE file `prompts/crn_pilot100_seed7/direct_prompts.jsonl` is not the seed=42 main config path. The multi-model experiment uses `prompts/crn_pilot100`.

## 4. Config State

Primary config:

```bash
configs/multi_model_r2r_seed42.json
```

Important settings:

- `gold_path`: `data/processed/crn_pilot100.jsonl`
- `prompt_dir`: `prompts/crn_pilot100`
- `subset_size`: `100`
- `seed`: `42`
- `conditions`: `["no_review", "direct", "gold_location"]`
- `metrics`: `["exact_match_line_trim", "location_overlap_f1"]`
- `backend`: `ollama`
- `temperature`: `0.0`
- `bootstrap_iters`: `1000`
- `reuse_existing_predictions`: `false`

`reuse_existing_predictions` is intentionally false for the clean multi-model run. Existing qwen pilot outputs can still be reused only if the user explicitly passes `--reuse-legacy-predictions`.

## 5. New Multi-Model Runner

Primary runner:

```bash
python scripts/run_multi_model_r2r.py --help
```

Useful arguments:

- `--config configs/multi_model_r2r_seed42.json`
- `--output-root <results_dir>`
- `--models qwen2.5-coder:7b deepseek-coder:6.7b codegemma:7b`
- `--limit 10`
- `--num-predict 512`
- `--resume`
- `--continue-on-error`
- `--reuse-legacy-predictions`
- `--skip-model-check`

The runner:

- selects required models from config and local `ollama list`;
- refuses to proceed if a required model family is unavailable;
- does not auto-pull models;
- keeps conditions fixed to `no_review`, `direct`, `gold_location`;
- writes one JSONL file per model and condition;
- computes per-example metrics during generation aggregation;
- writes integrity, metrics, bootstrap gain, paper table, and summary files.

Expected output layout:

```text
results/
  multi_model_r2r_seed42/
    generations/
      qwen2.5-coder-7b/
        no_review.jsonl
        direct.jsonl
        gold_location.jsonl
      deepseek-coder-6.7b/
        no_review.jsonl
        direct.jsonl
        gold_location.jsonl
      codegemma-7b/
        no_review.jsonl
        direct.jsonl
        gold_location.jsonl
    all_generations.jsonl
    metrics_by_model_condition.csv
    bootstrap_gains_by_model.csv
    integrity_report.csv
    paper_results_table.csv
    output_length_diagnostics.csv
    truncation_risk_cases.csv
    summary.md
    plots/
```

Each generation row includes at least:

- `example_id`
- `model`
- `condition`
- `old_snippet`
- `review_comment`
- `target_code`
- `raw_output`
- `extracted_code`
- `exact_match_line_trim`
- `location_overlap_f1`
- `error`
- `warning`

It also includes compatibility fields such as `id`, `baseline`, `prediction`, and failure flags.

## 6. Post-Processing Rule

The same extraction rule is applied to every model and condition.

- If fenced Markdown code blocks exist, use the longest non-empty code block.
- If no code fence exists, strip common wrapper labels and evaluate the remaining text.
- Strip gold-location marker tags if a model echoes them.
- Do not use qwen-specific post-processing.

This matters because model output style differs across qwen, deepseek, and codegemma.

## 7. Clean 3-Model Smoke Test Already Run

Clean smoke output root:

```bash
results/multi_model_r2r_seed42_smoke10_all3_np512
```

Command requested for the clean smoke:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np512 \
  --num-predict 512 \
  --resume \
  --continue-on-error
```

Important: the clean smoke did not reuse old qwen pilot outputs. `generation_source=backend` was verified for all 90 outputs.

Expected clean smoke size:

- 3 models x 3 conditions x 10 examples = 90 outputs.

Integrity result:

| model | condition | output count | generation errors | extraction failures | evaluation failures | valid evaluations |
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

| model | condition | n valid | exact_match_line_trim | location_overlap_f1 |
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

Paper-ready smoke table:

| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.539 | 0.913 | 0.100 | 0.079 | -0.100 | 0.374 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.439 | 0.500 | 0.481 | 0.000 | 0.061 | 0.000 | -0.019 |
| codegemma:7b | 0.000 | 0.100 | 0.000 | 0.783 | 0.641 | 0.867 | 0.100 | -0.142 | -0.100 | 0.226 |
| macro_average | 0.000 | 0.067 | 0.000 | 0.561 | 0.560 | 0.754 | 0.067 | -0.000 | -0.067 | 0.194 |

Bootstrap gain summary from smoke:

| model | comparison | metric | gain | 95% CI |
| --- | --- | --- | ---: | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 0.100 | [0.000, 0.300] |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 0.079 | [-0.140, 0.308] |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | -0.100 | [-0.300, 0.000] |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 0.374 | [0.163, 0.615] |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 0.000 | [0.000, 0.000] |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 0.061 | [-0.093, 0.260] |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 0.000 | [0.000, 0.000] |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | -0.019 | [-0.153, 0.106] |
| codegemma:7b | direct - no_review | exact_match_line_trim | 0.100 | [0.000, 0.300] |
| codegemma:7b | direct - no_review | location_overlap_f1 | -0.142 | [-0.444, 0.170] |
| codegemma:7b | gold_location - direct | exact_match_line_trim | -0.100 | [-0.300, 0.000] |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 0.226 | [-0.056, 0.507] |
| macro_average | direct - no_review | exact_match_line_trim | 0.067 | [0.000, 0.200] |
| macro_average | direct - no_review | location_overlap_f1 | -0.000 | [-0.162, 0.171] |
| macro_average | gold_location - direct | exact_match_line_trim | -0.067 | [-0.200, 0.000] |
| macro_average | gold_location - direct | location_overlap_f1 | 0.194 | [0.032, 0.370] |

These are smoke-test results only. Do not present them as final 100-example main experiment results.

## 8. Truncation Risk From `--num-predict 512`

The 512-token clean smoke passed generation, extraction, and evaluation integrity, but it produced truncation/format risk flags for deepseek.

Flagged cases:

| model | condition | example_id | raw chars | extracted chars | flags |
| --- | --- | --- | ---: | ---: | --- |
| deepseek-coder:6.7b | no_review | `crn-002192` | 1900 | 1900 | `unclosed_code_fence;near_num_predict_char_risk` |
| deepseek-coder:6.7b | gold_location | `crn-002192` | 1728 | 1659 | `unclosed_code_fence` |
| deepseek-coder:6.7b | gold_location | `crn-008823` | 216 | 216 | `unclosed_code_fence` |

Recommendation:

- Do not start the full 100-example run at `--num-predict 512` yet.
- First run a clean 10-example smoke with a larger shared cap, preferably `--num-predict 768` or `--num-predict 1024`.
- Use the same cap for all three models.

Suggested next smoke on desktop:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768 \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

Alternative, slower but safer:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np1024 \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

Proceed to full run only if the new smoke has:

- 90 outputs;
- 0 generation errors;
- 0 extraction failures;
- 0 evaluation failures;
- no serious truncation-risk cases.

Updated JupyterLab status:

- `results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1`
  - Clean 90-output smoke.
  - 0 generation errors, 0 extraction failures, 0 evaluation failures.
  - No near-cap truncation risk.
  - One short deepseek `gold_location` `unclosed_code_fence` format flag.
- `results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab`
  - Clean 90-output smoke requested after the `np768` check.
  - 0 generation errors, 0 extraction failures, 0 evaluation failures.
  - No near-cap truncation risk.
  - Same short deepseek `gold_location` `unclosed_code_fence` format flag.

The `np1024` smoke confirms that 1024 is safe, but it does not show that 1024
is necessary. The `np768` smoke remains sufficient for the full run unless the
priority is maximum conservativeness against truncation concerns.

## 9. Desktop Migration Checklist

After copying the repository to the desktop:

1. Open the copied folder as the working directory.
2. Confirm these files exist:

```bash
python scripts/run_multi_model_r2r.py --help
python -c "import json; print(json.load(open('configs/multi_model_r2r_seed42.json'))['run_name'])"
```

3. Confirm Ollama is installed and running.

```bash
ollama list
```

4. Pull missing required models manually if needed.

```bash
ollama pull qwen2.5-coder:7b
ollama pull deepseek-coder:6.7b
ollama pull codegemma:7b
```

5. Re-run a 10-example smoke with the selected shared cap.

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_desktop \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

6. Inspect:

```text
results/multi_model_r2r_seed42_smoke10_all3_np768_desktop/summary.md
results/multi_model_r2r_seed42_smoke10_all3_np768_desktop/integrity_report.csv
results/multi_model_r2r_seed42_smoke10_all3_np768_desktop/truncation_risk_cases.csv
```

7. Full experiment has already been approved and completed in this JupyterLab
   state; do not rerun unless there is a clear reason.

## 10. Full Run Command After Approval

The approved full run used `--num-predict 1024` and is complete.

Completed result directory:

```text
results/multi_model_r2r_seed42_np1024
```

Detailed result note:

```text
docs/multi_model_r2r_np1024_full_results_2026-04-27.md
```

Final full-run integrity:

- Expected outputs: 900
- Actual outputs: 900
- Backend-generated rows: 900
- Generation errors: 0
- Extraction failures: 0
- Evaluation failures: 0
- Valid evaluations: 900

Full-run command used:

```bash
python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np1024 \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

Expected full-run output count:

- 3 models x 3 conditions x 100 examples = 900 outputs.

Expected final files:

- `summary.md`
- `paper_results_table.csv`
- `metrics_by_model_condition.csv`
- `bootstrap_gains_by_model.csv`
- `integrity_report.csv`
- `output_length_diagnostics.csv`
- `truncation_risk_cases.csv`
- per-model/per-condition JSONL files under `generations/`

## 11. Earlier Smoke Runs For Context

These are not the clean main smoke, but they explain decisions:

- `results/multi_model_r2r_seed42_smoke10_installed`
  - Used qwen models that were initially installed.
  - Not the final main model set.

- `results/multi_model_r2r_seed42_smoke10`
  - Included `starcoder2:7b`.
  - Starcoder produced mostly empty outputs under Ollama chat and was excluded.

- `results/multi_model_r2r_seed42_smoke10_codegemma`
  - Codegemma-only smoke.
  - Passed generation, extraction, and evaluation.
  - Some codegemma outputs were generated with a different cap before the clean all-3 rerun, so this is not the final comparable smoke.

- `results/multi_model_r2r_seed42_smoke10_all3_np512`
  - Clean comparable all-3 smoke with shared `--num-predict 512`.
  - This is now superseded by the clean `np768` and `np1024` JupyterLab smokes.

- `results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1`
  - Clean comparable all-3 smoke with shared `--num-predict 768`.
  - Current recommended cap for the full run.

- `results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab`
  - Clean comparable all-3 smoke with shared `--num-predict 1024`.
  - This became the chosen full-run cap.

- `results/multi_model_r2r_seed42_np1024`
  - Completed 100-example full run.
  - 900/900 outputs, 900 valid evaluations, 0 generation/extraction/evaluation failures.
  - Main paper result directory.

## 12. Key Cautions

- Do not include `starcoder2:7b` in main metrics.
- Do not reuse old qwen pilot results in the clean multi-model run unless explicitly requested.
- Do not rerun the full 100-example experiment unless explicitly requested.
- Do not change condition definitions or metrics.
- Do not treat smoke-test metrics as final paper results.
- Use `results/multi_model_r2r_seed42_np1024` as the current final paper result.
- If the desktop has different Ollama model tags, update the config or pass `--models` explicitly.
- If any model-condition has missing IDs, duplicate IDs, extraction failures, evaluation failures, or serious truncation flags, stop and inspect before continuing.
