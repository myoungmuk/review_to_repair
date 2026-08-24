# Output Format And Truncation Sensitivity

Near generation cap is defined as `raw_output` length >= 1792 characters, matching the existing run diagnostic heuristic (`num_predict * 3.5`).
`any_suspicious_output_flag` removes pairs where either direct or gold_location has unclosed fence, near-cap output, marker echo, wrapper text, empty extracted output, suspiciously long output, or suspiciously short output. Extraction method flags are reported but are not treated as suspicious by themselves.

## Flag Counts
| model | condition | n_output | unclosed_code_fence_count | near_generation_cap_count | marker_echo_count | wrapper_text_count | extraction_by_fenced_code_block_count | extraction_by_raw_output_count | empty_extracted_output_count | suspiciously_long_output_count | suspiciously_short_output_count | any_suspicious_output_flag_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 14855 | 29 | 2 | 0 | 2 | 14855 | 0 | 0 | 18 | 8 | 57 |
| qwen2.5-coder:7b | direct | 14855 | 31 | 1 | 0 | 2 | 14855 | 0 | 0 | 16 | 1 | 51 |
| qwen2.5-coder:7b | gold_location | 14855 | 31 | 4 | 4811 | 6 | 14853 | 2 | 0 | 16 | 5 | 4859 |
| deepseek-coder:6.7b | no_review | 14855 | 242 | 280 | 0 | 2062 | 14855 | 0 | 0 | 2508 | 3 | 4211 |
| deepseek-coder:6.7b | direct | 14855 | 123 | 12 | 0 | 848 | 14855 | 0 | 0 | 162 | 9 | 1096 |
| deepseek-coder:6.7b | gold_location | 14855 | 189 | 2 | 2052 | 925 | 14831 | 24 | 0 | 43 | 9 | 3072 |
| qwen2.5-coder:32b | no_review | 14855 | 3171 | 3322 | 0 | 5471 | 14855 | 0 | 0 | 4427 | 2 | 6863 |
| qwen2.5-coder:32b | direct | 14855 | 789 | 754 | 0 | 2492 | 14855 | 0 | 0 | 845 | 3 | 2718 |
| qwen2.5-coder:32b | gold_location | 14855 | 159 | 122 | 44 | 243 | 14855 | 0 | 0 | 152 | 6 | 394 |

## Qwen 32B Sensitivity
| scenario | paired_n | removed_pair_count | direct_exact | gold_location_exact | gold_minus_direct_exact | direct_location_f1 | gold_location_f1 | gold_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_cases | 14855 | 0 | 0.1208 | 0.0418 | -0.0790 | 0.6530 | 0.7007 | 0.0477 |
| without_unclosed_code_fence | 13956 | 899 | 0.1262 | 0.0434 | -0.0828 | 0.6627 | 0.7020 | 0.0393 |
| without_near_generation_cap | 14009 | 846 | 0.1261 | 0.0432 | -0.0829 | 0.6627 | 0.7015 | 0.0388 |
| without_marker_echo | 14811 | 44 | 0.1212 | 0.0419 | -0.0793 | 0.6534 | 0.7009 | 0.0475 |
| without_any_suspicious_output_flag | 11918 | 2937 | 0.1149 | 0.0449 | -0.0700 | 0.6636 | 0.7009 | 0.0374 |

## All Models
| scenario | model | paired_n | removed_pair_count | gold_minus_direct_exact | gold_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- |
| all_cases | qwen2.5-coder:7b | 14855 | 0 | -0.0240 | 0.1660 |
| all_cases | deepseek-coder:6.7b | 14855 | 0 | -0.0009 | 0.0447 |
| all_cases | qwen2.5-coder:32b | 14855 | 0 | -0.0790 | 0.0477 |
| all_cases | macro_average | 14855 | 0 | -0.0346 | 0.0861 |
| without_unclosed_code_fence | qwen2.5-coder:7b | 14813 | 42 | -0.0242 | 0.1663 |
| without_unclosed_code_fence | deepseek-coder:6.7b | 14578 | 277 | -0.0010 | 0.0450 |
| without_unclosed_code_fence | qwen2.5-coder:32b | 13956 | 899 | -0.0828 | 0.0393 |
| without_unclosed_code_fence | macro_average | 13956 | 1218 | -0.0360 | 0.0835 |
| without_near_generation_cap | qwen2.5-coder:7b | 14851 | 4 | -0.0240 | 0.1659 |
| without_near_generation_cap | deepseek-coder:6.7b | 14841 | 14 | -0.0009 | 0.0447 |
| without_near_generation_cap | qwen2.5-coder:32b | 14009 | 846 | -0.0829 | 0.0388 |
| without_near_generation_cap | macro_average | 14009 | 864 | -0.0359 | 0.0832 |
| without_marker_echo | qwen2.5-coder:7b | 10044 | 4811 | 0.0029 | 0.1489 |
| without_marker_echo | deepseek-coder:6.7b | 12803 | 2052 | 0.0003 | 0.0438 |
| without_marker_echo | qwen2.5-coder:32b | 14811 | 44 | -0.0793 | 0.0475 |
| without_marker_echo | macro_average | 10044 | 6907 | -0.0254 | 0.0800 |
| without_any_suspicious_output_flag | qwen2.5-coder:7b | 9981 | 4874 | 0.0026 | 0.1493 |
| without_any_suspicious_output_flag | deepseek-coder:6.7b | 11093 | 3762 | -0.0006 | 0.0441 |
| without_any_suspicious_output_flag | qwen2.5-coder:32b | 11918 | 2937 | -0.0700 | 0.0374 |
| without_any_suspicious_output_flag | macro_average | 9981 | 11573 | -0.0227 | 0.0769 |
