# Codex JupyterLab Continuation Prompt

이 문서는 연구 파일을 다른 기기나 JupyterLab 환경으로 옮긴 뒤, 새 Codex 세션에 그대로 붙여 넣어 사용할 수 있는 이어받기용 설명과 프롬프트다.

## 0. 최신 상태 요약

2026-04-27 현재, `--num-predict 1024` full run이 완료됐다.

최종 결과:

```text
results/multi_model_r2r_seed42_np1024
```

최종 결과 정리 문서:

```text
docs/multi_model_r2r_np1024_full_results_2026-04-27.md
```

최종 integrity:

- 900/900 outputs
- generation error 0
- extraction failure 0
- evaluation failure 0
- valid evaluation 900
- near generation cap risk 0

이 문서 아래쪽에는 full run 전 단계의 지시가 일부 남아 있다. 새 세션에서는
먼저 위 최종 결과 문서와 `docs/multi_model_r2r_handoff.md`를 기준으로 삼아라.

## 1. 이 저장소의 현재 구조

이 저장소는 CodeReview-New 100개 예제에 대해 Review-to-Repair 조건별 수정을 생성하고 평가하는 실험 저장소다.

핵심 흐름은 다음과 같다.

```text
data/processed/crn_pilot100.jsonl
  -> prompts/crn_pilot100/*_prompts.jsonl
  -> scripts/run_multi_model_r2r.py
  -> results/<run_name>/generations/<model>/<condition>.jsonl
  -> metrics / bootstrap gains / integrity report / summary
```

중요한 파일과 디렉터리:

```text
configs/
  multi_model_r2r_seed42.json
    - multi-model 실험 설정 파일
    - seed=42, CodeReview-New 100개, 세 조건, 세 모델 설정

data/processed/
  crn_pilot100.jsonl
    - seed=42 CodeReview-New 100개 예제

prompts/crn_pilot100/
  no_review_prompts.jsonl
  direct_prompts.jsonl
  gold_location_prompts.jsonl
    - 현재 main experiment가 사용하는 프롬프트

scripts/
  run_multi_model_r2r.py
    - 새로 만든 multi-model 실행/후처리/평가/집계 스크립트
  run_local_predictions.py
    - 기존 local Ollama prediction runner, num_predict 지원 추가됨
  common.py
    - 데이터 로딩 및 location_overlap_f1 계산 관련 공통 코드
  evaluate_predictions.py
    - exact_match_line_trim 평가 코드
  bootstrap_gain.py
    - 기존 bootstrap gain 계산 참고 코드

results/
  multi_model_r2r_seed42_np1024/
    - 최종 3모델 x 3조건 x 100예제 full run 결과
    - 900/900 valid, generation/extraction/evaluation error 0
  multi_model_r2r_seed42_smoke10_all3_np512/
    - qwen, deepseek, codegemma 3모델을 같은 --num-predict 512로 돌린 clean smoke 결과
    - smoke는 통과했지만 deepseek 일부 truncation 위험 플래그가 있음

docs/
  multi_model_r2r_handoff.md
    - 지금까지의 상세 인수인계서
  codex_jupyterlab_continuation_prompt.md
    - 지금 보고 있는 JupyterLab/Codex 이어받기 문서
  multi_model_r2r_research_status_2026-04-27.md
    - 현재 머신에서의 연구 진행 상태와 모델 pull blocker 기록
  multi_model_r2r_paper_integration_plan.md
    - 최신 KCC2026 PDF 기준 multi-model 결과를 논문에 반영하는 계획
  multi_model_r2r_np1024_full_results_2026-04-27.md
    - 최종 full run 결과 요약과 논문용 표
```

주의:

- IDE에 열려 있던 `prompts/crn_pilot100_seed7/direct_prompts.jsonl`는 현재 main config 경로가 아니다.
- main multi-model experiment는 `prompts/crn_pilot100`와 `data/processed/crn_pilot100.jsonl`를 사용한다.
- JupyterLab에서 어느 폴더를 열었는지에 따라 repo root가 한 단계 다를 수 있다. 먼저 `pwd`, `ls`, `rg --files docs configs scripts`로 위치를 확인하고, 필요한 경우 `cd review_to_repair_crn` 후 진행한다.

## 2. 지금까지 한 일

기존 실험은 단일 모델 파일럿이었다.

- 데이터: CodeReview-New 100개 예제
- seed: 42
- 모델: `qwen2.5-coder:7b`
- 조건: `no_review`, `direct`, `gold_location`
- 평가: `exact_match_line_trim`, `location_overlap_f1`

이번 작업에서 한 일:

- 기존 조건, 데이터, 평가 지표는 바꾸지 않았다.
- 모델만 확장해서 다중 코드 LLM 진단 실험으로 만들었다.
- main model set을 다음 3개로 확정했다.
  - `qwen2.5-coder:7b`
  - `deepseek-coder:6.7b`
  - `codegemma:7b`
