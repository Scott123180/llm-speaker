# ASR Inference Pipelines, VAD, Alignment, and Batch Throughput for a ~6,500-Hour Dharma-Talk Archive (as of Nov 2026)

Scope: replacing a per-file `whisper file.mp3 --model turbo` bash loop for ~6,500 English talks (~5,000–8,000 h audio, center estimate 6,500 h) with long silences, bells, chanting, and old noisy audio. Hardware: local RTX 3070 Ti (8 GB), rented Lambda H100 80 GB / GH200 96 GB (ARM64 Grace CPU).

Research date: 2026-11-08. About 18 searches and fetches. Some framework areas were not re-verified this session; they are listed under Gaps.

---

## 1. WhisperX: maintenance status, accuracy and hallucination behavior, known issues

### Takeaway
WhisperX is actively maintained in 2026 (v3.8.x line, ~25k stars). It is still the most complete Whisper wrapper: VAD-chunked batched faster-whisper, wav2vec2 word alignment, and pyannote diarization. Its documented weak points are unchanged: words containing digits or symbols get no timing, overlapping speech is handled poorly, and diarization is imperfect. It also inherits CTranslate2's ARM64 problem (see section 8).

### Cited Findings
- The latest release listed is **v3.8.6, dated May 25, 2026**. Other 2026 releases include v3.8.4, which requires faster-whisper ≥1.2.0, and v3.7.8, which backported word-level-timestamp fixes from v3.8.2 — [GitPedia](https://gitpedia.pages.dev/wiki/m-bain/whisperX); [newreleases v3.8.4](https://newreleases.io/project/github/m-bain/whisperX/release/v3.8.4); [newreleases v3.7.8](https://newreleases.io/project/github/m-bain/whisperX/release/v3.7.8). I could not open the GitHub releases page directly to confirm which version is current.
- The repo crossed 25.0k stars on Nov 2, 2026 — [GitTrend](https://gittrend.io/repo/m-bain/whisperX). At fetch time the README page showed ~180 open issues and ~39 open PRs. It recommends the PyPI release over the dev branch for production — [whisperX README](https://github.com/m-bain/whisperX).
- Speed claim: "batched inference for 70x realtime transcription using whisper large-v2", with under 8 GB GPU memory for large-v2 at beam_size=5. The README gives no GPU for the 70x figure. The default batch_size is 16, and the README suggests lowering batch size or using int8 when memory is short — [whisperX README](https://github.com/m-bain/whisperX).
- Hallucination handling: the README says VAD preprocessing reduces hallucination, and `condition_on_prev_text` defaults to False for that reason. Batched mode transcribes **without Whisper timestamp tokens**, so output can differ from vanilla Whisper — [whisperX README](https://github.com/m-bain/whisperX).
- VAD: pyannote is used for VAD and diarization. The README still has an open TODO to "allow silero-vad as alternative VAD option". **Conflict:** some forks and versions may differ, and I did not verify the current code — [whisperX README](https://github.com/m-bain/whisperX).
- Alignment: phoneme-level wav2vec2 models. English uses the torchaudio default. A larger alignment model was "not found to be that helpful" — [whisperX README](https://github.com/m-bain/whisperX).
- Documented limitations:
  - Words with characters missing from the alignment dictionary (e.g. "2014.", "£13.60") get no timestamps.
  - "Overlapping speech is not handled particularly well."
  - "Diarization is far from perfect."
  - A language-specific alignment model is required.
  - Source: [whisperX README](https://github.com/m-bain/whisperX).
- Prompting: the fetched README did not mention `initial_prompt` or hotwords. It reportedly describes a 2026 "context-aware batching" option, `interleaved_context`, meant for long audio and technical vocabulary — [whisperX README](https://github.com/m-bain/whisperX). Flag: this came from a single page fetch and should be checked against the code.

### Inferences
- For dharma talks, the digit/symbol alignment gap matters less than it would for technical talks. Sanskrit/Pali/Japanese terms (e.g. "Dōgen", "sesshin") use letters only. Diacritics such as "ō" may fall outside the English wav2vec2 character set and lose word timing. Normalizing to ASCII before alignment would avoid this.
- Batched decoding with no previous-text conditioning and no timestamp tokens reduces cascading hallucination loops over long silences. The trade-off is less cross-chunk context, so punctuation and capitalization across chunk boundaries may be less consistent than sequential Whisper.
- The 70x realtime figure is for large-v2 on unspecified hardware. Use it as an order-of-magnitude number, not a planning constant.

### Gaps
- No independent 2026 WER or hallucination benchmark compares WhisperX with vanilla Whisper on noisy long-form audio. The WhisperX paper (arXiv 2303.00747) was not re-fetched this session.
- I did not verify whether pyannote VAD in current WhisperX still requires a Hugging Face token or gated-model acceptance.
- I did not confirm whether `initial_prompt` and hotwords pass through in batched mode in v3.8.x.

---

## 2. faster-whisper / CTranslate2 and other Whisper inference engines

### Takeaway
faster-whisper's `BatchedInferencePipeline` is the most proven drop-in upgrade for the current loop. On the exact local GPU (RTX 3070 Ti), the README benchmark shows **~46x realtime for large-v2 batched**, versus ~5.5x for openai/whisper. The VAD filter is on by default in batched mode. The main drawback is CUDA availability on ARM64.

### Cited Findings
- **README benchmark on an RTX 3070 Ti 8 GB (CUDA 12.4), 13-min clip, large-v2, beam 5** — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper):

  | Implementation | Precision | Time | VRAM |
  |---|---|---|---|
  | openai/whisper | fp16 | 2m23s | 4708 MB |
  | whisper.cpp (Flash Attention) | fp16 | 1m05s | 4127 MB |
  | HF transformers (SDPA) | fp16 | 1m52s | 4960 MB |
  | faster-whisper | fp16 | 1m03s | 4525 MB |
  | faster-whisper, batch_size=8 | fp16 | 17s | 6090 MB |
  | faster-whisper | int8 | 59s | 2926 MB |
  | faster-whisper, batch_size=8 | int8 | 16s | 4500 MB |

  - The benchmark was run on faster-whisper v1.1.0.
  - openai/whisper defaults to beam 1 and faster-whisper to beam 5, so settings must be matched for a fair comparison.
- distil-large-v3, batch 16, fp16:
  - faster-whisper: 25m50s, YouTube-Commons WER 13.53.
  - HF transformers: 46m12s, WER 14.80.
  - Source: [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- Batched usage: `BatchedInferencePipeline(model=WhisperModel("turbo", device="cuda", compute_type="float16"))`, then `.transcribe("audio.mp3", batch_size=16)`, as a drop-in replacement. "VAD filter is enabled by default for batched transcription." — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- VAD filter details:
  - Uses Silero VAD.
  - The default setting only removes silences longer than 2 s; it can be tuned via `vad_parameters`, e.g. `min_silence_duration_ms=500`.
  - Word timestamps come from `word_timestamps=True`.
  - Source: [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- Batching history: batching was introduced in PR #856, "inspired by whisper-x", and reported a ~3x speedup (medium model, batch 8) — [faster-whisper PR #856](https://github.com/SYSTRAN/faster-whisper/pull/856). A README mirror claims 10–12x over openai/whisper and 3–4x over sequential faster-whisper — [PyPI mirror](https://pypi.org/project/topai-faster-whisper/1.0.4.post1).
- Requirements:
  - Current CTranslate2 needs CUDA 12 + cuDNN 9. Use ctranslate2 3.24.0 for CUDA 11, or 4.4.0 for CUDA 12 + cuDNN 8.
  - Audio is decoded with PyAV, so the ffmpeg binary is not required.
  - `segments` is a lazy generator: nothing runs until you iterate it.
  - Source: [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- Community data point: sequential large-v3 fp16 takes ~52 s for a LibriSpeech-clean test set — [HF discussion](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3). This is a secondary forum post.
- vLLM serves Whisper. HF's Inference Endpoints team reported "nearly 8x improvement in RTFx" for Whisper large-v3 on vLLM versus their earlier setup, with no quality loss. A commenter noted missing timestamp support at the time — [HF blog](https://huggingface.co/blog/fast-whisper-endpoints). The post is older (2025). I did not verify current vLLM Whisper timestamp support.

### Inferences
- **RTFx on the 3070 Ti** (from the table): 13 min = 780 s.
  - openai/whisper: 780/143 ≈ **5.5x**
  - faster-whisper sequential: ≈ **12x**
  - faster-whisper batched fp16: 780/17 ≈ **46x**; int8: 780/16 ≈ **49x**
  - These are large-v2 numbers. large-v3 has the same size. Turbo (4 decoder layers) should be faster still: the Open ASR long-form ratio of turbo to v3 RTFx is about 2.2x (section 7).
- The current loop also reloads the model for every file and uses beam 5 by default. Keeping one long-lived Python process that loads the model once and iterates over files removes ~10–20 s of overhead per file. Over ~6,500 files that is roughly 18–36 h.
- The README's Silero default (only silences > 2 s removed) is conservative and fits talks with pauses well. Tightening `min_silence_duration_ms` risks clipping soft-spoken phrase starts.
- Other engines, ranked for this archive's needs (word timestamps + batch throughput):
  1. faster-whisper batched or WhisperX on x86.
  2. HF transformers or vLLM on ARM64 or when PyTorch-only is required.
  3. whisper.cpp, which is competitive single-stream and has native ARM builds but is weaker for GPU batch throughput.

### Gaps
- These were **not re-verified this session**, so no 2026 numbers are available:
  - insanely-fast-whisper (HF transformers + Flash Attention 2, chunked batching). Its README historically claimed ~150 min of audio in <98 s on an A100 (large-v3, fp16, batch 24, FA2).
  - stable-ts (timestamp stabilization and silence suppression on top of Whisper/faster-whisper).
  - WhisperS2T (multi-backend, including TensorRT-LLM).
  - TensorRT-LLM's Whisper example.
- No large-v3 or turbo batched benchmark appears in the faster-whisper README itself.
- I found no current confirmation of the hotwords parameter behavior or whether `initial_prompt` works in `BatchedInferencePipeline`.

---

## 3. NVIDIA NeMo: Parakeet / Canary on long audio, timestamps, Riva/NIM

### Takeaway
Parakeet TDT 0.6B v3 has the best accuracy-to-speed ratio for English. Its long-form RTFx is ~1000 on an A100, about 15x Whisper large-v3, with *better* long-form WER. It natively handles up to 3 h per file with local attention, so 90-minute talks need no chunking. Canary-Qwen 2.5B is the most accurate on short-form but is very slow on long-form.

### Cited Findings
- Parakeet TDT 0.6B v3 long audio: up to 24 min with full attention on an A100 80 GB, or **up to 3 hours with local attention**. Enable it with `asr_model.change_attention_model(self_attention_model="rel_pos_local_attn", att_context_size=[256, 256])` — [NGC Parakeet TDT collection](https://catalog.ngc.nvidia.com/orgs/nvidia/-/collections/parakeet-tdt-0.6b/).
- Throughput claims (sources disagree):
  - The NGC page cites RTFx 2940 on the HF Open ASR leaderboard at batch 128 — [NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/collections/parakeet-tdt-0.6b/).
  - A third party reports 3,332.74 — [localaimaster](https://localaimaster.com/models/parakeet-tdt).
  - The Open ASR paper reports 3330 short-form and **1000 long-form** on an A100 — [Open ASR Leaderboard paper](https://arxiv.org/html/2510.06961v4).
- The Open ASR paper abstract: CTC and TDT decoders "offer superior RTFx", while conformer-encoder + transformer-decoder (Canary-style) models achieve the best average WER — [arXiv 2510.06961](https://arxiv.org/abs/2510.06961).
- The Canary-1B-v2 & Parakeet-TDT-0.6B-v3 paper is the primary technical source — [arXiv 2509.14128](https://arxiv.org/pdf/2509.14128). It was not read in full this session.
- NVIDIA ships Parakeet 0.6B TDT as a NIM container (v1.3) — [NGC NIM](https://catalog.ngc.nvidia.com/orgs/nim/nvidia/containers/parakeet-0.6b-tdt/1.3). I did not verify its offline batch mode or ARM64 image.

### Inferences
- Parakeet TDT's long-form WER (10.7) beats Whisper large-v3 (11.2) and turbo (11.0) on the leaderboard's long-form set (section 7), so moving to it costs no accuracy on benchmark audio.
- Parakeet output is cased and punctuated, but its formatting style differs from Whisper's. Whether readability holds up on archaic, noisy, and jargon-heavy dharma audio is the key unknown. A pilot on ~20 representative talks is warranted.
- Transducer models like Parakeet TDT tend to emit nothing rather than invent text on silence or noise. This is a structural advantage over Whisper's autoregressive decoder for chanting and bells. It is an inference from architecture, not a measured result for this archive.
- NeMo is PyTorch-based, so on a GH200 it avoids the CTranslate2 ARM problem (section 8).

### Gaps
- No published RTFx for Parakeet with local attention on 60–90-min files, or on consumer 8 GB GPUs.
- I did not confirm here that Parakeet word timestamps (`timestamps=True` in `transcribe`) work together with local attention, though the model card advertises word and segment timestamps.
- Canary-1B-flash and Canary-1B-v2 long-form RTFx were not found in the leaderboard paper table.
- I did not verify whether Riva or NIM offers an offline bulk-file mode suited to 6,500 files, or its licensing.

---

## 4. Audio-LLMs via vLLM (Qwen3-ASR, Voxtral)

### Takeaway
Audio-LLMs now match or beat Whisper on short-form WER (Qwen3-ASR 1.7B: 5.76 vs 7.44). On standard benchmarks their throughput is at best Whisper-like, and Voxtral Small is much slower. Long-form timestamping needs a separate aligner with length limits. They are not the throughput-optimal choice for this archive.

### Cited Findings
- Open ASR short-form (A100, batch ≤64) — [Open ASR paper](https://arxiv.org/html/2510.06961v4):
  - Qwen3-ASR 1.7B: WER 5.76, RTFx 148
  - Voxtral Small 24B: WER 6.62, RTFx 54.1
  - Granite Speech 4.0 1B: WER 5.52, RTFx 280
  - Phi-4 multimodal: WER 6.02, RTFx 151
  - Canary-Qwen 2.5B: WER 5.63, RTFx 418 (long-form RTFx 16.1)
- Voxtral Mini 3B short-form RTFx is 109.86, versus 145.51 for Whisper large-v3, according to a third-party copy of leaderboard data — [F22 Labs](https://www.f22labs.com/blogs/voxtral-mini-3b-vs-whisper-large-v3-which-ones-faster/).
- Qwen3-ASR vendor claims:
  - The 0.6B model reaches "2000 times throughput at a concurrency of 128" — [Qwen3-ASR GitHub](https://github.com/QwenLM/Qwen3-ASR).
  - The README says long audio is supported and recommends raising `max_new_tokens` (e.g. 4096).
  - A vLLM path combined with a forced aligner is shown via `Qwen3ASRModel.LLM(..., forced_aligner=...)`.
- **Conflict on vLLM features:** a third-party ADR states the vLLM backend does *not* support batch inference or timestamps. It lists ~1200x realtime for 1.7B at concurrency 128 — [WhisperJAV ADR-003](https://meizhong986.github.io/WhisperJAV/architecture/ADR-003-qwen3-asr-integration). Verify against the installed `qwen-asr` version.
- The Qwen3 ForcedAligner reportedly handles at most ~5 minutes of speech per call, so long files must be segmented first — [Qwen3-ForcedAligner mirror](https://huggingface.co/Jinstudio/Qwen3-ForcedAligner-0.6B). This comes from a secondary source.
- One aggregator rates the Qwen3-ASR repo "inactive" in responsiveness — [SourcePulse](https://www.sourcepulse.org/projects/23584437).
- Voxtral Realtime (Mini 4B, 2602) is "currently only supported in vLLM" through a `/v1/realtime` streaming endpoint. Raising `--max-num-batched-tokens` trades latency for throughput — [HF model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602).
- vLLM and PyTorch improved aarch64 support in 2026 — [PyTorch KR blog](https://pytorch.kr/blog/2026/vllm-and-pytorch-improve-aarch64-experience/).

### Inferences
- Audio-LLMs are worth testing for *readability* (punctuation, disfluency handling) rather than throughput. They overlap with what the downstream Llama cleanup stage already does.
- They still carry LLM-style hallucination risk on non-speech, so VAD gating stays mandatory.

### Gaps
- No independent long-form (30–90 min) throughput or WER numbers for Qwen3-ASR or Voxtral under vLLM.
- No verified 2026 state of vLLM's Whisper timestamp support.

---

## 5. VAD options and their effect on hallucination and speech cut-off

### Takeaway
Non-speech hallucination in Whisper is common and well documented. VAD gating plus post-filtering of known hallucination strings is the evidence-backed mitigation. Silero, built into faster-whisper, is the default choice. TEN VAD claims better precision and recall but has no Linux aarch64 build.

### Cited Findings
- Barański et al. (ICASSP 2025) ran Whisper on non-speech audio from AudioSet, MUSAN, UrbanSound8K, and FSD50K — [arXiv 2501.11378](https://arxiv.org/abs/2501.11378):
  - About **40.3% of non-speech inputs produced hallucinations**, with more than 41,000 unique outputs.
  - The authors built a "Bag of Hallucinations" (BoH) list for post-filtering.
  - Repetition loops count as a separate hallucination type.
- VAD combined with BoH reduced erroneous outputs by **67.08%**. Tuning Whisper's parameters alone helped little — [EmergentMind summary](https://www.emergentmind.com/papers/2501.11378). This figure comes from a secondary summary, not checked against the paper.
- TEN VAD — [TEN VAD repo](https://github.com/TEN-framework/ten-vad):
  - Claims the "best performance" versus Silero and WebRTC on a hand-annotated LibriSpeech/GigaSpeech/DNS test set, shown as PR curves only (no numbers).
  - Claims Silero has a delay of "several hundred ms" on speech-to-non-speech transitions and misses short pauses.
  - RTF on a Xeon Gold 6348: 0.0086 for TEN versus 0.0127 for Silero.
  - Prebuilt libraries cover Linux x64 but **not Linux aarch64**. Python bindings are "optimized for Linux x64", with ONNX Python inference on Linux and macOS.
  - Requires 16 kHz input. License is Apache-2.0 with extra conditions.
- faster-whisper's Silero filter default only removes silences > 2 s — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper). WhisperX uses pyannote for VAD — [whisperX README](https://github.com/m-bain/whisperX).

### Inferences
- Chanting is the hard case. It is voiced and pitched, so all of these VADs are likely to pass it as speech, and Whisper may then produce sutra text or hallucinated phrases. Options:
  - A music/chant classifier pass (e.g. an AudioSet-tagging model) to label chant segments.
  - Accept that chants get transcribed.
  - Post-filter using the BoH list plus repeated-n-gram detection.
- Bells are short and broadband. VADs generally reject them, but a bell inside a long silence can trigger a Whisper "Thank you." style hallucination when VAD is off.
- The cut-off risk mostly comes from aggressive `min_silence_duration_ms` / `speech_pad_ms` settings. Keep padding at ≥200–400 ms for soft-spoken teachers. This is a heuristic, not sourced.

### Gaps
- No head-to-head benchmark of Silero vs pyannote vs NeMo MarbleNet / Frame-VAD vs TEN VAD on hallucination rate in a downstream ASR pipeline was found.
- NeMo Frame-VAD and MarbleNet were not researched this session.
- The "Careless Whisper" study (Koenecke et al.) appeared in search summaries as reporting ~1% of transcriptions containing fully hallucinated phrases. I did not fetch the primary source.

---

## 6. Forced alignment options for word timestamps

### Takeaway
Use whichever aligner matches the ASR stack:
- Whisper path: WhisperX's wav2vec2 aligner.
- NeMo path: Parakeet TDT's native timestamps, or the NeMo Forced Aligner (NFA) with a CTC model.
- Qwen3-ASR path: Qwen3 ForcedAligner, capped at ~5 min per call.

NFA explicitly supports 1 h+ files.

### Cited Findings
- NFA — [NFA docs](https://docs.nvidia.com/nemo/speech/latest/tools/nemo_forced_aligner.html):
  - Produces token, word, and segment timestamps from **CTC** NeMo models.
  - Pure Transducer models cannot be used; hybrid CTC-Transducer models work in CTC mode.
  - Handles "long audio files of 1+ hours duration", subject to memory.
  - Has a buffered chunked-streaming mode for CTC models (chunk 1.6 s, buffer 4.0 s). In that mode it transcribes for itself and ignores the provided text.
  - Writes CTM output to `ctm/words/<utt_id>.ctm`.
- WhisperX wav2vec2 alignment fails for tokens that contain characters outside the model's dictionary (digits, currency) — [whisperX README](https://github.com/m-bain/whisperX).
- The Qwen3 aligner works on segments of up to ~5 min — [Qwen3-ForcedAligner mirror](https://huggingface.co/Jinstudio/Qwen3-ForcedAligner-0.6B). Secondary source.

### Inferences
- If the Whisper transcript is kept as the text of record, NFA with a Parakeet CTC 1.1B model can re-align Whisper text to audio. Run the text through English normalization first (numbers spelled out).

### Gaps
- torchaudio MMS aligner and the `ctc-forced-aligner` package were not researched this session. Torchaudio's deprecation of some alignment APIs in 2.8+ should be checked.
- No accuracy comparison of aligners on noisy long-form speech was found.

---

## 7. Throughput benchmarks and archive-level wall-clock and cost estimates

### Takeaway
At Lambda prices effective **Nov 16, 2026**, the whole archive costs roughly:
- **~$15–40** with Parakeet TDT
- **~$110–170** with Whisper turbo
- **~$250–470** with Whisper large-v3

The ranges reflect GPU choice and the 5,000–8,000 h spread. The local 3070 Ti alone can do the job with batched faster-whisper in about **4–7 days of continuous running**. Parakeet should take a fraction of that if it fits in 8 GB, which it should at 0.6B.

### Cited Findings
- **Open ASR Leaderboard (A100-SXM4-80GB, CUDA 12.6, batch 64 adaptively reduced)** — [arXiv 2510.06961v4](https://arxiv.org/html/2510.06961v4):

  | Model | Short-form WER / RTFx | Long-form WER / RTFx |
  |---|---|---|
  | Whisper large-v3 | 7.44 / 146 | 11.2 / **68.6** |
  | Whisper large-v3-turbo | 7.83 / 200 | 11.0 / **148** |
  | Distil-Whisper large-v3.5 | 7.21 / 202 | 11.7 / 156 |
  | Parakeet TDT 0.6B v3 | 6.32 / 3330 | 10.7 / **1000** |
  | Parakeet CTC 1.1B | 7.40 / 2730 | 12.9 / 2790 |
  | Parakeet CTC 0.6B | — | 13.7 / 4383 |
  | Canary-Qwen 2.5B | 5.63 / 418 | 11.2 / **16.1** |
  | Qwen3-ASR 1.7B | 5.76 / 148 | n/a |
  | Voxtral Small 24B | 6.62 / 54.1 | n/a |

  The paper notes that absolute RTFx depends on hardware. It does not say which Whisper inference framework or long-form method (chunked or sequential) was used.
- RTX 3070 Ti, large-v2: faster-whisper batched fp16 ran 13 min in 17 s (≈46x RT); openai/whisper took 2m23s (≈5.5x) — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- WhisperX claims 70x realtime with large-v2 batched, GPU unspecified — [whisperX README](https://github.com/m-bain/whisperX).
- **Lambda on-demand prices, effective Nov 16, 2026 00:00 UTC** — [Lambda pricing](https://lambda.com/pricing):

  | Instance | Price per GPU-hour | vCPU / RAM |
  |---|---|---|
  | 1x GH200 96 GB | **$2.59** | 64 vCPU / 432 GiB |
  | 1x H100 SXM | **$4.89** | 26 vCPU / 225 GiB |
  | 1x H100 PCIe | **$3.79** | 26 vCPU / 225 GiB |
  | 1x A100 40 GB | $1.99 | — |
  | 1x A10 24 GB | $1.29 | — |
  | 8x H100 | $4.59 | — |

  Before Nov 16, prices are login-only. Third-party trackers showed GH200 at $1.99–$2.29 earlier in 2026 — [computeprices (Aug 2026)](https://computeprices.com/providers/lambda/gpus/gh200). Lambda bills per minute with no egress fees — [Lambda AI cloud](https://lambda.ai/welcome/ai-cloud).

### Inferences: estimates for 6,500 h of audio (range for 5,000–8,000 h in parentheses)

Method: wall-clock = audio hours ÷ RTFx. A100 long-form RTFx is used as a **conservative proxy** for H100 and GH200. Hopper is typically faster than A100, often ~1.5–2x for inference; that is an unsourced rule of thumb. Costs use the Nov 16, 2026 prices.

| Pipeline | RTFx basis | GPU-hours (A100-equiv) | Cost on GH200 @ $2.59 | Cost on H100 PCIe @ $3.79 | Cost on H100 SXM @ $4.89 |
|---|---|---|---|---|---|
| Whisper large-v3, batched (faster-whisper / HF) | 68.6 long-form | **95 h** (73–117) | ~$245 | ~$360 | ~$465 |
| WhisperX large-v2/v3 (70x claim, + alignment) | ~70 | **~93 h + alignment** | ~$240+ | ~$350+ | ~$455+ |
| Whisper large-v3-turbo, batched | 148 long-form | **44 h** (34–54) | ~$114 | ~$166 | ~$215 |
| Parakeet TDT 0.6B v3 (NeMo, local attn) | 1000 long-form | **6.5 h** (5–8) | ~$17 | ~$25 | ~$32 |
| Parakeet CTC 1.1B | 2790 long-form | **2.3 h** | ~$6 | ~$9 | ~$11 |
| Canary-Qwen 2.5B | 16.1 long-form | **404 h** (311–497) | ~$1,045 | ~$1,530 | ~$1,975 |
| Qwen3-ASR 1.7B (leaderboard) | 148 short-form | ~44 h | ~$114 | ~$166 | ~$215 |
| Qwen3-ASR 0.6B (vendor "2000x" @ conc. 128) | 2000 (vendor claim) | ~3.3 h | ~$9 | ~$12 | ~$16 |
| Voxtral Small 24B | 54.1 short-form | ~120 h | ~$311 | ~$455 | ~$587 |

- Add roughly 1–3 h of fixed overhead per rental for setup, model download, and data upload (~5,000–8,000 h of mp3 is on the order of 100–300 GB at 32–96 kbps). This is arithmetic from typical bitrates; the archive's actual bitrate is unknown.
- At under ~10 GPU-hours, Parakeet throughput will likely be limited by the CPU: mp3 decode, resampling, and VAD. The GH200's 64 vCPUs help here, versus 26 on the H100 instances.
- **The GH200 is the best price/performance option on paper.** For Whisper it currently means building CTranslate2 from source or using a PyTorch Whisper stack (HF transformers or vLLM); see section 8.
- **RTX 3070 Ti alone:**
  - faster-whisper batched large-v2/v3 at ≈46–49x → **~133–141 h ≈ 5.5–6 days** for 6,500 h (4.3–7.2 days across the range).
  - Turbo batched: an estimated ~2x faster, so **~3 days**. This assumes the A100 turbo/v3 ratio carries over to consumer GPUs, which is unverified.
  - The current openai/whisper CLI at ≈5.5x (large-v2, beam 5) would need **~1,200 h ≈ 50 days**. Turbo via the CLI is faster than that, but the exact figure was not measured.
  - Parakeet TDT 0.6B on 8 GB: even at 1/10th of A100 long-form RTFx (~100x), it would take ~65 h. Local attention is required to fit 90-min files in memory.
- Recommendation implied by the numbers: rent compute only if Whisper large-v3 quality is required and the user wants results in days, not a week. Otherwise the 3070 Ti with batched turbo is sufficient. Parakeet makes the whole archive a single-evening job on any GPU.

### Gaps
- No measured H100 or GH200 RTFx for faster-whisper batched or WhisperX was found. All cloud estimates are extrapolated from A100 leaderboard numbers.
- Leaderboard long-form audio (earnings calls, TED talks, etc.) is cleaner than 1970s–2000s cassette dharma talks. WER on this archive will be higher for every model.
- Alignment and diarization overhead for WhisperX was not quantified.
- Lambda's pre-Nov-16 pricing was not visible without login. GH200 availability is also unverified.

---

## 8. Practical gotchas: decoding, resampling, memory, resumability, ARM64

### Takeaway
The biggest operational trap is the **GH200's ARM64 CPU**: CTranslate2 (and therefore faster-whisper and WhisperX) has no official CUDA aarch64 wheel. PyTorch now ships CUDA aarch64 wheels on PyPI, so NeMo, HF transformers, and vLLM are the easier choices there. Memory is not an issue for 90-minute files, as long as Parakeet uses local attention.

### Cited Findings
- No official CUDA CTranslate2 wheel exists for linux/arm64 on PyPI. The `latest-cuda` Speaches image installed a CPU-only ctranslate2 on an ARM64 DGX Spark, and the suggested fix was building from source in an NGC CUDA image — [speaches issue #620](https://github.com/speaches-ai/speaches/issues/620). This is a single user report.
- PyPI does list manylinux aarch64 ctranslate2 4.8.1 wheels for CPython 3.10–3.14, but they appear to be CPU-only — [CERN PyPI mirror](https://simple-repository.app.cern.ch/project/ctranslate2).
- PyTorch 2.11 ships CUDA-enabled aarch64 wheels on PyPI, and vLLM improved its aarch64 experience — [PyTorch KR blog](https://pytorch.kr/blog/2026/vllm-and-pytorch-improve-aarch64-experience/).
- TEN VAD has no Linux aarch64 prebuilt library — [TEN VAD](https://github.com/TEN-framework/ten-vad).
- faster-whisper decodes audio via PyAV, not the ffmpeg CLI — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper).
- Parakeet full attention is limited to ~24 min per file on an A100 80 GB. Local attention extends this to ~3 h — [NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/collections/parakeet-tdt-0.6b/).
- NFA handles 1 h+ audio subject to memory — [NFA docs](https://docs.nvidia.com/nemo/speech/latest/tools/nemo_forced_aligner.html).

### Inferences
- **Memory:** 90 min at 16 kHz mono float32 is 86.4M samples ≈ 346 MB of RAM per file, which is trivial. GPU memory is the constraint only for full-attention encoders like Parakeet. Whisper processes 30 s windows, so file length does not affect its VRAM.
- **Decoding and resampling:** decode once to 16 kHz mono (`ffmpeg -i in.mp3 -ac 1 -ar 16000 -f s16le` or PyAV). Run this in a CPU worker pool feeding the GPU process, so the GPU is not idle while ffmpeg runs. Old mp3s with VBR or bad headers should be checked first; log `ffprobe` failures instead of crashing the batch.
- **Resumability:**
  - Use one long-lived process with a manifest (CSV or SQLite) of file → status.
  - Write each output to a temp file, then rename it atomically.
  - Skip files whose output exists and is non-empty.
  - Record model, version, and parameters in a sidecar JSON. This matches the project's `transcript_raw` lineage.
  - On Lambda, sync outputs off-instance regularly, since instance storage is ephemeral.
- **Multi-worker GPU saturation:** a single faster-whisper process at batch 16 uses ~5–6 GB and may not saturate an H100. Running 4–8 worker processes per 80–96 GB GPU is the usual approach. This is unsourced practice; benchmark it.

### Gaps
- I did not verify whether the NeMo, Riva, or NIM NGC containers publish linux/arm64 images for GH200.
- I did not verify whether the current ctranslate2 aarch64 PyPI wheels include CUDA; the evidence is a single issue report.
- Silero VAD on aarch64 was not checked. It runs via PyTorch or ONNX Runtime, which should work, but this is unverified.
