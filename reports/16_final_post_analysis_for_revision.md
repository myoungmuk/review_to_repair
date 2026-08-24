# Final Post-analysis for Revision

## 1. Main conclusion

The completed 3-model run supports the central claim that review comments improve both exact repair and localization, while gold location markers improve localization but do not reliably improve exact repair. The strongest example is `qwen2.5-coder:32b`: direct exact is 12.08%, gold_location exact is 4.18%, direct location F1 is 65.30%, and gold_location location F1 is 70.07%.

## 2. What the 32B result changes

For Qwen 32B, direct-correct -> gold-location-wrong cases are 1425 while direct-wrong -> gold-location-correct cases are 251. The net exact change is -1174 examples (-7.90 pp). This makes the location-vs-repair gap stronger than in the 7B-only framing.

## 3. Bootstrap CI summary

| model | comparison | metric | paired_n | gain_decimal | ci95_low_decimal | ci95_high_decimal | gain_percentage_points |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 14855 | 0.0843487041400202 | 0.07983843823628407 | 0.0889262874453046 | 8.43487041400202 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 14855 | 0.15083185992394796 | 0.14451005370928308 | 0.1570336398267594 | 15.083185992394796 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 14855 | -0.023964994951194883 | -0.028948165600807808 | -0.018643554358801755 | -2.3964994951194885 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 14855 | 0.16599858496904307 | 0.15991715581152205 | 0.17187513557248177 | 16.599858496904307 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 14855 | 0.006866374957926624 | 0.00558734432850892 | 0.008347357791989229 | 0.6866374957926624 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 14855 | 0.06174679970186774 | 0.05883661302439131 | 0.06467596446961033 | 6.174679970186774 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 14855 | -0.0009424436216762033 | -0.0027600134634803096 | 0.0006748569505217084 | -0.09424436216762033 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 14855 | 0.04470254719451219 | 0.04137690365308379 | 0.047974409463389676 | 4.470254719451219 |
| qwen2.5-coder:32b | direct - no_review | exact_match_line_trim | 14855 | 0.1127566475934029 | 0.10770784247728038 | 0.11787277011107371 | 11.27566475934029 |
| qwen2.5-coder:32b | direct - no_review | location_overlap_f1 | 14855 | 0.25593766216533437 | 0.249715998288202 | 0.26185409935014764 | 25.593766216533435 |
| qwen2.5-coder:32b | gold_location - direct | exact_match_line_trim | 14855 | -0.07903062941770447 | -0.0843503870750589 | -0.07398014136654325 | -7.903062941770448 |
| qwen2.5-coder:32b | gold_location - direct | location_overlap_f1 | 14855 | 0.04767572093087501 | 0.042252832979352936 | 0.05357209470161003 | 4.767572093087501 |
| macro_average | direct - no_review | exact_match_line_trim | 14855 | 0.06799057556378324 | 0.06565634466509593 | 0.07045944126556715 | 6.799057556378324 |
| macro_average | direct - no_review | location_overlap_f1 | 14855 | 0.1561721072637167 | 0.15317821950154348 | 0.15941036619573468 | 15.617210726371669 |
| macro_average | gold_location - direct | exact_match_line_trim | 14855 | -0.034646022663525185 | -0.03709525412319085 | -0.03224391338494335 | -3.4646022663525184 |
| macro_average | gold_location - direct | location_overlap_f1 | 14855 | 0.08612561769814342 | 0.08304469981956032 | 0.08916674006491751 | 8.612561769814342 |

## 4. Qwen 32B flip analysis

- direct correct -> gold wrong: 1425
- direct wrong -> gold correct: 251
- both correct: 370
- both wrong: 12809
- degraded cases with gold location F1 = 1.0: 896 (62.88%)
- degraded cases with gold location F1 >= 0.8: 936 (65.68%)
- over-edit suspects among degraded cases: 528 (37.05%)
- under-edit suspects among degraded cases: 0 (0.00%)

## 5. Output-format sensitivity

| scenario | paired_n | removed_pair_count | direct_exact | gold_location_exact | gold_minus_direct_exact | direct_location_f1 | gold_location_f1 | gold_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_cases | 14855 | 0 | 0.12083473577919893 | 0.041804106361494446 | -0.07903062941770447 | 0.6530348599133433 | 0.7007105808442183 | 0.04767572093087502 |
| without_unclosed_code_fence | 13956 | 899 | 0.1261822871883061 | 0.04335053023789051 | -0.08283175695041559 | 0.6627062916726116 | 0.7019632721372545 | 0.03925698046464288 |
| without_near_generation_cap | 14009 | 846 | 0.12606181740309802 | 0.043186522949532444 | -0.08287529445356558 | 0.6626794749937637 | 0.7014920280208853 | 0.03881255302712161 |
| without_marker_echo | 14811 | 44 | 0.12119370737965025 | 0.041928296536358114 | -0.07926541084329214 | 0.6534334036888093 | 0.7009311471312488 | 0.04749774344243951 |
| without_any_suspicious_output_flag | 11918 | 2937 | 0.11486826648766571 | 0.04489008222856184 | -0.06997818425910388 | 0.6635504857796771 | 0.7009219958567403 | 0.037371510077063186 |

