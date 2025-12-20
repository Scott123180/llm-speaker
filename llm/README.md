# How to run locally

1. Download ollama
`curl -fsSL https://ollama.com/install.sh | sh`

2. Choose a model

Basic, llama model:
`ollama run llama3.1:8b`

Reference Link
https://ollama.com/library/llama3.1

### Small Model Setup
`ollama create llama8-cleanup -f Modelfile-llama8-cleanup`

``` bash
  cat ./30594.txt | ollama run llama8-cleanup > 30594_cleaned.txt
```

### Big Model Setup

Saw this was using around 42GB of memory.
`ollama create llama70-cleanup -f Modelfile-llama70-cleanup`

``` bash
  cat ./30594.txt | ollama run llama70-cleanup > 30594_cleaned_and_corrected.txt
```

# Running on the cloud

## Overview
The plan is to run this on a single GPU instance and keep the model server warm while we process 1,000s of separate text files

## Approach
Long-lived worker + a batch queue



1. Export the model from the dev machine
- `ollama list` to confirm model name
- `ollama export llama70-cleanup-H100-smallctx -o llama70-cleanup-H100-smallctx.ollama` (creates a portable bundle).
   Copy the `.ollama` file to the cloud/VM storage
2. Import on the cloud GPU machine
- Install Ollama and GPU drivers (Lambda H100 PCIe).
- `ollama import llama70-cleanup-H100-smallctx.ollama`
- `ollama serve` (keeps the model loaded; don’t restart between jobs).3. Batch runner script (single process, many requests - see below)
- A script walks your 6,300 files, sends each to http://localhost:11434/api/chat (or /api/generate), and writes output to a parallel directory.
- Keep concurrency low (1–4) to avoid VRAM thrash and keep latency consistent.
- Reuse a single HTTP session and the same model name.
4. I/O handling
- Place input files on fast local NVMe or a mounted volume.
- Write outputs to another directory; later sync back to storage.

## Targeted Machine
URL: https://lambda.ai/instances

Name: NVIDIA H100 PCIe
VRAM/GPU: 80 GB
vCPUs: 26
RAM: 225 GiB
Storage: 1 TiB SSD
Hourly Cost: $2.49

Might be cheaper and perform equal or better for this task:

Name: NVIDIA GH200
VRAM/GPU: 96 GB
vCPUs: 64
RAM: 432 GiB
Storage: 4 TiB SSD
Hourly Cost: $1.49


## Batch Cleaup Script
1. Start Ollama server once (keeps model warm)
ollama serve

2. Run batch cleanup
Small Model
``` bash
python3 batch_cleanup.py \
  --input-dir /path/to/raw_txt \
  --output-dir /path/to/clean_txt \
  --model llama8-cleanup
```
Big Model
``` bash
python3 batch_cleanup.py \
  --input-dir /path/to/raw_txt \
  --output-dir /path/to/clean_txt \
  --model llama70-cleanup
```
