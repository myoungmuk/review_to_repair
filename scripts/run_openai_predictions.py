#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from run_local_predictions import main


if __name__ == "__main__":
    print(
        "scripts/run_openai_predictions.py is kept only as a compatibility shim. "
        "It now uses the local-LLM runner. Prefer scripts/run_local_predictions.py.",
        file=sys.stderr,
    )
    main()
