# Bootstrap CI Final

- Source: completed 3-model full-data run.
- Bootstrap: paired percentile bootstrap, iterations=1000, seed=42.
- This table includes three models plus the 3-model macro average. No 2-model macro rows are included.

| model | comparison | metric | n | gain | 95% CI | gain pp | 95% CI pp |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 14855 | 0.084349 | [0.079838, 0.088926] | 8.43 | [7.98, 8.89] |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 14855 | 0.150832 | [0.144510, 0.157034] | 15.08 | [14.45, 15.70] |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 14855 | -0.023965 | [-0.028948, -0.018644] | -2.40 | [-2.89, -1.86] |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 14855 | 0.165999 | [0.159917, 0.171875] | 16.60 | [15.99, 17.19] |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 14855 | 0.006866 | [0.005587, 0.008347] | 0.69 | [0.56, 0.83] |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 14855 | 0.061747 | [0.058837, 0.064676] | 6.17 | [5.88, 6.47] |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 14855 | -0.000942 | [-0.002760, 0.000675] | -0.09 | [-0.28, 0.07] |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 14855 | 0.044703 | [0.041377, 0.047974] | 4.47 | [4.14, 4.80] |
| qwen2.5-coder:32b | direct - no_review | exact_match_line_trim | 14855 | 0.112757 | [0.107708, 0.117873] | 11.28 | [10.77, 11.79] |
| qwen2.5-coder:32b | direct - no_review | location_overlap_f1 | 14855 | 0.255938 | [0.249716, 0.261854] | 25.59 | [24.97, 26.19] |
| qwen2.5-coder:32b | gold_location - direct | exact_match_line_trim | 14855 | -0.079031 | [-0.084350, -0.073980] | -7.90 | [-8.44, -7.40] |
| qwen2.5-coder:32b | gold_location - direct | location_overlap_f1 | 14855 | 0.047676 | [0.042253, 0.053572] | 4.77 | [4.23, 5.36] |
| macro_average | direct - no_review | exact_match_line_trim | 14855 | 0.067991 | [0.065656, 0.070459] | 6.80 | [6.57, 7.05] |
| macro_average | direct - no_review | location_overlap_f1 | 14855 | 0.156172 | [0.153178, 0.159410] | 15.62 | [15.32, 15.94] |
| macro_average | gold_location - direct | exact_match_line_trim | 14855 | -0.034646 | [-0.037095, -0.032244] | -3.46 | [-3.71, -3.22] |
| macro_average | gold_location - direct | location_overlap_f1 | 14855 | 0.086126 | [0.083045, 0.089167] | 8.61 | [8.30, 8.92] |
