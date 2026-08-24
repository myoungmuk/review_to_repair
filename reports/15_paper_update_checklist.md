# Paper Update Checklist

This checklist scans the available `gpt-shared` paper files for stale 2-model wording and expected 3-model wording.

## Inspected Files
- /cephfs/lab/users/2022810001/gpt-shared/.ipynb_checkpoints/folder_path-checkpoint.txt
- /cephfs/lab/users/2022810001/gpt-shared/folder_path.txt
- /cephfs/lab/users/2022810001/gpt-shared/poseidon_remote_gui_migration_summary (1).txt
- /cephfs/lab/users/2022810001/gpt-shared/poseidon_remote_gui_migration_summary.txt
- /cephfs/lab/users/2022810001/gpt-shared/.ipynb_checkpoints/심사용 논문_최종-checkpoint.pdf
- /cephfs/lab/users/2022810001/gpt-shared/심사용 논문_최종.pdf

## Notes
- No extraction notes.

## Pattern Check
| type | pattern | found | count |
| --- | --- | --- | --- |
| stale_expression | 두 로컬 코드 LLM | True | 10 |
| stale_expression | 두 모델 | True | 6 |
| stale_expression | 2모델 평균 | False | 0 |
| stale_expression | 89,130개 출력 | True | 2 |
| stale_expression | 7B 수준의 두 로컬 모델에 한정 | False | 0 |
| stale_expression | no_review exact 0.003 | False | 0 |
| stale_expression | direct exact 0.049 | False | 0 |
| stale_expression | gold_location exact 0.036 | False | 0 |
| stale_expression | direct F1 0.469 | False | 0 |
| stale_expression | gold F1 0.575 | False | 0 |
| stale_expression | 0.003 | True | 6 |
| stale_expression | 0.049 | True | 10 |
| stale_expression | 0.036 | True | 6 |
| stale_expression | 0.469 | True | 8 |
| stale_expression | 0.575 | True | 6 |
| replacement_expression | 세 로컬 코드 LLM | False | 0 |
| replacement_expression | 두 7B급 모델과 하나의 32B 모델 | False | 0 |
| replacement_expression | 3모델 macro average | False | 0 |
| replacement_expression | 133,695개 출력 | False | 0 |
| replacement_expression | 상용 폐쇄형 모델과 다른 모델 family로의 일반화는 추가 검증 필요 | False | 0 |

## Final PDF Only
| pattern | found_in_final_pdf | final_pdf_count |
| --- | --- | --- |
| 두 로컬 코드 LLM | True | 5 |
| 두 모델 | True | 3 |
| 2모델 평균 | False | 0 |
| 89,130개 출력 | True | 1 |
| 7B 수준의 두 로컬 모델에 한정 | False | 0 |
| no_review exact 0.003 | False | 0 |
| direct exact 0.049 | False | 0 |
| gold_location exact 0.036 | False | 0 |
| direct F1 0.469 | False | 0 |
| gold F1 0.575 | False | 0 |
| 0.003 | True | 3 |
| 0.049 | True | 5 |
| 0.036 | True | 3 |
| 0.469 | True | 4 |
| 0.575 | True | 3 |
| 세 로컬 코드 LLM | False | 0 |
| 두 7B급 모델과 하나의 32B 모델 | False | 0 |
| 3모델 macro average | False | 0 |
| 133,695개 출력 | False | 0 |
| 상용 폐쇄형 모델과 다른 모델 family로의 일반화는 추가 검증 필요 | False | 0 |

## Required Update Targets
- Replace 2-model framing with 3-model framing.
- Replace `89,130` outputs with `133,695` outputs.
- Replace old 2-model macro-average numbers with the 3-model macro-average values from `results/tables/table_bootstrap_ci_3model_final.csv` and `results/tables/table_diff_type_analysis_3model_final.csv` as appropriate.
- Add a limitation that generalization to commercial closed models and other model families still requires validation.
