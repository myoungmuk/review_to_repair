#!/bin/bash
export OLLAMA_MODELS=/cephfs/lab/models/ollama
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
exec /cephfs/lab/2022810001_강명묵/ollama_install/bin/ollama "$@"
