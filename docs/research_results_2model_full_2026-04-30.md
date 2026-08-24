# Review-to-Repair 2-Model Full Run Results

작성일: 2026-04-30

## 한 줄 결론

CodeReview-New 전체 유효 14,855개 예제에서 `qwen2.5-coder:7b`와 `deepseek-coder:6.7b`를 비교한 결과, 리뷰 코멘트는 exact match와 location overlap을 모두 개선했지만, gold location 정보는 location overlap을 크게 개선해도 exact repair 성공으로 안정적으로 이어지지 않았다.

## 실행 개요

- 데이터: `data/processed/crn_all.jsonl`
- 예제 수: 14,855
- 모델: `qwen2.5-coder:7b`, `deepseek-coder:6.7b`
- 조건: `no_review`, `direct`, `gold_location`
- 메트릭: `exact_match_line_trim`, `location_overlap_f1`
- Backend: local Ollama
- Decoding: temperature 0.0, seed 42, num_predict 512
- Workers: 6
- 전체 출력 수: 89,130 rows
- 실행 시간: 2026-04-30 03:16:59 UTC ~ 2026-04-30 06:50:37 UTC, 약 3시간 33분 38초
- 결과 디렉터리: `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/`

## 무결성 확인

모든 모델/조건에서 다음을 만족했다.

- expected count: 14,855
- output count: 14,855
- missing example id count: 0
- duplicate example id count: 0
- generation error count: 0
- extraction failure count: 0
- evaluation failure count: 0
- valid evaluation count: 14,855

## 주요 결과

| model | no_review exact | direct exact | gold_location exact | no_review loc.F1 | direct loc.F1 | gold_location loc.F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.006 | 0.091 | 0.067 | 0.381 | 0.531 | 0.697 |
| deepseek-coder:6.7b | 0.000 | 0.007 | 0.006 | 0.345 | 0.407 | 0.452 |
| macro average | 0.003 | 0.049 | 0.036 | 0.363 | 0.469 | 0.575 |

## Bootstrap Gain Summary

| model | comparison | metric | gain | 95% CI |
| --- | --- | --- | ---: | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | +0.084 | [0.080, 0.089] |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | +0.151 | [0.145, 0.157] |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | -0.024 | [-0.029, -0.019] |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | +0.166 | [0.160, 0.172] |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | +0.007 | [0.006, 0.008] |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | +0.062 | [0.059, 0.065] |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | -0.001 | [-0.003, 0.001] |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | +0.045 | [0.041, 0.048] |
| macro average | direct - no_review | exact_match_line_trim | +0.046 | [0.043, 0.048] |
| macro average | direct - no_review | location_overlap_f1 | +0.106 | [0.103, 0.110] |
| macro average | gold_location - direct | exact_match_line_trim | -0.012 | [-0.015, -0.010] |
| macro average | gold_location - direct | location_overlap_f1 | +0.105 | [0.102, 0.109] |

## 해석

1. `direct` 조건은 두 모델 모두에서 `no_review`보다 좋았다. 즉, 리뷰 코멘트는 snippet-level repair에서 모델의 수정 행동을 유의미하게 바꾼다.
2. `gold_location` 조건은 두 모델 모두에서 location overlap F1을 개선했다. 이는 within-snippet localisation 정보가 실제로 위치 중첩을 올린다는 점을 보여준다.
3. 그러나 `gold_location`은 exact match를 안정적으로 개선하지 않았다. `qwen2.5-coder:7b`에서는 direct보다 exact match가 낮아졌고, `deepseek-coder:6.7b`에서는 차이가 거의 없으며 bootstrap CI가 0을 포함한다.
4. 따라서 이 결과는 "localisation이 병목의 일부이지만, 올바른 위치를 아는 것만으로 정확한 repair가 보장되지는 않는다"는 진단적 결론을 지지한다.

## 논문/보고서에 쓸 수 있는 문장

Full-data results on 14,855 CodeReview-New snippets show that review comments improve both exact repair and location overlap over the no-review baseline for both local code LLMs. Gold-location hints further improve location overlap, but this localisation gain does not translate into higher exact-match repair accuracy. This supports the diagnostic framing that within-snippet localisation is an important bottleneck, but not a sufficient condition for correct review-to-repair generation.

## 주의사항

- 이 결과는 CodeReview-New의 snippet/hunk-level 설정에서의 within-snippet localisation 결과다.
- full-file localisation 결과로 해석하면 안 된다.
- `direct comment-to-patch` 자체를 novelty로 주장하면 안 된다.
- `codegemma:7b`는 이 2-model full result에 포함되지 않았다.
- `starcoder2:7b`는 현재 Ollama chat backend에서 빈 출력 문제가 있어 main metric과 macro average에서 제외했다.

## 주요 산출물

- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/summary.md`
- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/paper_results_table.csv`
- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/bootstrap_gains_by_model.csv`
- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/integrity_report.csv`
- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/output_length_diagnostics.csv`
- `results/multi_model_r2r_all_seed42_full_w6_np512_20260429/truncation_risk_cases.csv`
