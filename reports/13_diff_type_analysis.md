# Diff-Type Analysis

Diff type is computed from the gold `old` -> `new` snippet using line-level `SequenceMatcher` opcodes.

| model | diff_type | example_count | no_review_exact | direct_exact | gold_location_exact | direct_minus_no_review_exact | gold_location_minus_direct_exact | no_review_location_f1 | direct_location_f1 | gold_location_location_f1 | direct_minus_no_review_location_f1 | gold_location_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | replace_only | 10690 | 0.0057 | 0.0977 | 0.0294 | 0.0920 | -0.0683 | 0.3743 | 0.5584 | 0.7214 | 0.1841 | 0.1630 |
| qwen2.5-coder:7b | insert_only | 1121 | 0.0000 | 0.0009 | 0.0000 | 0.0009 | -0.0009 | 0.2516 | 0.2785 | 0.4749 | 0.0269 | 0.1963 |
| qwen2.5-coder:7b | delete_only | 1503 | 0.0213 | 0.1983 | 0.4498 | 0.1770 | 0.2515 | 0.4495 | 0.5825 | 0.7230 | 0.1330 | 0.1405 |
| qwen2.5-coder:7b | mixed | 1541 | 0.0000 | 0.0019 | 0.0000 | 0.0019 | -0.0019 | 0.4516 | 0.4789 | 0.6686 | 0.0273 | 0.1897 |
| deepseek-coder:6.7b | replace_only | 10690 | 0.0000 | 0.0070 | 0.0003 | 0.0070 | -0.0067 | 0.3274 | 0.4010 | 0.4416 | 0.0736 | 0.0406 |
| deepseek-coder:6.7b | insert_only | 1121 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2603 | 0.2623 | 0.2934 | 0.0020 | 0.0311 |
| deepseek-coder:6.7b | delete_only | 1503 | 0.0027 | 0.0206 | 0.0592 | 0.0180 | 0.0386 | 0.4260 | 0.4793 | 0.5462 | 0.0533 | 0.0670 |
| deepseek-coder:6.7b | mixed | 1541 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.4538 | 0.4849 | 0.5461 | 0.0311 | 0.0612 |
| qwen2.5-coder:32b | replace_only | 10690 | 0.0057 | 0.1189 | 0.0003 | 0.1132 | -0.1186 | 0.3893 | 0.6938 | 0.7384 | 0.3045 | 0.0446 |
| qwen2.5-coder:32b | insert_only | 1121 | 0.0000 | 0.0018 | 0.0000 | 0.0018 | -0.0018 | 0.2490 | 0.3424 | 0.4384 | 0.0934 | 0.0960 |
| qwen2.5-coder:32b | delete_only | 1503 | 0.0379 | 0.3413 | 0.4098 | 0.3034 | 0.0685 | 0.4671 | 0.6782 | 0.6958 | 0.2111 | 0.0176 |
| qwen2.5-coder:32b | mixed | 1541 | 0.0013 | 0.0058 | 0.0013 | 0.0045 | -0.0045 | 0.4906 | 0.5714 | 0.6347 | 0.0808 | 0.0633 |
| macro_average | replace_only | 10690 | 0.0038 | 0.0745 | 0.0100 | 0.0707 | -0.0645 | 0.3637 | 0.5511 | 0.6338 | 0.1874 | 0.0827 |
| macro_average | insert_only | 1121 | 0.0000 | 0.0009 | 0.0000 | 0.0009 | -0.0009 | 0.2536 | 0.2944 | 0.4022 | 0.0408 | 0.1078 |
| macro_average | delete_only | 1503 | 0.0206 | 0.1867 | 0.3063 | 0.1661 | 0.1195 | 0.4475 | 0.5800 | 0.6550 | 0.1325 | 0.0750 |
| macro_average | mixed | 1541 | 0.0004 | 0.0026 | 0.0004 | 0.0022 | -0.0022 | 0.4653 | 0.5117 | 0.6165 | 0.0464 | 0.1048 |