- `starcoder2:7b`는 제외했다.
  - 이유: 현재 Ollama chat backend에서 대부분 빈 출력 `"\n"`을 반환했다.
  - 이는 R2R 성능 문제가 아니라 모델-백엔드 호출 호환성 문제로 처리했다.
- `qwen2.5-coder:3b`는 fallback 후보로만 기록했다.
- `scripts/run_multi_model_r2r.py`를 만들어 모델별/조건별 실행, 후처리, 평가, bootstrap, integrity report, paper table 생성을 한 번에 하게 했다.
- 기존 qwen pilot 결과를 clean multi-model run에서 자동 재사용하지 않도록 설정했다.
- 3모델 x 3조건 x 10예제 clean smoke를 수행했다.

## 3. Clean Smoke 결과 요약

최근 clean smoke:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np512 \
  --num-predict 512 \
  --resume \
  --continue-on-error
```

결과:

- 총 출력 수: 90
- 구조: 3 models x 3 conditions x 10 examples
- 모든 모델/조건에서 output count 10
- generation error 0
- extraction failure 0
- evaluation failure 0
- old qwen pilot 결과 재사용 없음
- `generation_source=backend`가 90개 출력 모두에서 확인됨

하지만:

- `deepseek-coder:6.7b` 일부 출력에서 unclosed code fence와 near generation cap 위험 플래그가 있었다.
- 따라서 `--num-predict 512`로 바로 full run을 시작하지 않는 것이 좋다.
- 다음 단계는 같은 3모델에 대해 `--num-predict 768` 또는 `--num-predict 1024` smoke를 다시 수행하는 것이다.

## 4. 앞으로 해야 할 일

JupyterLab 또는 데스크톱에서 이어갈 때의 순서:

1. 저장소가 제대로 옮겨졌는지 확인한다.
2. 현재 작업 디렉터리가 repo root인지 확인한다.
3. `docs/multi_model_r2r_handoff.md`를 읽는다.
4. `configs/multi_model_r2r_seed42.json`을 확인한다.
5. `ollama list`로 세 main 모델이 설치되어 있는지 확인한다.
6. 모델이 없으면 자동 pull하지 말고 필요한 `ollama pull ...` 명령 목록을 사용자에게 보고한다.
7. 사용자가 승인하면 누락 모델을 수동으로 pull한다.
8. full run 전에 shared generation cap으로 10-example smoke를 다시 수행한다.
9. smoke 결과에서 다음을 확인한다.
   - 각 model x condition output count
   - generation error 수
   - extraction failure 수
   - evaluation failure 수
   - exact 평균
   - location_overlap_f1 평균
   - bootstrap gain
   - `generation_source=backend` 여부
   - truncation/empty-output risk
10. truncation 위험이 없으면 full run 명령을 제시한다.
11. 사용자가 명시적으로 승인하기 전에는 full run을 실행하지 않는다.

권장 smoke 명령:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

더 보수적인 smoke:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

smoke 후 반드시 확인할 파일:

```text
results/<smoke_run>/summary.md
results/<smoke_run>/integrity_report.csv
results/<smoke_run>/metrics_by_model_condition.csv
results/<smoke_run>/bootstrap_gains_by_model.csv
results/<smoke_run>/truncation_risk_cases.csv
results/<smoke_run>/all_generations.jsonl
```

smoke가 통과한 뒤 사용자 승인 후 full run:

```bash
python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np768 \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

또는 1024를 선택했다면:

```bash
python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np1024 \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

full run 예상 출력 수:

```text
3 models x 3 conditions x 100 examples = 900 outputs
```

## 5. 다음 Codex에게 붙여 넣을 프롬프트

아래 프롬프트를 JupyterLab 또는 새 데스크톱 Codex 세션에 그대로 붙여 넣으면 된다.

```text
너는 이 저장소의 Review-to-Repair 연구 실험을 이어받는 Codex 코딩 에이전트다.

먼저 현재 작업 디렉터리가 repo root인지 확인해라.

다음 명령으로 위치와 파일 구조를 확인해라.

pwd
ls
rg --files docs configs scripts

만약 docs/configs/scripts가 보이지 않고 review_to_repair_crn 디렉터리가 보이면, 먼저 그 디렉터리로 이동한 뒤 진행해라.

그 다음 다음 문서를 읽고 현재 상태를 파악해라.
- docs/multi_model_r2r_handoff.md
- docs/codex_jupyterlab_continuation_prompt.md
- docs/multi_model_r2r_research_status_2026-04-27.md
- docs/multi_model_r2r_paper_integration_plan.md
- configs/multi_model_r2r_seed42.json

연구 목표:
기존 CodeReview-New Review-to-Repair pilot을 단일 모델 파일럿에서 다중 코드 LLM 진단 실험으로 확장한다.
새로운 연구 방향을 만들지 말고 기존 실험 조건을 유지한다.

반드시 유지할 설정:
- 데이터: data/processed/crn_pilot100.jsonl
- seed: 42
- 조건: no_review, direct, gold_location
- 평가 지표: exact_match_line_trim, location_overlap_f1
- 모델 비교: 모델별 조건 비교와 gain 분석

