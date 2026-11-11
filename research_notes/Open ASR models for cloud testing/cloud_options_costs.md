# Cloud GPU options and costs for the open-ASR bake-off and full-archive run (researched 10 Nov 2026)

All prices are USD per GPU-hour unless stated, as listed on the dates fetched (10 Nov 2026). GPU rental prices move often, and marketplace prices (Vast.ai, RunPod community) change hour to hour. Anything marked **[est]** is my own calculation, not a published figure.

## 1. On-demand and spot/community prices by GPU and provider

### Takeaway
For an individual, **RunPod** (per-second billing, x86, no egress fees) and **Lambda** (per-minute billing, free egress, bigger CPU/RAM/disk per GPU) are the practical choices. The best price per GB of VRAM on x86 is the **RTX PRO 6000 Blackwell 96 GB**: $1.69 on RunPod community, $2.49 on RunPod secure. That is cheaper than any H100 and holds both Nemotron‑3.5 at bf16 and a 24B dense model at bf16. Lambda's **GH200 96 GB at $2.59** has the most CPU, RAM and disk per dollar, but its ARM64 host blocks the faster-whisper/CTranslate2 path.

### Cited findings

**RunPod pods (per-second billing, no commitment).** The table gives on-demand prices. "Community" is RunPod's cheaper peer-hosted tier. RAM and vCPU figures are per GPU, as listed. Source: [RunPod pricing](https://www.runpod.io/pricing).

| GPU | VRAM | RAM | vCPU | Secure | Community |
|---|---|---|---|---|---|
| L4 | 24 GB | 50 GB | 12 | $0.59 | $0.44 |
| A40 | 48 GB | 50 GB | 9 | $0.59 | $0.35 |
| RTX 4090 | 24 GB | 41 GB | 6 | $0.89 | $0.34 |
| RTX 5090 | 32 GB | 35 GB | 9 | $1.19 | $0.69 |
| RTX 6000 Ada | 48 GB | 167 GB | 10 | $0.99 | $0.74 |
| L40S | 48 GB | 94 GB | 16 | $1.09 | $0.79 |
| A100 PCIe | 80 GB | 117 GB | 8 | $1.79 | $1.19 |
| A100 SXM | 80 GB | 125 GB | 16 | $1.79 | $1.39 |
| **RTX PRO 6000** | **96 GB** | **188 GB** | **16** | **$2.49** | **$1.69** |
| H100 PCIe | 80 GB | 188 GB | 16 | $2.89 | $1.99 |
| H100 NVL | 94 GB | 94 GB | 16 | $3.19 | $2.59 |
| H100 SXM | 80 GB | 125 GB | 20 | $3.99 | $2.69 |
| H200 | 141 GB | 276 GB | 24 | $5.29 | $3.59 |
| B200 | 180 GB | 283 GB | 28 | $7.99 | $5.98 |