## 6. Diff-type analysis

| model | diff_type | example_count | direct_exact | gold_location_exact | gold_location_minus_direct_exact | direct_location_f1 | gold_location_location_f1 | gold_location_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| macro_average | replace_only | 10690 | 0.07452447770502027 | 0.009978172747115684 | -0.06454630495790457 | 0.5510871711586399 | 0.6338139828715945 | 0.0827268117129546 |
| macro_average | insert_only | 1121 | 0.0008920606601248885 | 0.0 | -0.0008920606601248885 | 0.29439097162181976 | 0.40221240346585135 | 0.1078214318440316 |
| macro_average | delete_only | 1503 | 0.18673763583943226 | 0.30627633621645595 | 0.11953870037702373 | 0.5800231125171286 | 0.655038331053289 | 0.0750152185361604 |
| macro_average | mixed | 1541 | 0.0025957170668397147 | 0.0004326195111399524 | -0.002163097555699762 | 0.5116992797819174 | 0.6164564083590927 | 0.10475712857717519 |

## 7. Length/complexity analysis

The full length/complexity table is in `results/tables/table_length_complexity_analysis.csv`. A Qwen 32B subset is shown below for revision triage.

| model | feature | bin | n | direct_exact | gold_location_exact | gold_minus_direct_exact | direct_location_f1 | gold_location_location_f1 | gold_minus_direct_location_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | old_snippet_line_count | q4_gt_11 | 3383 | 0.054389595033993494 | 0.04167898315104936 | -0.012710611882944131 | 0.6361511641785472 | 0.7269575804890468 | 0.09080641631049957 |
| qwen2.5-coder:32b | old_snippet_line_count | q3_8_to_11 | 3176 | 0.08532745591939547 | 0.05415617128463476 | -0.03117128463476071 | 0.6545571242873621 | 0.7315305680350502 | 0.07697344374768811 |
| qwen2.5-coder:32b | old_snippet_line_count | q1_le_8 | 8296 | 0.16152362584378013 | 0.03712632594021215 | -0.12439729990356799 | 0.6593370333727132 | 0.6782084256951663 | 0.01887139232245305 |
| qwen2.5-coder:32b | number_changed_spans | q4_gt_1 | 3613 | 0.024633268751729866 | 0.012178245225574315 | -0.01245502352615555 | 0.5957456604058791 | 0.6762438548274045 | 0.08049819442152539 |
| qwen2.5-coder:32b | number_changed_spans | q1_le_1 | 11242 | 0.1517523572318093 | 0.0513253869418253 | -0.100426970289984 | 0.6714466974707592 | 0.7085737974514723 | 0.03712709998071306 |
| qwen2.5-coder:32b | gold_location_output_char_count | q4_gt_473 | 3700 | 0.05540540540540541 | 0.00972972972972973 | -0.04567567567567568 | 0.6344505457217338 | 0.737090217089821 | 0.10263967136808727 |
| qwen2.5-coder:32b | gold_location_output_char_count | q1_le_262 | 3754 | 0.16409163558870538 | 0.08364411294619073 | -0.08044752264251465 | 0.6145137553627131 | 0.6301342577985111 | 0.015620502435797934 |
| qwen2.5-coder:32b | gold_location_output_char_count | q3_353_to_473 | 3717 | 0.11030400860909335 | 0.026096314231907454 | -0.0842076943771859 | 0.6816552822498175 | 0.7362839752031749 | 0.05462869295335737 |
| qwen2.5-coder:32b | gold_location_output_char_count | q2_262_to_353 | 3684 | 0.15309446254071662 | 0.04723127035830619 | -0.10586319218241044 | 0.6820761409033941 | 0.7001982452776098 | 0.018122104374215686 |

## 8. Manual audit sample summary

Manual audit sample generated: 180 rows.

| audit_category | count |
| --- | --- |
| direct_wrong_to_gold_correct | 30 |
| gold_location_f1_1_exact_wrong | 50 |
| qwen32b_direct_correct_to_gold_wrong | 50 |
| qwen7b_direct_correct_to_gold_wrong | 30 |
| random_exact_wrong_pair | 20 |

## 9. Recommended paper wording

Across three local code LLMs and 14,855 CodeReview-New examples, review comments consistently improved both exact repair and location overlap over the no-review setting. In contrast, gold changed-location markers further improved location overlap but did not translate into higher exact repair accuracy; for the 32B Qwen model, exact match dropped from 12.08% in the direct condition to 4.18% with gold-location markers while location F1 increased from 65.30% to 70.07%. This suggests that, in snippet-level Review-to-Repair, knowing where to edit and generating the correct edit remain distinct capabilities.

## 10. Claims to avoid

- Do not claim gold location is harmful in all repair settings; this is snippet-level CodeReview-New with this prompt/post-processing setup.
- Do not claim full-file localization was solved or evaluated.
- Do not claim commercial closed models will show the same behavior.
- Do not treat location F1 gains as exact repair success.
- Do not hide output-format/truncation-risk sensitivity; report whether the exact drop persists after flagged-case removal.
