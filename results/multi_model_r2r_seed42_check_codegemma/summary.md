# Multi-Model Review-to-Repair Seed42

## Model Check Blocked The Run
Required Ollama model families are not installed; no generations were run.
Installed Ollama models: starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b
Selected models so far: qwen2.5-coder:7b, deepseek-coder:6.7b
Missing required families:
- codegemma_7b: candidates=codegemma:7b
  suggested pull: ollama pull codegemma:7b

No generation was started. Install one model from each missing family, then rerun:

```bash
python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024
```

Installed Ollama models observed:
- starcoder2:7b
- deepseek-coder:6.7b
- qwen2.5-coder:3b
- qwen2.5-coder:7b

Configured candidate families:
- current_qwen: qwen2.5-coder:7b
  - suggested pull: `ollama pull qwen2.5-coder:7b`
- deepseek_coder_6_7b_or_7b: deepseek-coder:6.7b, deepseek-coder:7b
  - suggested pull: `ollama pull deepseek-coder:6.7b`
- codegemma_7b: codegemma:7b
  - suggested pull: `ollama pull codegemma:7b`

Excluded models:
- starcoder2:7b: excluded due to empty outputs under current Ollama chat backend

Fallback candidates not for main full run:
- fallback_if_codegemma_unavailable: qwen2.5-coder:3b. Installed fallback candidate only. Do not use in the main full run unless explicitly approved.