- RunPod serverless prices, per hour: L4/A5000/3090 $0.75, RTX 4090 $1.34, L40S/6000 Ada $1.75, RTX 5090 $1.79, A100 80 GB $2.72, RTX PRO 6000 $3.49, H100 $5.39, H200 $6.99, B200 $10.79 — [RunPod pricing](https://www.runpod.io/pricing).
- RunPod spot/interruptible: the pricing page shows no spot prices. A RunPod blog says spot is "usually much cheaper (50%)" and can be interrupted without notice — [RunPod blog](https://www.runpod.io/blog/spot-vs-on-demand-instances-runpod). But RunPod's own Lambda-comparison page says it has no spot tier, and a docs pull request removed spot references — [RunPod lambda-alternative](https://www.runpod.io/lambda-alternative). **Current spot availability is unclear.**

**Lambda on-demand.** These prices "take effect November 16, 2026, at 00:00 UTC". Until then, current prices are visible only after logging in. Source: [Lambda pricing](https://lambda.com/pricing).

| Instance | VRAM | vCPU | RAM | Local SSD | $/GPU-h |
|---|---|---|---|---|---|
| 1x A10 | 24 GB | 30 | 226 GiB | 1.3 TiB | $1.29 |
| 1x A6000 | 48 GB | 14 | 100 GiB | 512 GiB | $1.09 |
| 1x A100 PCIe/SXM 40 GB | 40 GB | 30 | 220–225 GiB | 512 GiB | $1.99 |
| **1x GH200 (ARM64 Grace)** | **96 GB** | **64** | **432 GiB** | **4 TiB** | **$2.59** |
| 1x H100 PCIe | 80 GB | 26 | 225 GiB | 1 TiB | $3.79 |
| 1x H100 SXM | 80 GB | 26 | 225 GiB | 2.75 TiB | $4.89 |
| 1x B200 SXM6 | 180 GB | 26 | 360 GiB | 2.75 TiB | $7.99 |
| 8x A100 80 GB (no 1x listed) | 80 GB | 240 | 1800 GiB | 19.5 TiB | $3.19 |
| 8x H100 | 80 GB | 208 | 1800 GiB | 22 TiB | $4.59 |

- Lambda bills on-demand instances "in one-minute increments" with no minimum. It charges nothing for ingress or egress — [Lambda billing docs](https://docs.lambda.ai/public-cloud/on-demand/billing). Lambda filesystems are billed per GB-month while they exist, even when unattached. Third parties put the rate at ~$0.20/GB/month (secondary source, possibly stale) — [Lambda filesystems docs](https://docs.lambdalabs.com/public-cloud/filesystems); [usagepricing](https://usagepricing.com/blueprint/lambda-labs).
- The previous report used the same post‑16‑Nov prices: GH200 $2.59, H100 PCIe $3.79, H100 SXM $4.89. Earlier in 2026, trackers listed the GH200 at $1.99–$2.29 — [Dharma talk transcription options report](../../reports/Dharma%20talk%20transcription%20options.md).
- Lambda lists no H200, L40S, L4, RTX 6000 Ada or RTX PRO 6000 single-GPU on-demand instances — [Lambda pricing](https://lambda.com/pricing).

**Modal (serverless, per-second billing).** Base GPU rates per hour: L4 $0.80, A10 $1.10, L40S $1.95, A100 40 GB $2.10, A100 80 GB $2.50, RTX PRO 6000 $3.03, H100 $3.95, H200 $4.54, B200 $6.25. CPU is extra at ~$0.047 per physical core-hour, and memory at ~$0.008/GiB-hour. The free Starter plan includes $30/month of credits and 1 TiB/month of free egress. Volumes cost $0.09/GiB/month, with 1 TiB free. Choosing a region multiplies prices by 1.15x–1.75x, and **non-preemptible execution costs 3x the base price**, so the base prices are for preemptible work — [Modal pricing](https://modal.com/pricing).

**Vast.ai (marketplace).** The live price grid did not render for scraping. Billing is per second with "no minimum hours, no rounding up". Interruptible instances are advertised as "50%+ cheaper" than on-demand — [Vast.ai pricing](https://vast.ai/pricing). Third-party snapshots: H100 at ~$1.05–$2.75/GPU-h (July 2026 marketplace snapshot), and an H100 SXM median of ~$2.14 (2 Nov 2026 post citing ComputeTick) — [Activepieces](https://www.activepieces.com/blog/vast-ai-gpu-pricing-per-hour-in-2026-and-extra-fees.md). H100 PCIe from $2.80 — [computeprices](https://computeprices.com/providers/vast/gpus/h100pcie). RTX 5090 ~$0.23–$0.41, or $0.337 (6 Aug 2026) — [computeprices](https://computeprices.com/providers/vast/gpus/rtx5090). These are secondary snapshots, and Vast prices fluctuate.

**Hetzner (dedicated GPU servers, hourly or monthly, prices excluding VAT)** — [Hetzner GPU matrix](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/):
- GEX45: RTX PRO 4000 Blackwell SFF 24 GB, i5‑13500, 64 GB RAM, 2x512 GB NVMe. €0.3429/h or €214/mo, plus a **€209 setup fee**.
- GEX63: RTX PRO 6000 Blackwell Max‑Q 96 GB, Core Ultra 7 265, 128 GB DDR5, 2x1.92 TB NVMe. €1.6009/h or €999/mo, plus a **€999 setup fee**.
- GEX131: RTX PRO 6000 Max‑Q 96 GB, Xeon Gold 5412U 24c/48t, 256–768 GB RAM, up to 4x3.84 TB NVMe. €2.4022/h or from €1,499/mo, plus a **€1,499 setup fee**.
- Traffic is unlimited and free, on a 1 Gbit/s uplink. Locations are Helsinki and Falkenstein.
- The setup fees equal one month's price, which rules Hetzner out for a short bake-off or a run of a few days.

**Hyperscalers (reference only):**
- GCP L4: about $0.71/h for the GPU on-demand. H100 A3‑High 8‑GPU node: ~$88.49/h (~$11.06 per GPU). Spot H100 ~$2.59/GPU-h and H200 ~$4.28/GPU-h, from a regional-language Spot VM pricing page I could not date — [GCP accelerator pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized?hl=en); [GCP Spot pricing](https://cloud.google.com/spot-vms/pricing?hl=zh-tw).
- AWS us-east-1: g6.xlarge (1x L4) $0.8048/h on-demand, spot ~$0.17–$0.44 depending on AZ. g6e.xlarge (1x L40S) ~$1.861/h on-demand, spot ~$0.87 (us-east-1b snapshot) — [Holori g6.xlarge](https://calculator.holori.com/aws/ec2/g6.xlarge/us-east-1); [DoiT g6e.xlarge](https://compute.doit.com/spot/us-east-1/g6e.xlarge); [Holori g6e.xlarge](https://calculator.holori.com/aws/ec2/g6e.xlarge).

### Inferences
- **The RTX PRO 6000 96 GB on RunPod is the sweet spot for the bake-off [est]**. It costs less than any 80 GB H100, is x86, has 96 GB (more than an H100's 80 GB), and comes with 188 GB of system RAM. Nemotron‑3.5 at bf16 reportedly uses ~75 GB under vLLM (third-party measurement, §3), which is tight on 80 GB and comfortable on 96 GB.
- The H200 141 GB ($3.59 community / $5.29 secure on RunPod) is the safe choice if a model needs more than 96 GB. Examples: running two big models side by side, or a 24B dense model with large audio batches.
- Hyperscalers cost 2–4x more on-demand, and new accounts usually need GPU quota approval. Neither is worth it here (the quota requirement is general knowledge; I did not verify it for these accounts).

### Gaps
- No live Vast.ai prices (the grid is JavaScript-rendered). No reliable Vast prices for GH200, H200, B200 or RTX PRO 6000.
- I did not fetch Paperspace/DigitalOcean, CoreWeave or Together GPU pricing. CoreWeave is aimed at contracted enterprise clusters, and I found no figures for individual on-demand use.
- RunPod's egress is "free", but its spot tier status is ambiguous (see above).
- Lambda's exact filesystem price is visible only at creation time.

## 2. RAM, vCPU, disk, storage, data transfer and billing increments

### Takeaway
The archive is much smaller than the assumed 1–2 TB. Measured local files average **~52 MB per audio hour**, so 6,500 h is about **340 GB** [est]. Pulling it once from CloudFront costs at most ~$30 in AWS egress, and it fits on any instance's local disk with the model weights.

### Cited findings
- I measured local mp3 sizes on 40 files in `data/audio` (43.4 h, 2.24 GB): 51.7 MB per audio hour. Scaled to 6,500 h, that is ~336 GB [est, assumes the sample's bitrate is typical].
- CloudFront data-transfer-out costs $0.085/GB for the first 10 TB in North America/Europe. The always-free tier covers 1 TB per month — [nOps CloudFront pricing](https://www.nops.io/blog/cloudfront-pricing/); [egresscost (verified 2026-06)](https://egresscost.com/aws/cloudfront-pricing). Third-party sources; check against the AWS page.
- Ingress and egress are free on RunPod pods — [RunPod pricing docs](https://docs.runpod.io/pods/pricing) — and on Lambda ([billing docs](https://docs.lambda.ai/public-cloud/on-demand/billing)). Modal includes 1 TiB/month of free egress, then charges $0.04/GiB ([Modal pricing](https://modal.com/pricing)). Hetzner traffic is unlimited ([Hetzner](https://www.hetzner.com/dedicated-rootserver/matrix-gpu/)).
- RunPod storage: container disk $0.10/GB/mo. Volume disk $0.10/GB/mo while running and $0.20 while idle. Network volume $0.07/GB/mo (below 1 TB) or $0.05 (above 1 TB), and $0.14 for high-performance — [RunPod pricing](https://www.runpod.io/pricing). Pods without a network volume lose their data when terminated — [Hivenet guide](https://www.hivenet.com/post/runpod-pricing-complete-guide-to-gpu-cloud-costs).
- Billing increments: RunPod and Vast.ai bill per second, Lambda per minute, Modal per second, Hetzner hourly but with a setup fee equal to one month — sources above.
- Local disk on Lambda 1x instances: GH200 4 TiB, H100 PCIe 1 TiB, H100 SXM 2.75 TiB — [Lambda pricing](https://lambda.com/pricing).

### Inferences
- **Storage cost is negligible [est].** About 340 GB of audio plus ~150–250 GB of weights and environments (Nemotron bf16 ~60–70 GB, a 24B dense model ~48 GB, VibeVoice ~18 GB, and smaller models) totals ~600 GB. On a RunPod network volume that is ~$42/month, or ~$1.40/day. Deleting the volume after each phase keeps it to a few dollars.
- **Transfer is fast and cheap [est].** On a 1 Gbit/s link, 340 GB downloads in about 45 minutes in theory, and realistically 1–3 h. CloudFront egress for one full pull is ~$29, or $0 if the account's 1 TB free tier is not already used up. Pull from CloudFront directly on the instance with a parallel downloader; the existing `content_fetcher` already does concurrent downloads. Do not upload from home.
- **vCPUs matter for the fast models.** At Parakeet-class speeds (hundreds to thousands × real time), mp3 decoding, resampling and VAD on the CPU become the bottleneck. A 16-vCPU RunPod RTX PRO 6000 or H100 PCIe should keep one GPU fed for Whisper, Qwen and Nemotron. For a Parakeet bulk run, the GH200 (64 vCPU) or Lambda H100 (26 vCPU) have more headroom. Decoding ahead of time to 16 kHz FLAC or WAV on the CPU is an option. (I found no published figure for mp3 decode throughput per core, so this is unquantified.)

### Gaps
- No primary AWS page for the current CloudFront tier schedule was fetched.
- Real per-pod network bandwidth on RunPod community hosts varies and is not published.

## 3. Practical issues: ARM64, Blackwell, Docker, spot, resumability

### Takeaway
Use x86 for the bake-off, because it runs CTranslate2/faster-whisper, NeMo and vLLM without source builds. The GH200 is only worth it for a PyTorch-only bulk run, such as Parakeet, Qwen via vLLM or Nemotron. Make every runner resumable per talk if spot or interruptible capacity is used.

### Cited findings
- CTranslate2 publishes no official CUDA aarch64 wheel. On a Grace-based DGX Spark, the PyPI wheel was CPU-only and raised "not compiled with CUDA support" — [speaches issue #620](https://github.com/speaches-ai/speaches/issues/620). Community Docker images compile CTranslate2 from source with CUDA and cuDNN to work around this — [cbinckly/speaches Docker Hub](https://hub.docker.com/r/cbinckly/speaches). Nix can build it with `withCUDA = true` — [NixOS discourse](https://discourse.nixos.org/t/cannot-get-python312packages-faster-whisper-working-with-cuda/58261).
- PyTorch publishes CUDA aarch64 wheels, and vLLM improved its ARM support in 2026, so NeMo, transformers and vLLM are the GH200-friendly stacks. TEN VAD has no aarch64 build — [earlier report, §throughput](../../reports/Dharma%20talk%20transcription%20options.md), citing [PyTorch KR](https://pytorch.kr/blog/2026/vllm-and-pytorch-improve-aarch64-experience/) and [TEN VAD](https://github.com/TEN-framework/ten-vad).
- Nemotron‑3.5‑Transcribe serving: NVIDIA's docs target one H100 80 GB at bf16 (`--gpu-memory-utilization 0.94`). They use vLLM 0.32.0 through NeMo Speech `main` with a Python 3.13 uv env, `--max-model-len 65536` and `--max-num-seqs 192`. Recordings of up to 1 h are supported per request. FP8 and NVFP4 checkpoints exist, with NVFP4 "for Blackwell GPUs". The docs state no CPU architecture, only "Linux", and give no throughput figures — [NVIDIA NeMo docs](https://docs.nvidia.com/nemo/speech/nightly/speechlm2/nemotron_transcribe.html).
- A third-party guide reports Nemotron‑3.5 at bf16 under vLLM "consumes just over 75GB of VRAM during active inference" — [aicybr guide](https://aicybr.com/blog/nvidia-nemotron-3-5-transcribe-local-speech-diarization-guide) (methodology unverified). A calculator estimates 73 GB at FP16, 37 GB at INT8 and 18 GB at INT4 — [Spheron GPU guide](https://www.spheron.network/tools/gpu-recommender/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B/).
- Qwen3‑ASR under stock vLLM: audio files over ~10 minutes do not fit in one request (Baseten, RTX PRO 6000), so VAD chunking is needed — [Baseten blog](https://baseten.co/blog/fastest-lowest-cost-qwen3-asr-batch-transcription) (the page did not render for me; figure from the search-result excerpt).
- Spot: RunPod spot can be interrupted without notice — [RunPod blog](https://www.runpod.io/blog/spot-vs-on-demand-instances-runpod). Vast interruptible instances are preemptible — [Vast.ai pricing](https://vast.ai/pricing). Modal's base prices assume preemption, and non-preemptible runs cost 3x — [Modal pricing](https://modal.com/pricing). AWS g6 spot shows a ~10–15% interruption rate — [Holori](https://calculator.holori.com/aws/ec2/g6.xlarge/us-east-1).

### Inferences
- **Blackwell risk on the RTX PRO 6000 [unverified]:** it is a Blackwell workstation part (sm_120). Wheels must be built for CUDA 12.8 or later. Recent PyTorch, vLLM and NeMo releases should be fine, but whether the CTranslate2 wheels in this repo's main env (cu12) run on sm_120 was not verified. Run a 5-minute smoke test of `asr/run_whisper.py` first. Whether NVFP4 kernels run on sm_120, as opposed to the datacenter B200's sm_100, is also unverified. Use bf16 or FP8 on the RTX PRO 6000.
- The repo already isolates NeMo (`asr/envs/nemo`) and Qwen (`asr/envs/qwen`) in uv projects. Nemotron needs a third env (Python 3.13, vLLM 0.32, NeMo `main`), and a 24B speech-LLM may need a fourth. On a fresh pod, building these envs and downloading weights will take longer than the gold-set inference itself (see §4).
- Use a RunPod network volume or a Lambda filesystem to hold `~/.cache/huggingface` and the uv envs, so a second session, or a replacement after a spot loss, starts in minutes.
- Resumability: `eval/run_bakeoff.sh` is already resumable. For the 6,500 h run, write one output JSON per talk, skip talks that already have output, and sync outputs to persistent storage or back home every few minutes. With that in place, interruptible capacity is safe.

### Gaps
- Whether NVIDIA NIM/Riva or the Nemotron vLLM plugin publish aarch64 images was not verified.
- CTranslate2 support on RTX PRO 6000/RTX 5090 (sm_120) was not verified.

## 4. Throughput, wall-clock and cost estimates

### Takeaway
**Bake-off:** about **$15–$40** of RTX PRO 6000 time, over roughly 6–12 billable hours, most of which go to environment setup and weight downloads [est]. **Full archive:** the local 3070 Ti already runs Parakeet (1.2 days) and turbo (1.8 days), so the cloud only pays off for **Qwen3‑ASR via vLLM (~$30–$60)** and **Nemotron‑3.5 (~$150–$320)** [est]. Whisper large-v3 costs ~$110–$360 in the cloud, against ~4 days free at home.

### Cited throughput inputs
- **Measured locally on the RTX 3070 Ti** (this repo, short gold-set clips, includes per-clip overhead) — `reports/ASR bake-off.md`:

  | System | Speed | Archive time |
  |---|---|---|
  | Parakeet‑TDT‑0.6B‑v3 | 224× (192× with boosting) | 1.2–1.4 days |
  | faster-whisper turbo | 153× | 1.8 days |
  | faster-whisper large-v3 | 60–64× | 4.2–4.6 days |
  | Qwen3‑ASR‑1.7B, transformers backend | 17–22× | 12–15 days |
- **L4 (E2E Networks, 27 Mar 2026, LibriSpeech):** whisper-large-v3-turbo 41.1× (HF transformers, batch 4). Parakeet‑TDT‑0.6B‑v3 238.9× (batch 8, 5.1 GB). Nemotron streaming‑en‑0.6B 258.9× — [E2E Networks](https://www.e2enetworks.com/blog/benchmarking-asr-models-nvidia-l4-parakeet-whisper-nemotron).
- **Leaderboard RTFx (A100, batched; best case):** Parakeet‑TDT‑0.6B‑v3 3,333×. Whisper large-v3 68.6×. turbo 148×. Canary‑Qwen‑2.5B 16.1× (long-form). Nemotron‑3.5‑Transcribe 110.5× long-form, measured on H200 — [earlier report](../../reports/Dharma%20talk%20transcription%20options.md), citing the [Open ASR paper](https://arxiv.org/html/2510.06961v4) and [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [localaimaster Parakeet page](https://localaimaster.com/models/parakeet-tdt).
- **Qwen3‑ASR:** the official figure for the 0.6B model is 2,000× throughput at concurrency 128, against 106× at concurrency 1 — [QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR). For the 1.7B on an RTX PRO 6000 with 64 concurrent requests, stock vLLM "plateaus around 380x". Baseten's tuned stack reaches 2,645× on 5-minute clips and 3,128× on hour-long files (vendor figure) — [Baseten blog](https://baseten.co/blog/fastest-lowest-cost-qwen3-asr-batch-transcription) (search excerpt; page did not render).
- **Modal end-to-end batch (July 2025):** Parakeet‑TDT‑0.6B‑v2 transcribed about a week of audio in ~1 minute for ~$1, on A100/L40S-class GPUs with an autoscaling pool, excluding CPU cost — [Modal blog](https://modal.com/blog/fast-cheap-batch-transcription).

### Estimates for (a) the bake-off [est]
Gold set: 3.8 h of speech plus 38 min of non-speech, ~4.5 h of audio in total ([bake-off report](../../reports/ASR%20bake-off.md)). Assume ~12 models, with 2–3 context variants for some.

- Pure inference per model run is 3–15 min even at 20–100× (4.5 h ÷ 20 = 13.5 min). Thirty runs total ~2–4 GPU-hours.
- Setup is the larger cost: 3–4 uv envs, ~150–250 GB of weight downloads, vLLM warm-up and compilation, and debugging. Allow 4–8 h.
- **Total ≈ 6–12 billable hours.** On a RunPod RTX PRO 6000 that is **$10–$20 community or $15–$30 secure**. On a Lambda H100 PCIe ($3.79) it is $23–$45, and on a RunPod H200 secure ($5.29) $32–$64. Add ~$1–$3 for a 600 GB network volume kept for a few days.
- Running models in parallel on one 96 GB card (a small model alongside a big one) can halve the wall-clock time.

### Estimates for (b) 6,500 h per model [est]
GPU-hours = 6,500 ÷ assumed end-to-end speed. Prices: RunPod RTX PRO 6000 $1.69/$2.49, RunPod H100 PCIe $1.99/$2.89, Lambda GH200 $2.59, RunPod L4 $0.44/$0.59.

| Model | Assumed cloud speed (basis) | GPU-h | RTX PRO 6000 (comm./secure) | H100 PCIe (comm./secure) | Cheaper option | Local 3070 Ti |
|---|---|---|---|---|---|---|
| Parakeet‑TDT‑0.6B‑v3 | 500–1,000× (CPU-bound well below the 3,333× leaderboard) | 6.5–13 | $11–$32 | $13–$38 | L4 at ~239×: 27 h, $12–$16 | **1.2 days, free** |
| faster-whisper turbo | 150–300× (local 153×; leaderboard 148×) | 22–44 | $37–$110 | $43–$127 | L4 at ~41× (HF): 159 h, ~$70–$94 | **1.8 days, free** |
| faster-whisper large-v3 | 65–130× (local 64×; leaderboard 68.6×) | 50–100 | $85–$250 | $100–$290 | — | 4.2–4.6 days, free |
| **Qwen3‑ASR‑1.7B (vLLM)** | ~380× stock vLLM (Baseten, RTX PRO 6000) | ~17 | **$29–$43** | similar | — | 12–15 days with transformers |
| **Nemotron‑3.5 (bf16, vLLM)** | 110× on H200 (leaderboard); ~70–110× on H100/PRO 6000 (guess) | 59–93 | $100–$230 | $118–$270 | H200: 59 h × $3.59/$5.29 = **$212–$312** | Not possible |
| Canary‑Qwen‑2.5B | 16× long-form | ~404 | $680–$1,000 | $800–$1,170 | — | Impractical |

- For the largest runs, a GH200 at $2.59 costs about the same as RunPod secure RTX PRO 6000 or H100 pricing, with 4x the CPU and RAM. It runs only PyTorch/vLLM stacks; see §3.
- Wall-clock on one GPU: Parakeet <1 day, Qwen3‑ASR ~1 day, Nemotron ~2.5–4 days, large-v3 ~2–4 days. Splitting across 2–4 pods divides the wall-clock time at the same total cost, since billing is per second.

### Inferences / recommendation
1. **Bake-off: one RunPod RTX PRO 6000 96 GB** (secure $2.49/h or community $1.69/h), x86, with 188 GB RAM, 16 vCPU and a ~600 GB network volume. It runs every candidate up to Nemotron bf16 (~75 GB) and a 24B dense model at bf16 (~48 GB of weights) on one card, with per-second billing and free egress. **Fallback:** RunPod H200 141 GB ($3.59/$5.29) if 96 GB is too little, or Lambda H100 PCIe ($3.79, 26 vCPU, 225 GiB, 1 TiB local SSD, per-minute billing) if RunPod capacity is short.
2. **Full run:** keep Parakeet, turbo and probably large-v3 local, since they are measured to take 1–5 days. Rent only for the bake-off winner if it is a speech-LLM. Qwen3‑ASR on vLLM costs ~$30–$60 on the same RTX PRO 6000 setup. Nemotron‑3.5 costs ~$150–$320 on an RTX PRO 6000, H100 or H200, or on a Lambda GH200 if the PyTorch-only stack builds on ARM. Pull audio straight from CloudFront (~340 GB, ≤~$30), write per-talk outputs and resume. Interruptible capacity (Vast, or RunPod spot if offered) can then cut ~50%.
3. Hetzner (one-month setup fee), the hyperscalers (2–4x the price, quotas) and Modal (non-preemptible is 3x; base RTX PRO 6000 $3.03, H100 $3.95) do not fit this one-off, individual workload. One exception is Modal's $30/month free credit, which could cover a small parallel Parakeet or Qwen run.

### Gaps
- No published H100 or RTX PRO 6000 RTFx exists for faster-whisper, Nemotron‑3.5‑Transcribe or Qwen3‑ASR‑1.7B under stock vLLM on long-form audio. The cloud rows above are extrapolations. Measure each finalist on the gold set during the bake-off and recompute.
- No source quantifies Nemotron‑3.5 throughput on non-H200 GPUs or with FP8.
- I did not identify the specific 24B dense speech model or its VRAM and throughput, so it is treated generically (bf16 weights ≈ 2 bytes × params).
