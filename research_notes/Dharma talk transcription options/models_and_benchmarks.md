# English Speech-to-Text Models and Accuracy Benchmarks (as of November 8, 2026)

Scope: choosing a replacement for the naive `whisper --model turbo` CLI setup, to transcribe about 6,500 English dharma talks (5,000–8,000 hours total). The audio is mostly monologue, with old cassette transfers, hiss, room mics, chanting, bells and long silences. Available hardware is a local RTX 3070 Ti (8 GB) and rented H100 80 GB or GH200 96 GB.

Leaderboard method note: I could not render the Hugging Face Open ASR Leaderboard Space in a browser. The leaderboard numbers below come from the Space's own Gradio `/config` endpoint (the tables the page loads on start), fetched on 2026-11-08. The Space repo was last modified 2026-11-06T10:04:53Z, and the version in force is labeled "06-11-2026" (6 November 2026). These are primary-source numbers, not blog summaries. Source for all leaderboard numbers: [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard). The data sits in gated or private HF datasets (`hf-audio/open-asr-leaderboard-results`, `hf-audio/leaderboard_longform`) that I could not download directly.

---

## Q1. Current standings on the HF Open ASR Leaderboard (English short-form and long-form)

### Takeaway
In the 6 November 2026 snapshot, the top 8 short-form spots all go to proprietary APIs (Zoom Scribe v2.1 Pro leads at 4.87% average WER). The best open-weight models are NVIDIA Nemotron-3.5-Transcribe-30B-A4B (6.13%) and Qwen3-ASR-1.7B (6.15%). On the long-form track, ElevenLabs Scribe v2 leads (8.45%), and the best fully open models are a Parakeet fine-tune (9.81%), Nemotron-3.5-Transcribe (10.52%) and Cohere Transcribe (11.88%). Whisper large-v3 and large-v3-turbo rank near the bottom of the strong models on short-form (8.24% and 8.75%) but are mid-pack on long-form (13.10% and 12.82%).

### Cited Findings

