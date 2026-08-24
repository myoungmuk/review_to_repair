# Qwen 32B Flip Analysis

Scope: paired `direct` vs `gold_location` rows for `qwen2.5-coder:32b`.

- Total pairs: 14855
- direct correct -> gold_location wrong: 1425 (9.59%)
- direct wrong -> gold_location correct: 251 (1.69%)
- both correct: 370
- both wrong: 12809
- Net exact change: -1174 examples (-7.90 pp)

Among direct-correct -> gold-location-wrong cases:
- gold_location location F1 = 1.0: 896 (62.88%)
- gold_location location F1 >= 0.8: 936 (65.68%)
- Over-edit suspect: 528 (37.05%)
- Under-edit suspect: 0 (0.00%)

All-model flip table:

| model | total_pairs | direct_correct_gold_wrong | direct_wrong_gold_correct | direct_correct_gold_correct | direct_wrong_gold_wrong | net_exact_change_count | net_exact_change_rate | dc_gw_gold_loc_f1_eq_1_count | dc_gw_gold_loc_f1_ge_0_8_count | dc_gw_over_edit_suspect_count | dc_gw_under_edit_suspect_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 14855 | 933 | 577 | 413 | 12932 | -356 | -0.0240 | 611 | 635 | 298 | 8 |
| deepseek-coder:6.7b | 14855 | 87 | 73 | 19 | 14676 | -14 | -0.0009 | 39 | 41 | 45 | 0 |
| qwen2.5-coder:32b | 14855 | 1425 | 251 | 370 | 12809 | -1174 | -0.0790 | 896 | 936 | 528 | 0 |