main model set:
- qwen2.5-coder:7b
- deepseek-coder:6.7b
- codegemma:7b

excluded model:
- starcoder2:7b

starcoder2 제외 사유:
- 현재 Ollama chat backend에서 대부분 빈 출력 "\n"을 반환했다.
- 이는 Review-to-Repair 성능 문제가 아니라 모델-백엔드 호출 호환성 문제다.
- starcoder2 결과를 논문용 metrics, macro average, full run에 포함하지 마라.

fallback:
- qwen2.5-coder:3b는 codegemma가 없을 때의 fallback 후보일 뿐이다.
- main full run에는 사용자 승인 없이 사용하지 마라.

현재까지 한 일:
- scripts/run_multi_model_r2r.py를 추가해 multi-model generation/evaluation/aggregation을 지원하게 했다.
- scripts/run_local_predictions.py에 --num-predict 지원을 추가했다.
- configs/multi_model_r2r_seed42.json에 main model set과 excluded model 정보를 기록했다.
- results/multi_model_r2r_seed42_smoke10_all3_np512에서 3모델 x 3조건 x 10예제 clean smoke를 수행했다.
- smoke 결과 generation/extraction/evaluation은 모두 통과했다.
- old qwen pilot 결과는 재사용되지 않았고, generation_source=backend가 확인됐다.
- deepseek 일부 사례에서 truncation risk flag가 있었다.
- 따라서 full run은 아직 하지 말아야 한다.

지금 해야 할 일:
1. 저장소 구조와 위 파일들이 존재하는지 확인해라.
2. ollama list를 실행해서 main 3모델이 설치되어 있는지 확인해라.
3. 모델이 없으면 자동 pull하지 말고 필요한 pull 명령을 보고해라.
4. 사용자가 승인한 경우에만 누락 모델을 pull해라.
5. main 3모델이 모두 있으면 full run 전에 shared cap smoke를 다시 실행해라.
6. 우선 다음 명령을 사용해 10-example smoke를 수행해라.

python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab \
  --num-predict 768 \
  --resume \
  --continue-on-error

7. smoke 후 반드시 다음 실제 생성 파일을 읽고 보고해라.
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/summary.md
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/integrity_report.csv
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/metrics_by_model_condition.csv
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/bootstrap_gains_by_model.csv
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/truncation_risk_cases.csv
- results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab/all_generations.jsonl

8. smoke 후 다음을 보고해라.
- 사용 모델 목록
- 제외 모델 목록과 제외 사유
- model x condition별 output count
- generation error 수
- extraction failure 수
- evaluation failure 수
- exact_match_line_trim 평균
- location_overlap_f1 평균
- bootstrap gain 요약
- generation_source=backend 확인 결과
- truncation risk case 수와 사례
- full run 진행 가능 여부

9. truncation 위험 판단 시 최소한 다음 플래그를 확인해라.
- unclosed_code_fence
- near_num_predict_char_risk
- empty output 또는 whitespace-only output 반복
- extracted_code가 비정상적으로 짧거나 raw_output 끝이 잘린 경우

10. truncation 위험이 남아 있으면 full run을 진행하지 말고 --num-predict 1024 smoke를 제안해라.
11. smoke가 깨끗하게 통과하면 full run 명령만 제시하고, 사용자가 명시적으로 승인하기 전에는 full run을 실행하지 마라.

주의:
- no_review/direct/gold_location 조건 정의를 바꾸지 마라.
- exact_match_line_trim/location_overlap_f1 지표를 바꾸지 마라.
- predicted_location 같은 새 조건을 추가하지 마라.
- 기존 qwen pilot 결과를 clean multi-model run에 자동 재사용하지 마라.
- 실패한 실행은 조용히 무시하지 말고 summary와 integrity report에 남겨라.
- 결과를 지어내지 마라. 실제 생성된 CSV/summary만 보고해라.
```

## 6. 판단 기준

full run을 진행해도 되는 상태:

- 세 main 모델이 모두 설치되어 있다.
- smoke output count가 정확히 90이다.
- generation error가 0이다.
- extraction failure가 0이다.
- evaluation failure가 0이다.
- `generation_source=backend`가 모든 smoke 출력에서 확인됐다.
- truncation risk가 없거나, 결과 해석에 영향을 주지 않는 것으로 실제 출력 검토를 통해 확인됐다.
- 사용자가 full run을 명시적으로 승인했다.

full run을 멈춰야 하는 상태:

- 모델이 하나라도 누락됐다.
- starcoder2가 main model set에 들어갔다.
- output count가 부족하거나 중복 ID가 있다.
- extraction failure가 반복된다.
- deepseek/codegemma/qwen 중 하나에서 empty output이 반복된다.
- `unclosed_code_fence`, `near_num_predict_char_risk`, whitespace-only output 같은 truncation 또는 invalid-output 위험이 여러 사례에서 확인된다.
- 사용자가 아직 full run을 승인하지 않았다.