**The benchmark definition changed recently, so older published numbers are not comparable:**
- The default English short-form average now covers AMI-Cleaned, Earnings22-Cleaned-AA-chunked, Gigaspeech-Cleaned, SPGISpeech, URGENT24 (noisy and reverberant), Voice Arena Monsoon (Indian-accented conversational), Voxpopuli-AA-Cleaned, Private (scripted) and Private (conversational). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Changelog: on 2 Nov 2026 LibriSpeech clean/other were removed from the default average. On 9 Oct 2026 URGENT24 was added to the average. On 26 Oct 2026 long-form was re-run on H200 with a new normalizer. On 6 Nov 2026 a normalizer fix and new Egyptian and Nigerian accent data were added. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Because of this, vendor claims made under the old metric don't line up with current numbers. Cohere claimed #1 at 5.42% on 2026-03-26 (old metric), but Cohere Transcribe is now #14 at 6.72%. Whisper large-v3 was 7.44% in Cohere's March table and is 8.24% now. — [Cohere blog](https://cohere.com/blog/transcribe); [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Third-party blogs cite conflicting "leaders": Granite Speech 4.1 2B at 5.33% (May 22, 2026 snapshot), Canary-Qwen 2.5B at 5.63%, Qwen3-ASR-1.7B at 5.40% (Oct 9, 2026). Each reflects a different metric version. — [benchmarklist.com](https://benchmarklist.com/benchmarks/open_asr_leaderboard/); [Gladia blog](https://www.gladia.io/blog/best-open-source-speech-to-text-models); [pinggy.io](https://pinggy.io/blog/best_open_source_self_hosted_speech_to_text_models/)
- RTFx means seconds of audio processed per second of compute (higher is faster). WER and RTFx come from the same inference run. — [HF Open ASR Leaderboard, About tab](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

**English short-form leaderboard, 6 Nov 2026 snapshot (selected rows; full table has 63 entries).** WER is in %, and "API" marks a proprietary entry with no RTFx. Source for every row: [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

| Rank | Model | Avg WER | RTFx | AMI-Cl | Earn22-Cl | Giga-Cl | SPGI | URGENT24 (noisy) | VA Monsoon | VoxP-Cl | Priv scripted | Priv conv |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | zoom/scribe_v2.1_pro (API) | 4.87 | API | 5.96 | 3.80 | 7.19 | 1.39 | 6.63 | 2.78 | 1.58 | 2.87 | 11.67 |
| 2 | OtterAI/speech-v3.1 (API) | 5.21 | API | 6.31 | 4.35 | 7.02 | 1.54 | 8.24 | 2.97 | 1.55 | 3.08 | 11.79 |
| 3 | microsoft/azure-speech-09-2026 (API) | 5.55 | API | 6.70 | 4.52 | 7.18 | 2.30 | 9.26 | 3.18 | 1.36 | 2.22 | 13.21 |
| 5 | elevenlabs/scribe_v2 (API) | 5.93 | API | 8.20 | 4.80 | 7.64 | 3.02 | 9.20 | 3.32 | 1.41 | 3.03 | 12.77 |
| 9 | nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B (open) | 6.13 | 472.6 | 7.78 | 5.25 | 7.18 | 1.91 | 10.94 | 3.63 | 1.89 | 3.58 | 13.01 |
| 10 | Qwen/Qwen3-ASR-1.7B (open) | 6.15 | 835.6 | 8.31 | 5.84 | 7.22 | 2.57 | 9.93 | 3.50 | 2.85 | 2.87 | 12.29 |
| 11 | assemblyai/universal-3-5-pro (API) | 6.21 | API | 10.63 | 6.05 | 7.62 | 1.81 | 9.08 | 3.49 | 1.92 | 2.67 | 12.62 |
| 13 | ibm-granite/granite-speech-5.0-2b (open) | 6.68 | 548.4 | 6.96 | 6.22 | 8.14 | 3.36 | 10.22 | 3.94 | 3.52 | 3.16 | 14.56 |
| 14 | CohereLabs/cohere-transcribe-03-2026 (open, gated) | 6.72 | 923.7 | 7.02 | 7.88 | 7.88 | 2.74 | 9.50 | 3.44 | 5.38 | 3.20 | 13.42 |
| 16 | TheStageAI/thewhisper-large-v3-turbo (optimized Whisper) | 6.74 | 1183.9 | 7.32 | 7.18 | 7.84 | 1.62 | 10.82 | 3.72 | 4.02 | 3.93 | 14.25 |
| 18 | openai/gpt-transcribe (API) | 6.80 | API | 8.95 | 6.61 | 7.76 | 2.23 | 12.86 | 3.63 | 2.65 | 3.24 | 13.28 |
| 21 | nvidia/parakeet-tdt-0.6b-v2 (fast-gpu-asr decoding) | 6.91 | 17254 | 9.03 | 6.84 | 8.16 | 1.87 | 11.64 | 3.72 | 3.85 | 3.48 | 13.62 |
| 23 | nvidia/canary-qwen-2.5b (open) | 6.92 | 881.7 | 7.91 | 6.41 | 7.80 | 1.70 | 13.02 | 3.60 | 4.14 | 3.47 | 14.19 |
| 25 | nvidia/parakeet-tdt-0.6b-v2 (NeMo default) | 6.93 | 6148 | 9.09 | 6.76 | 8.15 | 1.94 | 11.42 | 3.89 | 3.78 | 3.63 | 13.70 |
| 27 | ibm-granite/granite-speech-5.0-470m-turboctc-nc | 6.98 | 21082 | 7.31 | 8.23 | 8.37 | 1.75 | 10.22 | 4.30 | 4.67 | 3.81 | 14.14 |
| 29 | meta/muse-voice-transcribe (API) | 7.00 | API | 9.20 | 6.01 | 7.75 | 3.21 | 13.03 | 4.16 | 2.02 | 4.52 | 13.07 |
| 30 | ibm-granite/granite-speech-4.1-2b | 7.03 | 546.8 | 7.06 | 6.69 | 8.18 | 3.47 | 11.25 | 4.12 | 4.18 | 3.16 | 15.17 |
| 31 | nvidia/parakeet-tdt-0.6b-v3 | 7.04 | 6322 | 9.42 | 5.85 | 7.99 | 3.63 | 11.52 | 4.14 | 3.05 | 4.27 | 13.53 |
| 33 | Qwen/Qwen3-ASR-0.6B | 7.07 | 749.5 | 9.33 | 7.83 | 7.62 | 2.74 | 11.56 | 4.23 | 2.90 | 3.92 | 13.47 |
| 35 | ibm-granite/granite-speech-5.0-470m-turboctc | 7.41 | 21435 | 7.71 | 6.75 | 8.74 | 3.22 | 11.79 | 4.75 | 4.90 | 4.13 | 14.69 |
| 36 | mistralai/Voxtral-Small-24B-2507 | 7.44 | 101.5 | 13.25 | 7.07 | 8.32 | 1.84 | 12.34 | 3.49 | 2.00 | 3.22 | 15.46 |
| 37 | nvidia/nemotron-speech-streaming-en-0.6b | 7.47 | 1116 | 8.84 | 9.45 | 7.90 | 2.69 | 12.54 | 4.44 | 2.40 | 4.79 | 14.21 |
| 38 | distil-whisper/distil-large-v3.5 | 7.57 | 898.2 | 12.09 | 7.70 | 8.21 | 2.62 | 12.42 | 3.60 | 2.52 | 4.34 | 14.62 |
| 39 | ibm-granite/granite-4.0-1b-speech | 7.69 | 667.0 | 7.38 | 8.53 | 8.44 | 3.55 | 11.99 | 4.84 | 4.41 | 3.56 | 16.52 |
| 42 | openai/whisper-large-v3 | 8.24 | 470.7 | 13.63 | 7.99 | 8.35 | 2.71 | 13.73 | 3.95 | 4.53 | 3.60 | 15.66 |
| 43 | mistralai/Voxtral-Mini-3B-2507 | 8.32 | 179.8 | 13.57 | 7.66 | 8.70 | 2.15 | 15.66 | 4.90 | 2.22 | 3.78 | 16.24 |
| 44 | nvidia/canary-1b-v2 | 8.43 | 1854 | 13.03 | 7.28 | 9.12 | 2.03 | 14.56 | 4.97 | 4.39 | 4.66 | 15.84 |
| 47 | openai/whisper-large-v3-turbo | 8.75 | 808.9 | 13.88 | 8.09 | 8.47 | 2.79 | 13.69 | 4.77 | 7.02 | 4.06 | 15.95 |
| 51 | microsoft/VibeVoice-ASR-HF | 9.54 | 217.9 | 12.02 | 7.97 | 7.87 | 3.47 | 19.50 | 4.74 | 2.02 | 11.09 | 17.17 |
| 52 | mistralai/Voxtral-Mini-4B-Realtime-2602 | 9.72 | 103.5 | 13.34 | 9.31 | 8.80 | 2.23 | 17.94 | 8.86 | 2.60 | 5.76 | 18.64 |
| 59 | google/gemma-4-E4B-it | 13.20 | 160.7 | 20.57 | 14.16 | 11.74 | 5.49 | 26.38 | 6.19 | 4.09 | 8.88 | 21.34 |

- Other new 2026 open entries are on the board but less established: Edge0/ARK-ASR-0.6B (6.75), HojoAI/Hojo-ASR-V1 (6.74, RTFx 73), OpenMOSS MOSS-Transcribe-Diarize (6.91), bosonai/higgs-audio-v3-stt (6.98), FermionResearch/Phonon-2 (7.86), facebook/omniASR-LLM-7B-v2 (9.45), FunAudioLLM Fun-ASR-Nano (8.54), futo-org/asr4all-l/m/s (9.97–13.97, RTFx 21k–41k), and abr-ai/niagara (9–84M params, 10.9–17.9). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

**Long-form leaderboard, 6 Nov 2026 snapshot (all 14 entries).** Datasets: Earnings21 (39 h), Earnings22 (119 h), CORAAL (159 h of sociolinguistic interviews). Re-run on H200 with a new normalizer on 26 Oct 2026. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

| Rank | Model | Avg WER | RTFx | Earnings21 | Earnings22 | CORAAL |
|---|---|---|---|---|---|---|
| 1 | elevenlabs/scribe_v2 (API) | 8.45 | API | 6.19 | 9.70 | 9.47 |
| 2 | reson8/resonant-1 (API) | 9.74 | API | 6.73 | 10.19 | 12.30 |
| 3 | freetranscribe/parakeet-ft-v1 | 9.81 | 985.8 | 6.98 | 10.09 | 12.35 |
| 4 | nvidia/Nemotron-3.5-Transcribe-30B-A4B | 10.52 | 110.5 | 7.16 | 10.48 | 13.93 |
| 5 | assemblyai/universal-3-5-pro (API) | 10.76 | API | 8.26 | 10.95 | 13.08 |
| 6 | CohereLabs/cohere-transcribe-03-2026 | 11.88 | 492.9 | 8.31 | 13.01 | 14.33 |
| 7 | openai/gpt-transcribe (API) | 12.10 | API | 8.67 | 12.17 | 15.47 |
| 8 | nvidia/parakeet-tdt-0.6b-v3 | 12.60 | 1419.1 | 9.72 | 13.61 | 14.47 |
| 9 | openai/whisper-large-v3-turbo | 12.82 | 373.8 | 9.28 | 12.64 | 16.54 |
| 10 | nvidia/canary-qwen-2.5b | 12.94 | 666.0 | 9.71 | 11.96 | 17.16 |
| 11 | nvidia/parakeet-tdt-0.6b-v2 | 13.08 | 1475.9 | 10.22 | 12.69 | 16.33 |
| 12 | openai/whisper-large-v3 | 13.10 | 162.0 | 9.20 | 12.58 | 17.52 |
| 13 | TheStageAI/thewhisper-large-v3-turbo | 13.18 | 2555.7 | 9.72 | 11.86 | 17.95 |
| 14 | distil-whisper/distil-large-v3.5 | 13.31 | 425.7 | 10.12 | 13.48 | 16.33 |

- Many strong short-form open models (Qwen3-ASR, Granite Speech 5.0, Voxtral, Kyutai) have no long-form entry, so they cannot be compared on this track. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- NVIDIA's own card reports a long-form mean WER of 10.98 for Nemotron 3.5 Transcribe and 13.37 for Parakeet-TDT-0.6B-v3. The current leaderboard shows 10.52 and 12.60. The difference is likely the pre- versus post-26-Oct normalizer. — [Nemotron-3.5-Transcribe model card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)

**Private (held-out) data tab, which resists benchmark overfitting:**
- This tab uses non-public scripted and conversational data from Appen, DataoceanAI, Voice Arena and Liva AI (US, UK, AU, CA, IN, NG and EG accents), introduced "to address risks of overfitting to public datasets." — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Private-data average WER: Zoom 7.27, Otter 7.43, p99lab audrey 7.49, **Qwen3-ASR-1.7B 7.58 (best open, #4 overall)**, AssemblyAI U-3.5 Pro 7.64, Azure 7.72, ElevenLabs 7.90, gpt-transcribe 8.26, Nemotron-3.5-Transcribe 8.29, Cohere 8.31, Parakeet v2 8.66, Canary-Qwen 8.83, Granite 5.0-2b 8.86, Parakeet v3 8.90, Whisper large-v3 9.63, Whisper large-v3-turbo 10.00, VibeVoice-ASR 14.13. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- A "benchmark fitting" tab, built with Hume AI, measures how often models reproduce known VoxPopuli reference errors and copy dataset spelling conventions. The leaderboard warns that a high score "does not imply that a model trained on the test set." — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [Hume AI technical report, arXiv 2608.19936](https://arxiv.org/pdf/2608.19936)

### Inferences
- For a lecture monologue, the most relevant columns are Private (scripted), Earnings22 (oratory, long-form), Voxpopuli (parliamentary oratory) and URGENT24 (noise and reverb). On these, Qwen3-ASR-1.7B, Nemotron-3.5-Transcribe, Cohere Transcribe and Granite 5.0 are clearly ahead of Whisper. The gap between Parakeet and Whisper on monologue is small on scripted speech and larger on noise.
- The gap from Whisper turbo to the best open models is about 2.6 WER points absolute on short-form (8.75 to 6.13). On long-form it is only about 2.3 points (12.82 to 10.52), and the Whisper turbo baseline is already better than Parakeet v2 and Canary-Qwen there. Moving to a better long-form *pipeline* (VAD, chunking, decoding settings) may matter about as much as switching models.
- Qwen3-ASR-1.7B's strong private-data score suggests its public-benchmark ranking is not just overfitting.

### Gaps
- The leaderboard's underlying CSVs are in gated or private HF datasets, so I captured only the rendered default view (default datasets, default version). Columns not in the default view, such as URGENT24-Clean, LibriSpeech and accent splits, were not extracted.
- The leaderboard does not state which GPU the short-form RTFx numbers were measured on. The changelog mentions only that long-form was moved to H200. RTFx values across entries may not be strictly comparable.
- The leaderboard paper ([arXiv 2510.06961](https://arxiv.org/html/2510.06961v1)) reflects an October 2025 state and was not re-read for this snapshot.

---

## Q2. Open-weight candidates: specs, long-form handling, and suitability

### Takeaway
Three open models stand out for this project. **NVIDIA Parakeet-TDT-0.6B v2/v3** is tiny, extremely fast, natively punctuated, has word timestamps, and processes 24 minutes in one pass (up to 3 hours with local attention). It fits easily on the 3070 Ti. **Qwen3-ASR-1.7B** is the best open accuracy on held-out data (Apache 2.0) and needs a separate forced aligner for timestamps. **NVIDIA Nemotron-3.5-Transcribe-30B-A4B** (released 28 Oct 2026) is the best open long-form model, accepts 1-hour inputs with word timestamps, and needs an H100-class GPU. Whisper large-v3 and turbo are now mid-to-low tier on accuracy and have the worst hallucination profile.

### Cited Findings

**Master comparison table (open-weight).** WER figures are from the 6 Nov 2026 leaderboard unless noted. "—" means not found.

| Model | Params / arch | License | Short-form avg WER / RTFx | Long-form avg WER | Punct + case | Timestamps | Max input / long-form method | VRAM / hardware | Known weaknesses | Sources |
|---|---|---|---|---|---|---|---|---|---|---|
| Whisper large-v3 | 1.55B enc-dec (AED) | MIT | 8.24 / 471 | 13.10 | Native | Segment and word (cross-attention DTW) | 30 s receptive field; sequential sliding window or chunked + stitch | — | Hallucination on non-speech; poor on AMI (13.6) | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [turbo card](https://huggingface.co/openai/whisper-large-v3-turbo) |
| Whisper large-v3-turbo (current setup) | ~809M (4-layer decoder) | MIT | 8.75 / 809 | 12.82 | Native | Segment and word | 30 s; card says sequential is "up to 0.5% WER more accurate" than chunked for batches of long files | — | Same as large-v3; worst VoxPopuli (7.02) | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/openai/whisper-large-v3-turbo) |
| Distil-Whisper distil-large-v3.5 | distilled Whisper | MIT (assumed, not verified) | 7.57 / 898 | 13.31 | Native | Yes | 30 s chunks | — | Highest "benchmark fitting" rates among those listed | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| CrisperWhisper (v1) | Whisper large-v3 fine-tune | **CC-BY-NC-4.0** | not on current LB | — | Verbatim (keeps fillers) | Precise word-level (DTW + attention loss) | 30 s chunks | — | Non-commercial; v1 superseded by CrisperWhisper 2.0 | [card](https://huggingface.co/nyrahealth/CrisperWhisper) |
| Parakeet-TDT-0.6B-v2 | 600M FastConformer + TDT | CC-BY-4.0 | 6.93 / 6148 (6.91 / 17254 with fast-gpu-asr) | 13.08 | Native | Char, word and segment | 24 min single pass (full attention) | "At least 2GB RAM" to load; larger memory for longer audio | Weaker on AMI (9.1) and noisy URGENT24 (11.4) | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) |
| Parakeet-TDT-0.6B-v3 | 600M, 25 European languages | CC-BY-4.0 | 7.04 / 6322 | 12.60 | Native | Word and segment | 24 min with full attention (on A100 80 GB) or **up to 3 h with local attention** (`rel_pos_local_attn`, context [256,256]) | Small | Slightly worse English than v2 on short-form | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) |
| Canary-Qwen-2.5B | FastConformer encoder + Qwen LLM (SALM), released 17 Jul 2025 | CC-BY-4.0 | 6.92 / 882 (card: 418 RTFx) | 12.94 | Native (trained on P&C transcripts) | — (not found on card) | — | — | 138.1 chars/min hallucinated on MUSAN non-speech (card) | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/nvidia/canary-qwen-2.5b) |
| Canary-1B-v2 | 1B AED, multilingual | CC-BY-4.0 (assumed per NVIDIA series; not verified) | 8.43 / 1854 | — | Native | — | — | — | Weak on AMI (13.0) | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| **Nemotron-3.5-Transcribe-30B-A4B** (28 Oct 2026) | 34B total / 4.3B active MoE SALM | **OpenMDW-1.1** | 6.13 / 473 | **10.52** | Prompt-controlled (verbatim or "readable" with fillers removed) | Optional word timestamps (CTC timestamp middleware) | **Up to 1 hour**, 65,536-token context | "1× H100 80 GB"; FP8 on L40S 48 GB; NVFP4 on RTX 5090 | Card lists "substitutions, deletions, repetitions, hallucinated speech"; trained with no-speech abstention data | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B) |
| Qwen3-ASR-1.7B | 1.7B LLM-based | Apache-2.0 | 6.15 / 836 | not on LB | Native | Via separate Qwen3-ForcedAligner-0.6B ("up to 5 minutes of speech") | — (max ASR length not captured) | vLLM batch; FlashAttention 2 recommended | No native timestamps; streaming mode has no timestamps | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) |
| Qwen3-ASR-0.6B | 0.6B | Apache-2.0 | 7.07 / 750 | — | Native | Same aligner | — | Small | — | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| Cohere Transcribe (03-2026) | 2B Conformer enc + light Transformer dec | Apache-2.0, **gated** | 6.72 / 924 | 11.88 | Native (not detailed) | **No timestamps** (per VentureBeat) | — | "Manageable" (no number given) | No timestamps, no diarization, no auto language ID | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [Cohere](https://cohere.com/blog/transcribe); [VentureBeat](https://venturebeat.com/orchestration/coheres-open-weight-asr-model-hits-5-4-word-error-rate-low-enough-to-replace) |
| IBM Granite Speech 5.0 2B (20 Oct 2026) | 2B speech-LLM | Apache-2.0 | 6.68 / 548 | not on LB | Native via prompt; PER and Cap-F1 published | — | **~2 minutes per segment**; split longer audio with VAD | GGUF Q8_0 is 3.2 GB (Ollama `ibm/granite5-speech`); lower-bit quants "lose accuracy on audio longer than about a minute" | Needs external segmentation | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b) |
| IBM Granite Speech 5.0 470M TurboCTC (21 Oct 2026) | 470M CTC Conformer, block attention (128 frames) | Apache-2.0 (the "-nc" LB variant's license is unclear) | 7.41 / 21435 (nc: 6.98 / 21082) | — | **Native P&C** | — | Block attention | Edge-friendly | Emits `<|nospeech|>` on silence; trained with 43 h MUSAN noise and music with empty targets | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/ibm-granite/granite-speech-5.0-470m-turboctc) |
| Voxtral Small 24B (2507) | 24B audio-LLM | Apache-2.0 | 7.44 / 101 | — | Native | — | 32k context, **up to 30 min** for transcription | **~55 GB** GPU RAM in bf16/fp16 | Poor AMI (13.25); slow | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507) |
| Voxtral Mini 3B (2507) | 3B | Apache-2.0 (assumed; not verified) | 8.32 / 180 | — | Native | — | — | — | — | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| Microsoft VibeVoice-ASR | LLM-based, 50+ languages | MIT | 9.54 / 218 | — | Native | Yes, plus speaker diarization (JSON output) | **60 min single pass** (64K tokens; 60 s tokenizer chunks with cached conv states) | Tokenizer chunk is tunable for OOM | Weak: 11.09 private scripted, 19.5 URGENT24 | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [card](https://huggingface.co/microsoft/VibeVoice-ASR-HF) |
| Kyutai STT 2.6B en | 2.6B streaming (2.5 s delay) | CC-BY-4.0 | 6.40 (Cohere's March 2026 table, old metric); not in current default LB | — | Native | Yes (text-stream offset) | "Perform[s] well with audio as long as 2 hours with no additional changes" | — | Pseudo-labels came from whisper-timestamped | [card](https://huggingface.co/kyutai/stt-2.6b-en); [Cohere](https://cohere.com/blog/transcribe) |
| Google Gemma-4-E4B-it (general multimodal) | ~4B effective | — | 13.20 / 161 | — | — | — | — | — | Far behind dedicated ASR | [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |

- Whisper's long-form algorithms: "Sequential" uses a sliding window that transcribes 30-second slices one after the other. "Chunked" splits audio with overlap and stitches the results. For batches of long files, sequential has comparable latency and is "up to 0.5% WER more accurate." — [Whisper large-v3-turbo card](https://huggingface.co/openai/whisper-large-v3-turbo)
- Parakeet v2 is "trained with full attention, enabling efficient transcription of audio segments up to 24 minutes in a single pass," with an RTFx of 3380 at batch size 128 per the card. — [Parakeet-TDT-0.6B-v2 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)
- Nemotron 3.5 Transcribe offers prompt templates for "Readable text" (omit fillers and accidental repetitions) versus "verbatim," plus speaker tags and context-term biasing ("Context terms: <names and terms>"). — [Nemotron-3.5-Transcribe card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- On one RTX PRO 6000 Blackwell, NVIDIA's NIM serving stack transcribes up to 2,238 seconds of audio per second (NVFP4 with speculative decoding). This is a vendor-measured figure. — [Nemotron-3.5-Transcribe card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- Granite Speech 5.0 2B: "For best results, transcribe audio in segments of up to ~2 minutes; split longer recordings (e.g. with VAD) before decoding." — [Granite Speech 5.0 2B card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b)
- Cohere Transcribe claims 61% average human-preference win rate in English (vendor-run). — [Cohere blog](https://cohere.com/blog/transcribe)

### Inferences
- Dharma-talk lengths (30–90 min) exceed the single-pass windows of Parakeet with full attention (24 min), Voxtral (30 min) and Granite (~2 min). Every candidate except Nemotron 3.5 (1 h), VibeVoice (1 h), Kyutai (~2 h claimed) and Parakeet with local attention (3 h) will need VAD-based segmentation. VAD segmentation also solves the silence and hallucination problem, so it is worth doing regardless.
- On the 3070 Ti (8 GB): Parakeet 0.6B, Qwen3-ASR-0.6B/1.7B, Granite 5.0 (Q8 GGUF 3.2 GB) and Whisper turbo should fit. This is inferred from parameter counts and the published GGUF size; I did not verify VRAM per model. Nemotron-3.5 (34B total) and Voxtral Small (~55 GB) need the rented H100/GH200.
- Throughput is not a bottleneck for any modern model. At RTFx about 500 (Nemotron long-form RTFx is 110 on H200), 6,500 h of audio takes about 13 GPU-hours at RTFx 500, or about 59 GPU-hours at RTFx 110. Parakeet at RTFx over 1,000 takes under 7 GPU-hours. These are rough figures from leaderboard RTFx, which uses batched, optimized inference; real pipelines with VAD and I/O will be slower.
- Licenses: Whisper (MIT), Qwen3-ASR, Granite and Voxtral (Apache-2.0), and Parakeet, Canary and Kyutai (CC-BY-4.0, attribution required) are all permissive. CrisperWhisper is non-commercial. Nemotron uses OpenMDW-1.1, whose terms I did not review. Cohere is Apache-2.0 but gated.

### Gaps
- I couldn't find Canary-Qwen-2.5B's maximum input length or timestamp support, or Qwen3-ASR's maximum single-pass audio length (the card text I extracted didn't state it).
- I didn't find a primary VRAM figure for Whisper large-v3/turbo, Qwen3-ASR or Cohere.
- I didn't find Microsoft Phi-4-multimodal, Qwen2.5-Omni, Kimi-Audio or Moonshine in the current default leaderboard view, and didn't research them further. They appear to be superseded for pure English ASR (inference from their absence among top entries).
- I didn't check CrisperWhisper 2.0's license or benchmarks.
- I didn't review what "freetranscribe/parakeet-ft-v1" is (#3 on long-form): its license, training data and provenance.

---

## Q3. Hallucination behavior (silence, music, repetition loops, dropped content)

### Takeaway
Whisper's autoregressive decoder hallucinates on non-speech audio. One 2026 paper cites large-v3 producing non-empty text for 40.3% of non-speech inputs. This is well documented, and it gets worse past 30 s. CTC and transducer models (Parakeet, Granite TurboCTC) are widely reported to stay silent on non-speech, and newer models are explicitly trained with empty-target noise and music. However, I found no rigorous head-to-head benchmark against Whisper on silence. LLM-based ASR (Canary-Qwen, Nemotron, Voxtral, Qwen3-ASR) can also hallucinate.

### Cited Findings
- "Careless Whisper" (cited via Calm-Whisper) found about 1% of Whisper transcriptions contain hallucinated content absent from the audio. — [Calm-Whisper, arXiv 2505.12969](https://arxiv.org/html/2505.12969v1)
- Calm-Whisper (Interspeech 2025) finds that a few specific decoder self-attention heads cause most non-speech hallucination. Fine-tuning only those heads on non-speech audio with blank labels cut non-speech hallucination by over 80%, with under 0.1% WER degradation on LibriSpeech. — [Calm-Whisper, arXiv 2505.12969](https://arxiv.org/html/2505.12969v1); [ISCA archive](https://www.isca-archive.org/interspeech_2025/wang25b_interspeech.html)
- "Investigation of Whisper ASR Hallucinations Induced by Non-Speech Audio" built a "Bag of Hallucinations" of frequent stock phrases for detection and post-filtering. It found hallucination rates rise noticeably for inputs longer than 30 seconds. — [arXiv 2501.11378](https://arxiv.org/html/2501.11378v1)
- A 2026 paper reports Whisper large-v3 produced non-empty transcripts for 40.3% of non-speech inputs (citing Barański et al., 2025), often as stock phrases or fillers. — [Hallucination Space Projection, arXiv 2609.04561](https://arxiv.org/pdf/2609.04561)
- Canary-Qwen-2.5B's card reports 138.1 hallucinated characters per minute on the 48 h MUSAN non-speech eval set. — [Canary-Qwen-2.5B card](https://huggingface.co/nvidia/canary-qwen-2.5b)
- Granite Speech 5.0 TurboCTC was trained with 43 h of MUSAN noise and music with empty targets. On silence or non-speech, transcribe.cpp returns a `<|nospeech|>` control token. — [Granite 5.0 TurboCTC card](https://huggingface.co/ibm-granite/granite-speech-5.0-470m-turboctc)
- Nemotron 3.5 Transcribe training includes "no-speech abstention data" from AudioSet with empty-response targets. Its card still lists "repetitions, hallucinated speech" among error types and recommends "targeted testing ... for long recordings, ... noise." — [Nemotron-3.5-Transcribe card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- Claims that transducer and CTC models like Parakeet "stay quiet during silence" come from practitioner blogs and forum posts. One blog explicitly says it has not measured this against Whisper's failure modes. — [ModelsLab blog](https://modelslab.com/blog/audio-generation/parakeet-cpp-vs-whisper-self-hosted-asr-comparison-2026); [dev.to on Whisper silence loops](https://dev.to/nareshipme/whisper-hallucination-on-silence-why-your-transcript-loops-the-same-phrase-2pg4)
- An NVIDIA technical report on Canary-1B-v2 / Parakeet-TDT-0.6B-v3 ([arXiv 2509.14128](https://arxiv.org/abs/2509.14128v2)) came up in searches about hallucination. I didn't fetch it, so I can't confirm its findings on non-speech.

### Inferences
- Dharma talks have long silences, bells, chanting and meditation periods. With Whisper, these are high-risk for stock-phrase insertions ("Thank you for watching") and repetition loops. The current `whisper` CLI with default settings (temperature fallback, condition_on_previous_text) is prone to loops; this is general knowledge, not verified for this note. At minimum, a VAD pre-gate (e.g., Silero), with non-speech regions dropped before ASR, plus "bag of hallucinations" post-filtering would help.
- A CTC/TDT model (Parakeet, Granite TurboCTC) is structurally less prone to inventing text because it emits per-frame labels rather than free-running generation. But it can *drop* quiet or degraded speech. Chanting may come out as gibberish or nothing either way.
- For LLM-based ASR (Qwen3-ASR, Nemotron, Canary-Qwen, Voxtral), hallucination risk sits between the two. Test on the archive's own silence and chant segments.

### Gaps
- No peer-reviewed benchmark I found directly compares Parakeet or other CTC/TDT models with Whisper on silence, music or chanting.
- I didn't fetch the original Careless Whisper paper (Koenecke et al., FAccT 2024). Details beyond the about-1% figure (such as the share of harmful hallucinations and the link to longer non-vocal durations) are not verified here.
- I didn't find quantitative data on content *dropping* (deletions) on long-form audio for any model.

---

## Q4. Robustness to noisy, degraded or old recordings

### Takeaway
No public benchmark captures cassette-era hiss and wow/flutter. The closest proxies are URGENT24 (added noise and room reverb), AMI (distant mics), CORAAL (sociolinguistic interview recordings, partly older) and the earnings sets. On URGENT24, proprietary APIs lead (Zoom 6.63). Among open models, Cohere (9.50), Qwen3-ASR-1.7B (9.93) and Granite 5.0 (10.22) clearly beat Whisper large-v3 and turbo (about 13.7).

### Cited Findings
- URGENT24 is 1.92 h of speech from Common Voice, LibriTTS, VCTK and CC-licensed YouTube podcasts, overlaid with WHAM!, DEMAND and TUT noise plus room impulse responses. The noisy variant is research and non-commercial use only. — [HF Open ASR Leaderboard, About tab](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- URGENT24 WER: Zoom 6.63, Otter 8.24, AssemblyAI 9.08, ElevenLabs 9.20, Azure 9.26, Cohere 9.50, Qwen3-ASR-1.7B 9.93, Granite 5.0-2b 10.22, Granite TurboCTC-nc 10.22, Nemotron-3.5 10.94, Parakeet v2 11.42, Parakeet v3 11.52, Voxtral Small 12.34, gpt-transcribe 12.86, Canary-Qwen 13.02, Whisper large-v3-turbo 13.69, Whisper large-v3 13.73, VibeVoice 19.50. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- CORAAL (long-form; 159 h sociolinguistic interviews, CC-BY-NC-4.0) WER: ElevenLabs 9.47, AssemblyAI 13.08, Nemotron 13.93, Cohere 14.33, Parakeet v3 14.47, Whisper turbo 16.54, Whisper large-v3 17.52, Canary-Qwen 17.16. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Canary-Qwen-2.5B on LibriSpeech test-clean with additive white noise: 2.41% at 10 dB SNR, 4.08% at 5 dB, 9.83% at 0 dB, 30.60% at -5 dB (vendor-measured). — [Canary-Qwen-2.5B card](https://huggingface.co/nvidia/canary-qwen-2.5b)
- IBM claims Granite 5.0-2b adds "increased robustness to noise, reverberation and distant microphone speech" over 4.1 (vendor claim). — [Granite Speech 5.0 2B card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b)
- Kyutai's card says its STT is "robust to noisy conditions" (vendor claim, no numbers). — [Kyutai STT 2.6B card](https://huggingface.co/kyutai/stt-2.6b-en)
- TED-LIUM is no longer in the default leaderboard average. In Cohere's March 2026 table, Cohere scored 2.49 on TED-LIUM. — [Cohere blog](https://cohere.com/blog/transcribe)

### Inferences
- Earnings22 and Earnings21 (single-speaker-dominated oratory over telephone-quality audio) plus CORAAL (older field recordings) are probably the best public proxies for degraded lecture audio. On those, Nemotron-3.5, Cohere and Parakeet v3 beat Whisper by 1–3 WER points.
- Since no benchmark matches the archive, a small in-domain eval is warranted: about 20–30 representative excerpts across decades and recording types, hand-corrected. Dharma vocabulary (Sanskrit/Pali/Japanese terms, teacher names) is a separate error source that context-biasing models can help with (Nemotron context terms, Qwen3-ASR, AssemblyAI keyterms).
- Speech enhancement or denoising before ASR can *hurt* modern ASR. This is general knowledge, not sourced here, and should be tested rather than assumed.

### Gaps
- No public benchmark specifically covers tape-transferred or analog-degraded audio, chanting, or Buddhist-domain vocabulary.
- CHiME-specific results for the current models weren't found in this pass.
- Robustness numbers for hosted APIs beyond URGENT24 and CORAAL are vendor-reported only.

---

## Q5. Punctuation and casing: native vs separate model

### Takeaway
Every current candidate emits punctuated, cased text natively: Whisper, Parakeet v2/v3, Canary, Granite (including the 470M CTC), Qwen3-ASR, Nemotron, Voxtral, Kyutai and Cohere. A separate punctuation model is no longer needed. The leaderboard WER is computed after normalization, so it does **not** measure punctuation quality. Only IBM publishes punctuation-specific metrics.

### Cited Findings
- Parakeet v2/v3 output "Punctuations and Capitalizations included." The v3 card's WER chart "does not include Punctuation and Capitalisation errors." — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3); [Parakeet v2 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)
- Canary-Qwen-2.5B "training transcripts contained punctuation and capitalization." — [Canary-Qwen card](https://huggingface.co/nvidia/canary-qwen-2.5b)
- Granite 5.0-2b publishes punctuation error rate (PER) and capitalization F1 (LibriSpeech-PC definitions). On Earnings-22, PER is 21.64 and Cap-F1 is 94.98. On LibriSpeech clean, PER is 23.20 and Cap-F1 is 90.16. — [Granite Speech 5.0 2B card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b)
- Granite TurboCTC 470M "outputs punctuated and capitalized transcripts" despite being CTC. — [Granite 5.0 TurboCTC card](https://huggingface.co/ibm-granite/granite-speech-5.0-470m-turboctc)
- Kyutai STT "produces transcripts with capitalization and punctuation." — [Kyutai card](https://huggingface.co/kyutai/stt-2.6b-en)
- Nemotron 3.5 controls punctuation, casing, number formatting and filler removal through the prompt. — [Nemotron-3.5-Transcribe card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- CrisperWhisper is designed for verbatim output (keeps disfluencies), unlike Whisper's "intended" transcription style. — [CrisperWhisper card](https://huggingface.co/nyrahealth/CrisperWhisper)

### Inferences
- The project already has an LLM cleanup and structuring stage (Llama). With any modern ASR, that stage can focus on paragraphing and domain-term correction rather than restoring punctuation. A "readable" mode (Nemotron) or an LLM-decoder ASR may reduce how much cleanup is needed, but it also reduces the likeness score that `likeness.py` relies on.
- For segment-level paragraphs and timestamps, Parakeet's segment timestamps or Whisper's segments map naturally onto the existing pipeline.

### Gaps
- No cross-model, apples-to-apples punctuation and casing benchmark was found. The HF leaderboard normalizes text before scoring.

---

## Q6. Hosted APIs: accuracy and cost for about 6,500 hours

### Takeaway
Batch prices (fetched from vendor pages on 2026-11-08) range from $0.04/h (Groq Whisper turbo) to about $0.38/h (Speechmatics Enhanced). For 6,500 h, mainstream high-accuracy APIs cost roughly **$800–$2,500 total**. The most accurate on the leaderboard: ElevenLabs Scribe v2 is #1 on long-form (8.45) at $0.22/h, about $1,430. AssemblyAI Universal-3.5 Pro is $0.21/h, about $1,365. OpenAI gpt-transcribe is $0.27/h, about $1,755. Self-hosting an open model on a rented H100 is likely an order of magnitude cheaper in compute, but costs engineering time.

### Cited Findings

**Batch / pre-recorded list prices and leaderboard accuracy.** Cost columns are simple multiplication (5,000 / 6,500 / 8,000 h) before volume discounts and add-ons.

| Provider / model | Batch price | ≈$/h | 5,000 h | 6,500 h | 8,000 h | LB short avg | LB long avg | Source |
|---|---|---|---|---|---|---|---|---|
| Groq whisper-large-v3-turbo | $0.04/h | 0.04 | $200 | $260 | $320 | (≈ Whisper turbo: 8.75 / 12.82) | | [Groq pricing per search summary](https://groq.com/pricing); [morphllm](https://www.morphllm.com/groq-pricing) |
| Groq whisper-large-v3 | $0.111/h | 0.111 | $555 | $722 | $888 | (≈ 8.24 / 13.10) | | same |
| Speechmatics Melia 1 (multilingual) | $0.12/h | 0.12 | $600 | $780 | $960 | not on LB | | [Speechmatics pricing](https://www.speechmatics.com/pricing) |
| AssemblyAI Universal-2 | $0.15/h | 0.15 | $750 | $975 | $1,200 | not on LB | | [AssemblyAI pricing](https://www.assemblyai.com/pricing) |
| OpenAI gpt-4o-mini-transcribe | $0.003/min | 0.18 | $900 | $1,170 | $1,440 | not on LB | | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) |
| Google Cloud STT V2 "Dynamic Batch" Standard | $0.003/min | 0.18 | $900 | $1,170 | $1,440 | not on LB | | [Google Cloud STT pricing](https://cloud.google.com/speech-to-text/pricing) |
| Rev.ai Reverb | $0.20/h | 0.20 | $1,000 | $1,300 | $1,600 | not on LB | | [Rev.ai pricing](https://www.rev.ai/pricing) |
| AssemblyAI Universal-3.5 Pro | $0.21/h | 0.21 | $1,050 | $1,365 | $1,680 | 6.21 (#11) | 10.76 | [AssemblyAI pricing](https://www.assemblyai.com/pricing); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| ElevenLabs Scribe v2 | $0.22/h | 0.22 | $1,100 | $1,430 | $1,760 | 5.93 (#5) | **8.45 (#1)** | [ElevenLabs API pricing](https://elevenlabs.io/pricing/api); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| Speechmatics Standard | $0.23/h | 0.23 | $1,150 | $1,495 | $1,840 | not on LB | | [Speechmatics pricing](https://www.speechmatics.com/pricing) |
| OpenAI gpt-transcribe | $0.0045/min | 0.27 | $1,350 | $1,755 | $2,160 | 6.80 (#18) | 12.10 | [OpenAI pricing](https://developers.openai.com/api/docs/pricing); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) |
| Rev.ai Whisper Large | $0.005/min | 0.30 | $1,500 | $1,950 | $2,400 | (Whisper) | | [Rev.ai pricing](https://www.rev.ai/pricing) |
| OpenAI gpt-4o-transcribe | $0.006/min | 0.36 | $1,800 | $2,340 | $2,880 | not on LB | | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) |
| Speechmatics Enhanced | $0.38/h | 0.38 | $1,900 | $2,470 | $3,040 | not on LB | | [Speechmatics pricing](https://www.speechmatics.com/pricing) |
| Deepgram Nova-3 (monolingual) | streaming $0.0077/min PAYG, $0.0065 Growth; "Pre-recorded runs lower" (pre-recorded figure not captured) | ≤0.46 | ≤$2,310 | ≤$3,003 | ≤$3,696 | not on LB | | [Deepgram pricing](https://deepgram.com/pricing) |
| Google Cloud STT V2 standard recognition | $0.016/min (first 500k min/month) | 0.96 | $4,800 | $6,240 | $7,680 | not on LB | | [Google Cloud STT pricing](https://cloud.google.com/speech-to-text/pricing) |

- Leaderboard leaders not priced here: Zoom Scribe v2.1 Pro (4.87), Otter speech-v3.1 (5.21), Azure speech 09-2026 (5.55). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Add-ons cost extra: AssemblyAI keyterms prompting $0.05/h on U-3.5 Pro and diarization $0.02/h. Deepgram keyterm prompting $0.0013/min and diarization $0.0020/min, with smart formatting included. — [AssemblyAI pricing](https://www.assemblyai.com/pricing); [Deepgram pricing](https://deepgram.com/pricing)
- Google's dynamic batch tier has further volume discounts ($0.0027 and $0.0024/min). Which models count as "Standard" (e.g., whether Chirp is included) is footnoted on the page and I didn't confirm it. — [Google Cloud STT pricing](https://cloud.google.com/speech-to-text/pricing)
- Groq bills a 10-second minimum per request. One dev.to post lists turbo at about $0.02/h, which conflicts with Groq's $0.04 and is unverified. — [Groq pricing summary via search](https://www.morphllm.com/groq-pricing); [dev.to](https://dev.to/pietrus914/speech-to-text-api-comparison-whisper-api-options-in-2026-400h)
- Third-party price roundups conflict, especially on Deepgram batch ($0.29/h vs $0.46/h). AssemblyAI's own roundup (prices "as of October 28, 2026") lists only streaming prices. — [AssemblyAI blog](https://www.assemblyai.com/blog/best-api-models-for-real-time-speech-recognition-and-transcription); [futureagi](https://futureagi.com/blog/speech-to-text-apis-in-2026-benchmarks-pricing-developer-s-decision-guide/)
- Vendor-run benchmarks such as Cohere's human-preference results and NVIDIA's throughput numbers should be treated skeptically. The HF leaderboard itself added private data and a benchmark-fitting analysis because public test sets get optimized against. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [arXiv 2608.19936](https://arxiv.org/pdf/2608.19936)

### Inferences
- Even the best API costs under $2,000 for the whole archive, cheaper than a few days of engineering time. A pragmatic hybrid: run an open model locally or on a rented GPU for the bulk, and send the hardest (oldest or noisiest) recordings to ElevenLabs Scribe v2 or AssemblyAI U-3.5 Pro for comparison.
- Self-host compute estimate: at long-form RTFx of 110–1,400 (Nemotron to Parakeet v3, on H200 per the leaderboard), 6,500 h needs about 5–60 GPU-hours. At typical cloud H100 rates (assumed $2–4/h; Lambda's current price not verified), compute is roughly $10–$250. Real pipeline overhead (VAD, I/O, unbatched long files) could multiply that several times.
- Data-handling note: sending a sangha's archive to third-party APIs raises consent and retention questions (e.g., whether audio is used for training). The Deepgram page says customer audio is "never used" for training (partial phrase seen). Check each vendor's terms.

### Gaps
- I couldn't capture Deepgram's pre-recorded Nova-3 price (the page uses a JavaScript toggle). Mistral Voxtral API transcription pricing, Groq's official page text, Gladia batch pricing and Microsoft Azure batch pricing were also not captured.
- I found no "batch discount" programs (e.g., 50% async tiers) in this pass, apart from Google's dynamic batch and volume tiers and Deepgram/AssemblyAI Growth/custom plans.
- Lambda Cloud's current H100/GH200 hourly rates weren't verified.
