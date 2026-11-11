# Dedicated open-weight ASR models worth testing for the dharma-talk archive (as of 10 November 2026)

Scope: open-weight, ASR-specialised models (CTC, TDT/RNNT, AED and speech-LLM decoders sold as ASR models). Paid APIs are out of scope. This note avoids repeating the model table in `reports/Dharma talk transcription options.md`. That table covered Whisper large-v3/turbo, Parakeet-TDT v2/v3, Qwen3-ASR-1.7B, Nemotron-3.5-Transcribe, Cohere Transcribe 03-2026, Granite Speech 5.0 2B, Canary-Qwen-2.5B, VibeVoice-ASR and CrisperWhisper v1. This note covers what that table missed: new leaderboard entries, fine-tunes, the Canary and other NVIDIA variants, Granite variants, and older or alternative families.

Method note: leaderboard numbers were read directly from the Open ASR Leaderboard's Gradio config (`/config` endpoint) on 10 Nov 2026, version **v1.15.1**. Model facts come from raw Hugging Face model-card READMEs and the HF model API (creation dates). Model cards are vendor documents; anything they claim is marked **[vendor]**.

---

## Q0. What changed on the HF Open ASR Leaderboard since the 6 Nov snapshot, and which top-20 open models did the earlier report miss?

### Takeaway
Two entries arrived on 10 Nov 2026 (v1.15.1). One of them, **Musci-ASR-qwen-1019-hf**, is a community GRPO fine-tune of Qwen3-ASR-1.7B and is now the #1 open model on short-form (5.70). It does **not** beat its base model on the private held-out sets, which points to leaderboard tuning. The long-form track's best open model is **freetranscribe/parakeet-ft-v1** (9.81), a Parakeet-v3 fine-tune. The earlier report did not cover it, and it is the most relevant new find for 30–90-minute talks. The top 20 open models also include several 2026 newcomers (ARK-ASR, Hojo-ASR, MOSS-Transcribe-Diarize, Higgs-Audio-v3-STT) that score slightly better than Parakeet on short-form, but none of them beats Qwen3-ASR-1.7B on private data.

### Cited Findings
- Changelog: "**10 November 2026** (v1.15.1) — Add reson8/rumble-2 and Musci-research/Musci-ASR-qwen-1019-hf, and update benchmark fitting results." 9 Nov 2026 introduced versioned deeplinks such as `?version=1.13.1`. The 6 Nov (v1.15.0), 2 Nov (LibriSpeech removed from the default average) and 26 Oct (long-form re-run on H200, new normalizer, freetranscribe/parakeet-ft-v1 added) entries match the earlier notes. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- The default short-form average is over AMI-Cleaned, Earnings22-Cleaned-AA-chunked, Gigaspeech-Cleaned, SPGISpeech, URGENT24, Voice Arena Monsoon, Voxpopuli-AA-Cleaned, Private (scripted) and Private (conversational). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **Open-weight short-form ranking, 10 Nov 2026 (v1.15.1).** Columns are overall rank among all 64 entries, avg WER, RTFx, URGENT24 (noisy/reverberant), private avg (scripted/conversational macro) and benchmark-fitting "spelling copy" rate (higher means more copying of benchmark spelling conventions; about 0.5 is chance). Source: [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

| LB rank | Model | Avg WER | RTFx | URGENT24 | Private avg | Fit rate | In earlier report's table? |
|---|---|---|---|---|---|---|---|
| 4 | Musci-research/Musci-ASR-qwen-1019-hf (new 10 Nov) | **5.70** | 775 | 10.49 | 7.64 | 0.752 | No |
| 10 | nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B | 6.13 | 473 | 10.94 | 8.29 | 0.707 | Yes |
| 11 | Qwen/Qwen3-ASR-1.7B-hf | 6.15 | 836 | **9.93** | **7.58** | 0.670 | Yes |
| 14 | ibm-granite/granite-speech-5.0-2b | 6.68 | 548 | 10.22 | 8.86 | 0.744 | Yes |
| 15 | CohereLabs/cohere-transcribe-03-2026 | 6.72 | 924 | 9.50 | 8.31 | 0.740 | Yes |
| 16 | TheStageAI/thewhisper-large-v3-turbo | 6.74 | 1184 | 10.82 | 9.09 | 0.767 | No |
| 17 | HojoAI/Hojo-ASR-V1 (4B) | 6.74 | **73** | 12.33 | 9.09 | 0.748 | No |
| 18 | Edge0/ARK-ASR-0.6B | 6.75 | 665 | 12.49 | 8.37 | 0.645 | No |
| 22 | nvidia/parakeet-tdt-0.6b-v2 (fast-gpu-asr) | 6.91 | 17254 | 11.64 | 8.55 | 0.586 | Yes (v2) |
| 23 | OpenMOSS-Team/MOSS-Transcribe-Diarize (0.9B) | 6.91 | 387 | 12.74 | 9.11 | 0.766 | No |
| 24 | nvidia/canary-qwen-2.5b | 6.92 | 882 | 13.02 | 8.83 | 0.593 | Yes |
| 25 | Edge0/ARK-ASR-3B | 6.92 | 480 | 13.29 | 8.28 | 0.759 | No |
| 27 | nvidia/parakeet-tdt-0.6b-v3 (fast-gpu-asr) | 6.95 | 14320 | 11.50 | 8.97 | 0.628 | Yes (v3) |
| 28 | bosonai/higgs-audio-v3-stt | 6.98 | 110 | 11.88 | 9.73 | **0.839 (highest)** | No |
| 29 | ibm-granite/granite-speech-5.0-470m-turboctc-nc | 6.98 | 21082 | 10.22 | 8.97 | 0.618 | Mentioned |
| 31 | ibm-granite/granite-speech-4.1-2b | 7.03 | 547 | 11.25 | 9.16 | 0.736 | No |
| 32 | nvidia/parakeet-tdt-0.6b-v3 | 7.04 | 6322 | 11.52 | 8.90 | 0.637 | Yes |
| 34 | Qwen/Qwen3-ASR-0.6B-hf | 7.07 | 750 | 11.56 | 8.70 | 0.727 | Mentioned |
| 35 | ibm-granite/granite-speech-4.1-2b-nar (non-autoregressive) | 7.16 | 2113 | 11.19 | 9.65 | 0.732 | No |
| 36 | ibm-granite/granite-speech-5.0-470m-turboctc | 7.41 | 21435 | 11.79 | 9.41 | 0.617 | Mentioned |
| 37 | mistralai/Voxtral-Small-24B-2507 | 7.44 | 101 | 12.34 | 9.34 | 0.643 | Notes only |
| 38 | nvidia/nemotron-speech-streaming-en-0.6b | 7.47 | 1116 | 12.54 | 9.50 | 0.640 | Notes only |
| 39 | distil-whisper/distil-large-v3.5 | 7.57 | 898 | 12.42 | 9.48 | 0.646 | Notes only |
| 41 | FermionResearch/Phonon-2 | 7.86 | 1977 | 14.90 | 10.07 | 0.640 | No |
| 42 | soundsgoodai/Zipformer-cr-ctc-transducer-XL-290M (beam) | 8.07 | 22109 | 13.67 | 10.51 | 0.741 | No |
| 45 | nvidia/canary-1b-v2 | 8.43 | 1854 | 14.56 | 10.25 | 0.601 | Notes only |
| 46 | FunAudioLLM/Fun-ASR-Nano-2512-hf | 8.54 | 506 | 13.93 | 11.27 | 0.725 | No |
| 47 | OpenLLM-France/Luciole-8B-Audio-1.0 | 8.73 | 999 | 15.34 | 10.90 | 0.615 | No |
| 49 | espnet/owsm_ctc_v4_1B | 9.26 | 783 | 16.12 | 11.71 | 0.798 | No |
| 51 | facebook/omniASR-LLM-7B-v2 | 9.45 | 130 | 14.84 | 11.79 | 0.621 | Notes only |
| 57 | nvidia/nemotron-3.5-asr-streaming-0.6b | 11.09 | 1353 | 20.14 | 13.14 | 0.648 | No |
| 61 | facebook/omniASR-CTC-7B-v2 | 13.27 | 522 | 18.68 | 17.71 | 0.579 | No |

- **Long-form track (Earnings21, Earnings22, CORAAL; re-run on H200 with new normalizer, 26 Oct 2026).** In order: elevenlabs/scribe_v2 8.45 (API); reson8/resonant-1 9.74 (no public card; HF README returned an auth error, so probably not open); **freetranscribe/parakeet-ft-v1 9.81 (RTFx 986; CORAAL 12.35)**; Nemotron-3.5-Transcribe 10.52 (CORAAL 13.93); assemblyai 10.76; Cohere 11.88 (CORAAL 14.33); gpt-transcribe 12.10; parakeet-tdt-0.6b-v3 12.60 (CORAAL 14.47); whisper-large-v3-turbo 12.82 (CORAAL 16.54); canary-qwen-2.5b 12.94 (CORAAL 17.16); parakeet-v2 13.08; whisper-large-v3 13.10; TheStageAI thewhisper-turbo 13.18 (CORAAL 17.95); distil-large-v3.5 13.31. Only 14 systems have long-form entries, and Qwen3-ASR, Granite, MOSS, ARK and Hojo are absent. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Benchmark-fitting tab: "higher scores indicating a higher fit … **A higher score does not imply that a model trained on the test set**." It measures how often a model copies each benchmark's spelling conventions (about 0.5 is chance). It was produced with Hume AI (technical report arXiv 2608.19936). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Private tab rationale: "to address risks of overfitting to public datasets, and to incentivize the development of models that generalize well to real-world data." The data comes from Appen, DataoceanAI, Voice Arena and Liva AI. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Several new top-10 short-form entries are proprietary or API-only: p99lab/audrey-0.7 (card says `license_name: proprietary`, "Hosted; file and live-streaming APIs"), reson8/rumble-2, modulate/multilingual, sophea/asr-k1, smallestai/pulse, sprag/symphony, gladia/solaria-3 and fonada/kapture-v3 (all with no RTFx, i.e. API rows). — [p99lab/audrey-0.7 card](https://huggingface.co/p99lab/audrey-0.7); [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

### Inferences
- On the held-out private data, the open ranking is Qwen3-ASR-1.7B (7.58) > Musci (7.64) > ARK-3B (8.28) > Nemotron-3.5 (8.29) > Cohere (8.31) > ARK-0.6B (8.37) > Parakeet-v2 (8.55–8.66). Everything newer than the earlier report sits in a 0.1–1.5-point band behind Qwen3-ASR-1.7B. A new short-form leader therefore does not change the bake-off finalists.
- Several newcomers have high benchmark-fitting rates together with weak URGENT24 or private scores: Higgs 0.839, OWSM-CTC 0.798, MOSS 0.766, ARK-3B 0.759, Musci 0.752 and Hojo 0.748. Their public averages likely overstate how they will do on out-of-domain cassette audio. NVIDIA Parakeet and Canary have the lowest fitting rates (about 0.59–0.64).

### Gaps
- I couldn't read Reson8's model card (auth error). Whether resonant-1 or rumble-2 have open weights is unverified, so I assumed API.
- The long-form track still lacks Qwen3-ASR, Granite, MOSS and the other LLM-decoder newcomers, so there is no apples-to-apples long-form comparison for them.

---

## Q1. Per-model catalogue: license, size, release date, architecture (models not in the earlier table)

### Takeaway
NVIDIA has released **no larger Parakeet or Canary** since 2025. Its 2026 ASR releases are 0.6B unified or streaming RNNT models plus the 30B-A4B Nemotron-3.5-Transcribe. The largest current open models for English are LLM-decoder systems: Nemotron 30B-A4B, Higgs 8.9B, Luciole 8B, VibeVoice 7B, Hojo 4B and ARK 3B. None of them beats Qwen3-ASR-1.7B on held-out data. The most useful new releases for this archive are **Parakeet-v3 derivatives** (freetranscribe parakeet-ft-v1, Moondream Parakeet Ultra), **Granite 4.1-2B-Plus** (keyword biasing, speaker attribution, 9-min segments) and **MOSS-Transcribe-Diarize** (90-min single pass, hotwords, diarization).

### Cited Findings

**NVIDIA (NeMo)**
- **freetranscribe/parakeet-ft-v1**: CC-BY-4.0; a fine-tune of parakeet-tdt-0.6b-v3 with the same architecture, tokenizer and 0.6B parameters, loadable with NeMo. HF repo created 13 Oct 2026, GGUF 17 Oct 2026. It was trained on 100 h of clips from 809 long YouTube recordings ("mostly interviews, podcasts and talks in English") using self-training only, with "no person wrote or corrected a transcript". Training took ~18 h on one RTX 3090. It is a single-developer release. — [parakeet-ft-v1 card](https://huggingface.co/freetranscribe/parakeet-ft-v1); [HF API listing](https://huggingface.co/freetranscribe)
- **moondream/parakeet-ultra**: CC-BY-4.0, "a post-trained version of parakeet-tdt-0.6b-v3. Same architecture, same tokenizer, same 0.6B parameters". It is run with Moondream's **Photon** runtime ("Every accuracy number on this page is Photon on an NVIDIA GPU"). A third-party GGUF appeared on 5 Oct 2026. — [Parakeet Ultra card](https://huggingface.co/moondream/parakeet-ultra); [handy-computer GGUF](https://huggingface.co/handy-computer/parakeet-ultra-gguf)
- **nvidia/parakeet-unified-en-0.6b**: released 7 Apr 2026 under the **NVIDIA Open Model License**. It is a 600M FastConformer RNNT trained jointly for offline and streaming (latency down to 160 ms) on ~250k h, with native punctuation and capitalization. — [card](https://huggingface.co/nvidia/parakeet-unified-en-0.6b)
- **nvidia/nemotron-labs-unified-asr-0.6b**: released 27 Oct 2026 under **OpenMDW-1.1**. It is the multilingual (25 European languages) version of parakeet-unified, with its encoder initialised from parakeet-tdt-0.6b-v3 and language-ID prompting. The card says it "outperforms parakeet-tdt-0.6b-v3 in offline mode" **[vendor]**. — [card](https://huggingface.co/nvidia/nemotron-labs-unified-asr-0.6b)
- **nvidia/nemotron-3.5-asr-streaming-0.6b**: released 4 Jun 2026 under OpenMDW-1.1. It is a 600M cache-aware FastConformer-RNNT for 40 locales, designed for low-latency voice agents. Short-form average **11.09** on the leaderboard (URGENT24 20.14). — [card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **nvidia/canary-1b-v2**: CC-BY-4.0, **978M** AED (32 encoder and 8 decoder layers, 16,384-token vocabulary), 25 European languages, word- and segment-level timestamps via an auxiliary CTC model. HF repo created 4 Aug 2025. — [card](https://huggingface.co/nvidia/canary-1b-v2)
- **nvidia/canary-1b-flash**: CC-BY-4.0, 883M AED, ">1000 RTFx". "Canary models are designed to handle input audio smaller than 40 seconds", and longer audio uses `speech_to_text_aed_chunked_infer.py`. — [card](https://huggingface.co/nvidia/canary-1b-flash)
- **nvidia/canary-qwen-2.5b**: CC-BY-4.0, SALM (canary-1b-flash encoder + Qwen3-1.7B with LoRA). "The maximum audio duration in training was 40s, and the maximum token sequence length was 1024 tokens … accuracy may be degraded" on longer input. — [card](https://huggingface.co/nvidia/canary-qwen-2.5b)
- **nvidia/parakeet-tdt-1.1b** (older, ~2024): CC-BY-4.0, ~1.1B FastConformer-TDT trained on 64K h of English. It "transcribes speech in lower case English alphabet", with no punctuation. It is not on the current leaderboard. — [card](https://huggingface.co/nvidia/parakeet-tdt-1.1b)
- The HF API listing of `nvidia` ASR models sorted by creation date shows **no new Canary or larger Parakeet in 2026**. The listing contains only Nemotron-3.5-Transcribe (+FP8/NVFP4 variants, Oct 2026), nemotron-labs-unified-asr-0.6b, nemotron-3.5-asr-streaming-0.6b, parakeet-unified-en-0.6b, nemotron-speech-streaming-en-0.6b (Dec 2025) and parakeet-ctc-0.6b-Vietnamese. — [HF models API, author=nvidia, pipeline=ASR](https://huggingface.co/api/models?author=nvidia&pipeline_tag=automatic-speech-recognition&sort=createdAt&direction=-1)
- The Nemotron-3.5 ASR streaming card compares itself against a "Parakeet RNNT 1.1B multilingual" model, which is available only as a hosted NIM on build.nvidia.com, not as open weights on HF. — [nemotron-3.5-asr-streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)

**IBM Granite**
- **ibm-granite/granite-speech-4.1-2b-plus**: Apache-2.0 (Granite family). The card's tables call the original release "v2604" and an updated "drop-in replacement" weight set "v2610" ("more accurate, especially for keyword biasing and for word-level timestamps on long samples"). Prompt-selected modes cover speaker-attributed ASR (`[Speaker N]:`), word-level timestamps (`[T:N]` tags), incremental decoding and keyword-list biasing. — [card](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus)
- **ibm-granite/granite-speech-4.1-2b-nar**: non-autoregressive 4.1 variant. Leaderboard 7.16 at RTFx 2113. — [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **granite-speech-5.0-2b** was released 20 Oct 2026, with ONNX (28 Oct) and GGUF (14 Oct) variants. It was trained on 390,000 h including "synthetic datasets tailored to support … keyword-biased ASR". **granite-speech-5.0-470m-turboctc** became multilingual on 21 Oct 2026 (the English-only original was released 25 Aug 2026). It has 16 conformer blocks with CTC greedy decoding and native punctuation and capitalization. — [5.0-2b card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b); [TurboCTC card](https://huggingface.co/ibm-granite/granite-speech-5.0-470m-turboctc)

**New community and lab LLM-decoder models (2026)**
- **Musci-research/Musci-ASR-qwen-1019-hf**: Apache-2.0, created 27 Oct 2026. It is "a GRPO fine-tune of Qwen3-ASR and is not an official Qwen release", "fine-tuned from Qwen3-ASR-1.7B-HF on an internal mixture built from the **public Open ASR Leaderboard training datasets** and non-native English speaker training datasets". It loads natively in transformers (`Qwen3ASRForConditionalGeneration`). — [card](https://huggingface.co/Musci-research/Musci-ASR-qwen-1019-hf)
- **OpenMOSS-Team/MOSS-Transcribe-Diarize** (0.9B): Apache-2.0, released 9 Jul 2026. It does end-to-end "long-form multi-speaker transcription, diarization, timestamps, and acoustic event awareness", with "single-pass inference on audio recordings up to **90 minutes** long, and custom hotword prompting for domain-specific terms". It won first place in the 2nd MLC-SLM Challenge (INTERSPEECH 2026). — [card](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize)
- **Edge0/ARK-ASR-0.6B** (25 May 2026) and **ARK-ASR-3B** (22 Jun 2026): Apache-2.0, audio encoder + adapter + decoder LLM trained with "teacher-data adaptation and on-policy distillation". They need `trust_remote_code=True`. The 3B card claims "state-of-the-art … average WER of 5.04%" **[vendor, old metric]**, against 6.92 on the current leaderboard. — [ARK-ASR-3B card](https://huggingface.co/Edge0/ARK-ASR-3B); [ARK-ASR-0.6B card](https://huggingface.co/Edge0/ARK-ASR-0.6B)
- **HojoAI/Hojo-ASR-V1** (4B, Apache-2.0, 24 May 2026): an Encoder-Adapter-Qwen3 LLM with "multi-frame acoustic fusion". It is slow (RTFx 73). — [card](https://huggingface.co/HojoAI/Hojo-ASR-V1); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **bosonai/higgs-audio-v3-stt** (25 Mar 2026) and **higgs-audio-v3-8b-stt-v2** (27 Apr 2026): Apache-2.0. The 8B v2 is "a Whisper-Large-v3 encoder with a Qwen3-8B decoder (8.91B total parameters), **fine-tuned with LoRA on diverse ASR benchmarks**". — [card](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2)
- **OpenLLM-France/Luciole-8B-Audio-1.0**: Apache-2.0 general audio-LLM (ASR, AST, QA, captioning) with 82.1M trainable parameters on top of a ~8.2B base. — [card](https://huggingface.co/OpenLLM-France/Luciole-8B-Audio-1.0)
- **microsoft/VibeVoice-ASR-Streaming-7B / -1.5B** (2 Sep 2026, MIT): "unified streaming ASR model that transcribes Who (Speaker) said What (Content), with support for Customized Hotwords and 10 languages". Tech report arXiv 2609.02812. The card gives no English WER. **VibeVoice-ASR-BitNet** (24 Jul 2026, MIT) is a quantized variant. — [Streaming-7B card](https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-7B); [BitNet card](https://huggingface.co/microsoft/VibeVoice-ASR-BitNet)
- **StepFun ParaASR** (arXiv 31 Jul 2026): a 0.6B frozen encoder plus a 4B decoder with multi-token prediction, up to 30 min per session. It reports long-form avg 3.70 vs Qwen3-ASR-1.7B 4.20 on its own long-form sets. I found no license or weights. — [ParaASR paper](https://arxiv.org/html/2607.29279v1)

**Whisper derivatives**
- **TheStageAI/thewhisper-large-v3-turbo**: CC-BY-4.0, described as "a fine-tuned, high-performance variant of OpenAI's Whisper Large V3". It is distributed as "Elastic" compressed models through TheStage's SDK (`thestage-elastic-models[nvidia]`). — [card](https://huggingface.co/TheStageAI/thewhisper-large-v3-turbo)
- **CrisperWhisper 2.0** (`nyralabs/CrisperWhisper2.0_large`, plus turbo/medium/small sizes): `license_name: nyra-health-non-commercial-research`. It is verbatim-focused, claims "built-in mitigation of Whisper's looping-hallucination failure mode" and "3-5x faster inference" than v1 **[vendor]**. Derivative GGUF/ONNX repos date from Aug–Sep 2026. — [CrisperWhisper 2.0 card](https://huggingface.co/nyralabs/CrisperWhisper2.0_large); [v1 card](https://huggingface.co/nyrahealth/CrisperWhisper)
- **distil-whisper/distil-large-v3.5**: short-form 7.57, long-form 13.31. It is no better than large-v3 on long-form. — [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)

**Other families**
- **Moonshine Streaming** (UsefulSensors, MIT): Tiny 34M, Small 123M, Medium 245M. The Medium averages 6.65 over 8 older Open-ASR sets including LibriSpeech **[vendor]**; its AMI score is 10.68. The card advises "Limit max output length to avoid hallucination loops." — [Moonshine Streaming Medium card](https://huggingface.co/UsefulSensors/moonshine-streaming-medium)
- **Kyutai STT 2.6B en** (CC-BY-4.0, Jun 2025): "found to perform well with audio as long as 2 hours". Its pseudo-labels came from whisper-timestamped. I found no 2026 Kyutai STT release on HF. — [card](https://huggingface.co/kyutai/stt-2.6b-en); [HF API kyutai listing](https://huggingface.co/kyutai)
- **Meta Omnilingual ASR** (`facebook/omniASR-*`, Apache-2.0, Nov 2025; v2 entries on the leaderboard) comes in CTC, LLM and W2V variants at 300M–7B and covers 1,600+ languages. CTC-3B needs about 8 GiB of VRAM. English is weak: LLM-7B-v2 scores 9.45 and CTC-7B-v2 13.27. — [omniASR-LLM-7B card](https://huggingface.co/facebook/omniASR-LLM-7B); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **ESPnet OWSM-CTC v4 1B**: CC-BY-4.0, encoder-only hierarchical self-conditioned CTC trained on 320k h. `decode_long` handles "one recording of any length" with overlapping buffers. Leaderboard 9.26. — [card](https://huggingface.co/espnet/owsm_ctc_v4_1B)
- **FunAudioLLM Fun-ASR-Nano-2512** (Dec 2025; HF/vLLM/GGUF variants in 2026) scores 8.54 on the leaderboard. The SenseVoiceSmall and Paraformer GGUFs exist but have no English leaderboard entries. — [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard); [HF FunAudioLLM](https://huggingface.co/FunAudioLLM)
- **zai-org/GLM-ASR-Nano-2512**: MIT, 1.5B, claims "lowest average error rate (4.10) among comparable open-source models" **[vendor; not on LB]**. — [card](https://huggingface.co/zai-org/GLM-ASR-Nano-2512)
- **DataoceanAI Dolphin** (small/base, May 2026, Apache-2.0) "supports 40 Eastern languages" and is not aimed at English. — [card](https://huggingface.co/DataoceanAI/dolphin-small)
- **soundsgoodai Zipformer-cr-ctc-transducer-XL-290M** is **CC-BY-NC-4.0** (k2/icefall). It scores 8.07 with beam search. — [card](https://huggingface.co/soundsgoodai/Zipformer-cr-ctc-transducer-XL-290M)
- **FermionResearch Phonon-2 / 2.5** are low-bit quantizations of parakeet-tdt-0.6b-v3 (CC-BY-4.0). Phonon-2 scores 7.86, worse than its parent at 7.04. — [Phonon-2.5-English card](https://huggingface.co/FermionResearch/Phonon-2.5-English); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- **futo-org/asr4all** (FUTO ethical-use license 1.0) scores 9.97–13.97. **abr-ai/niagara** (9–84M) scores 10.9–17.9. **Edge0/Audio8-ASR-Infinite** (Apache-2.0) is a streaming Chinese/English model on a Voxtral-Realtime-4B audio tower that publishes only LibriSpeech numbers. — [asr4all-l-plus card](https://huggingface.co/futo-org/asr4all-l-plus); [Audio8-ASR-Infinite card](https://huggingface.co/Edge0/Audio8-ASR-Infinite)
- **Cohere**: the only Cohere Transcribe releases on HF are `cohere-transcribe-03-2026` (gated) and `cohere-transcribe-arabic-07-2026` (an Arabic+English fine-tune, 18 Jun 2026 repo date). I found no newer English model. — [HF CohereLabs listing](https://huggingface.co/CohereLabs/cohere-transcribe-arabic-07-2026); [AIWiki](https://aiwiki.ai/wiki/cohere_transcribe)

### Inferences
- "Larger variant" checks come back negative for NVIDIA. No open Parakeet or Canary above 1.1B exists, and parakeet-tdt-1.1b (2024) has no punctuation. It is not worth testing over v3 and its fine-tunes.
- The only "bigger" English-ASR open models that are actually competitive are Nemotron-3.5 (already downloaded) and, on paper, ARK-3B, Hojo-4B and Higgs-8B. All three of those score worse than Qwen3-ASR-1.7B on private data and URGENT24.

### Gaps
- I couldn't confirm the exact release dates of Moonshine Streaming and CrisperWhisper 2.0. The Aug 2026 date for CrisperWhisper 2.0 is inferred from derivative repos.
- I couldn't read the license and card for omniASR v2 or the Reson8 models (auth errors).
- I didn't verify whether Parakeet Ultra loads in plain NeMo. Its card documents only the Photon runtime.

---

## Q2. WER evidence beyond the leaderboard average: long-form, noisy, CORAAL, held-out; independent vs vendor

### Takeaway
For long monologues, the most relevant new numbers come from **parakeet-ft-v1**. It reaches 9.81 long-form average and 12.35 on CORAAL (scored by the leaderboard) against 12.60 and 14.47 for Parakeet-v3. Its own held-out test on 29.6 h of long YouTube talks and podcasts shows skipped passages falling from 87 to 3 **[self-reported]**. Musci's 5.70 short-form lead disappears on private data (7.64 vs 7.58 for base Qwen3-ASR) and on URGENT24 (10.49 vs 9.93). Most other newcomers' card claims are on old metrics and do not match current leaderboard numbers.

### Cited Findings
- parakeet-ft-v1 card, with the leaderboard decoding vs its own "recipe": Earnings-21 7.62 / 6.97 (v3: 9.40 / 8.11); CORAAL mean of 8 subsets 13.21 / 12.33 (v3: 14.48 / 13.08); TED-LIUM 1.95 / 1.95 (v3: 2.47 / 2.29). "v3 sometimes skips whole passages of a long recording … on 16 recordings kept out of training, v3 skipped 87 passages and this model 3" (1,775 vs 31 words skipped; 13 of 16 vs 3 of 16 recordings affected). — [parakeet-ft-v1 card](https://huggingface.co/freetranscribe/parakeet-ft-v1)
- parakeet-ft-v1's own caveats: "Short clips are mixed against v3 … slightly worse on average." "It drops fewer words. It doesn't hear them better, so **names and jargon are no more accurate than with v3**." "None of the training audio was taken from an Open ASR Leaderboard dataset." — [parakeet-ft-v1 card](https://huggingface.co/freetranscribe/parakeet-ft-v1)
- The leaderboard independently scores parakeet-ft-v1 at long-form 9.81 (Earnings21 6.98, Earnings22 10.09, CORAAL 12.35), the best open model and 0.7 below Nemotron-3.5 (10.52). — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Parakeet Ultra vs v3, scored with the leaderboard's pipeline "as of September 2026" by Moondream **[vendor]**: 7 English sets 6.26 → 5.80; MUSAN background noise (9 conditions) 6.72 → 5.82; **TED-LIUM long-form 2.71 → 1.94**; AMI 10.86 → 9.77; Earnings-22 10.75 → 9.76. Throughput is 9,743× vs 6,005× real time on a B200. — [Parakeet Ultra card](https://huggingface.co/moondream/parakeet-ultra)
- parakeet-unified-en-0.6b: offline 5.91 vs parakeet-tdt-0.6b-v2 6.04 on "HF ASR Leaderboard datasets" **[vendor, old LibriSpeech-including average]**. It is not on the current board. — [card](https://huggingface.co/nvidia/parakeet-unified-en-0.6b)
- Musci reports its own public 9-set average of 4.36, including LibriSpeech. On the leaderboard it scores 5.70 avg, but URGENT24 10.49 (base Qwen3-ASR-1.7B: 9.93) and private 7.64 (base: 7.58). — [Musci card](https://huggingface.co/Musci-research/Musci-ASR-qwen-1019-hf); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Card vs leaderboard gaps: ARK-ASR-3B claims 5.04 (current LB 6.92); Higgs-v3-8B-STT-v2 claims 5.449 on an 8-set average including LibriSpeech and TED-LIUM; Zipformer-XL claims 5.56 (LB 8.07). — [ARK-3B card](https://huggingface.co/Edge0/ARK-ASR-3B); [Higgs card](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2); [Zipformer card](https://huggingface.co/soundsgoodai/Zipformer-cr-ctc-transducer-XL-290M); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Nemotron-3.5-Transcribe's own card lists long-form mean WER 10.98 vs Parakeet-TDT-0.6B-v3 13.37 (an earlier leaderboard run). The current H200 re-run gives 10.52 vs 12.60. — [Nemotron-3.5 card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B); [LB](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Noise (URGENT24), open models: Cohere 9.50 < Qwen3-1.7B 9.93 < Granite-5.0-2B and TurboCTC-nc 10.22 < Musci 10.49 < TheWhisper 10.82 < Nemotron 10.94 < Granite-4.1-NAR 11.19 < Parakeet-v3 11.50–11.52 < Higgs 11.88 < Hojo 12.33 < ARK-0.6B 12.49 < MOSS 12.74 < Canary-Qwen 13.02 < ARK-3B 13.29 < Whisper-large-v3 13.73 < Canary-1B-v2 14.56. — [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)
- Fair-Speech study (arXiv 2604.21276): at 0 dB SNR, overall WER is 12.1% for Whisper-large-v3 and 7.4% for Qwen3-ASR-1.7B. — [Do LLM Decoders Listen Fairly?](https://arxiv.org/html/2604.21276v1)
- ParaASR (StepFun, no released weights found) reports long-form avg 3.70 vs Qwen3-ASR-1.7B 4.20, VibeVoice-ASR 4.87 and FunASR-Nano 5.59 on the authors' own long-form sets **[vendor]**. — [ParaASR](https://arxiv.org/html/2607.29279v1)

### Inferences
- CORAAL (spontaneous field interviews, older recordings) is the closest public proxy to the archive. On it, parakeet-ft-v1 (12.35) beats every other open model on the board, including Nemotron-3.5 (13.93) and Parakeet-v3 (14.47). Its fix for skipped passages addresses a failure mode (silent deletion of whole passages) that the gold-set WER would penalise heavily on 60–90-minute talks. Its training data ("interviews, podcasts and talks") is also closer to dharma talks than any benchmark.
- Musci adds no held-out gain over the Qwen3-ASR the user already runs, and it is worse in noise. It is cheap to test because the existing Qwen runner should load it unchanged (same transformers class), but its expected value is low.

### Gaps
- No public benchmark resembles cassette audio, chant or Sino-Japanese vocabulary. All of the above are proxies.
- parakeet-ft-v1's skip study uses YouTube auto-captions as the reference, and it is one developer's evaluation. It has not been replicated independently.
- Parakeet Ultra has no independent leaderboard entry.

---

## Q3. Long-form handling, timestamps, diarization and hallucination on silence

### Takeaway
New single-pass long-form options are MOSS-Transcribe-Diarize (90 min, with diarization) and parakeet-ft-v1's recipe (local attention plus ≤90 s pause cuts). Granite 4.1-2B-Plus now handles 9-minute segments. Canary (40 s), Canary-Qwen (40 s trained) and Granite 5.0 (~2 min) need heavy chunking. Recent independent hallucination studies **contradict the "transducers don't hallucinate" assumption**. On a hard Earnings-22 subset, Parakeet-TDT-v2 and Canary hallucinated more often than Whisper-large-v3. Qwen3-ASR, by contrast, shows near-zero repetition loops under silence or dropout, while Granite's compressed encoder reintroduces them.

### Cited Findings
- parakeet-ft-v1 recipe: "local attention with 256 encoder frames of context on each side, about 20 seconds, where the leaderboard's long-audio setting is 128"; "cuts the recording at pauses into pieces of at most 90 seconds … at the quietest point in the second half of the allowed length, the min-cut rule from WhisperX"; "decodes each piece with 5 seconds of extra audio on both sides and keeps each word only from the piece its midpoint falls inside". On Earnings-22 with v3: whole recording at 128-frame attention 13.75, plus 256-frame 12.76, plus pause cuts ≤90 s 11.12. — [parakeet-ft-v1 card](https://huggingface.co/freetranscribe/parakeet-ft-v1)
- MOSS-Transcribe-Diarize: one pass up to 90 min; outputs timestamps and anonymous speaker labels (`[S01]`, `[S02]`) plus acoustic event annotations. — [MOSS card](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize)
- Granite 4.1-2B-Plus: "works well with audio segments up to 9 minutes long for ASR and SAA, and up to 3.5 minutes for timestamps". It has speaker-attributed ASR (`[Speaker N]:`) with WDER reported on 2–5-minute segments, word timestamps as `[T:N]` centisecond tags with silences transcribed as `_`, and **incremental decoding** that conditions on previously transcribed segments "to improve transcription accuracy or to maintain the speaker numbering". — [Granite 4.1-2B-Plus card](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus)
- Granite 5.0 2B: "transcribe audio in segments of up to ~2 minutes; split longer recordings (e.g. with VAD)". — [card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b)
- Canary-1B-flash/v2: inputs under 40 s, with a chunked AED script for longer audio (`chunk_len_in_secs=40.0`, or 10 s when timestamps are needed). Canary-1B-v2 provides word and segment timestamps through an auxiliary CTC model. — [Canary-1B-flash card](https://huggingface.co/nvidia/canary-1b-flash); [Canary-1B-v2 card](https://huggingface.co/nvidia/canary-1b-v2)
- Qwen3-ASR "naturally supports single speech no longer than 20 minutes". — [Qwen3-ASR technical report](https://arxiv.org/pdf/2601.21337)
- OWSM-CTC v4 `decode_long` handles any length with overlapping buffers (`context_len_in_secs=4`). Kyutai claims about 2 h without changes. — [OWSM card](https://huggingface.co/espnet/owsm_ctc_v4_1B); [Kyutai card](https://huggingface.co/kyutai/stt-2.6b-en)
- nemotron-labs-unified-asr: "The output text might be empty if the input audio doesn't contain any speech." — [card](https://huggingface.co/nvidia/nemotron-labs-unified-asr-0.6b)
- **HALAS** (AGH Kraków, arXiv 2606.23048, 22 Jun 2026) uses human-annotated hallucinations on unprocessed Earnings-22 segments (0.6–17.6 s) chosen for high inter-model disagreement, so the rates are inflated by design. Hallucination rate: Whisper large-v2 43.8%, **Whisper large-v3 23.8%**, large-v3-turbo 29.4%, **CrisperWhisper (v1) 21.4%**, **Canary-1B 33.6%**, Canary-1B-Flash 30.4%, **Parakeet-TDT v2 33.7%**. Looping was rare (1.1%). Parakeet's hallucinations are highly concentrated: its "top-10 phrases cover 83%". Phrases common to all models include "you", "okay" and "thank you". — [HALAS](https://arxiv.org/html/2606.23048)
- **Fair-Speech / LLM-decoder study** (arXiv 2604.21276). Under 30% signal masking: Whisper-large-v3 had 10,365 insertions (35% repetition); Qwen3-ASR-1.7B 1,353 (3% repetition); Granite-Speech 2B/8B 7,689 / 10,187 (49–57% repetition); Canary-Qwen-2.5B 4,552 (~30% repetition). Under silence injection: Qwen3 under 4% repetition, Granite 31–43%. The authors attribute this to encoder compression: "High-compression audio encoding (Granite's Q-former) brings repetition back even with an LLM decoder". The Granite versions tested were Granite Speech 3.3, per the search snippet. — [Do LLM Decoders Listen Fairly?](https://arxiv.org/html/2604.21276v1)
- Moonshine's card warns to "Limit max output length to avoid hallucination loops". CrisperWhisper 2.0 claims built-in loop mitigation **[vendor]**. — [Moonshine card](https://huggingface.co/UsefulSensors/moonshine-streaming-medium); [CrisperWhisper 2.0 card](https://huggingface.co/nyralabs/CrisperWhisper2.0_large)

### Inferences
- The HALAS results mean the gold set should explicitly measure Parakeet-family insertions of stock phrases ("thank you", "okay") in bell, chant and silence regions. Parakeet's concentrated phrase distribution suggests a simple blocklist filter on non-speech regions would remove most of them.
- Qwen3-ASR's low repetition under silence (an independent result) supports keeping it as a finalist for VAD-chunked long-form work. Granite (Q-former) may need stricter VAD gating, although the evidence comes from an older Granite version.
- For Q&A segments, the candidates that provide built-in speaker turns in one model are MOSS (90 min), Granite 4.1-Plus (9-min segments) and Nemotron-3.5 (1 h). Each is an alternative to separate diarization.

### Gaps
- No independent long-form hallucination benchmark (30–90-minute files with long silences) covers the 2026 models. HALAS is short-segment and Fair-Speech uses synthetic perturbations.
- I found no published English WER for MOSS on long-form sets, nor for VibeVoice-ASR-Streaming.

---

## Q4. Context biasing support and evidence of effectiveness

### Takeaway
Biasing support has spread. Granite (keyword list, up to 2,000 terms in 5.0), MOSS, VibeVoice-Streaming, Nemotron-3.5 and Qwen3-ASR all accept prompt hotwords, and NeMo GPU-PB covers all CTC, TDT/RNNT and Canary AED models, including parakeet-ft-v1 and parakeet-unified. Only IBM publishes before/after numbers, which are large (keyword F1 +10 to +20 points). I found no independent test of these new mechanisms with long, distractor-heavy lists. One important caveat: parakeet-ft-v1 itself does not improve names, so boosting remains essential.

### Cited Findings
- Granite 4.1-2B-Plus keyword-list biasing, keyword F1 (v2610 without → with KWB) **[vendor]**: Gigaspeech 74.1 → 84.4; LS-other 77.2 → 97.4; SPGISpeech 79.9 → 92.2; TED-LIUM 88.7 → 94.3; CV-en 72.7 → 82.4. Syntax: "`Can you transcribe the speech into a written format? Keywords: …`". Lists "may also include terms that do not appear in the input audio, making them well suited for batch processing or recurring domain-specific use cases". — [Granite 4.1-2B-Plus card](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus)
- Granite 5.0 2B: "Increased keyword list size (up to 2000) for multilingual keyword-biased ASR and AST". KWB F1 is reported only as a chart image. — [Granite 5.0 2B card](https://huggingface.co/ibm-granite/granite-speech-5.0-2b)
- MOSS-Transcribe-Diarize: "To add hotwords, append a short hint to the default prompt". No effectiveness numbers are given. — [MOSS card](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize)
- VibeVoice-ASR-Streaming: "Users can provide customized hotwords, such as names and technical terms". No numbers on the card. — [card](https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-7B)
- Nemotron-3.5-Transcribe prompt template: "`Transcribe with punctuation and capitalization. Context terms: .`" for "Earnings calls, support recordings, and technical discussions". The card gives no quantified biasing results. — [Nemotron-3.5 card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- NeMo GPU-PB "is supported for CTC, RNN-T/TDT, and AED (Canary) models based on NGPU-LM infrastructure", applied at decoding in shallow fusion with no retraining. Recommended settings: `context_score` 1.0; `depth_scaling` 2.0 for CTC/RNNT/TDT and 1.0 for Canary; `boosting_tree_alpha` "should be tuned". CTC-WS works on CTC and on hybrid Transducer-CTC models. Flashlight boosting is CTC lexicon-mode only. The docs do not mention SALM/Canary-Qwen and report no WER gains. — [NeMo word boosting docs](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/asr_customization/word_boosting.html)
- parakeet-ft-v1: "names and jargon are no more accurate than with v3". — [card](https://huggingface.co/freetranscribe/parakeet-ft-v1)
- A search for 2026 head-to-head biasing benchmarks found only Huber & Waibel (arXiv 2608.05759, already in the earlier notes). It compares Whisper biasing methods with Qwen3-ASR, Qwen3-Omni and VibeVoice-ASR, but not Canary, Granite or NeMo. — [How to Recognize New Words](https://arxiv.org/html/2608.05759)
- A secondary roundup lists keyword biasing as "not disclosed" for Qwen3-ASR-1.7B and Canary-Qwen-2.5B, against 2,000 terms for Granite 5.0. — [MarkTechPost, Granite 5.0 release](https://www.marktechpost.com/2026/10/22/ibm-granite-speech-5-0-2b-release/)

### Inferences
- parakeet-ft-v1 has the same architecture and tokenizer as v3 and loads in NeMo, so the user's existing GPU-PB boosting setup should apply unchanged. That makes it the cheapest high-value swap. This is inferred and not tested.
- Parakeet Ultra's boosting support depends on whether it runs in NeMo. If it only runs in Photon, it loses GPU-PB.
- Granite 4.1-2B-Plus is the only new model with published biasing gains plus incremental context and speaker turns. Its biasing should be tested with per-talk lists of 20–40 terms and with the larger glossary, because IBM does not report distractor-list size.

### Gaps
- None of the new prompt-hotword models (MOSS, VibeVoice-Streaming, Granite 5.0) publish robustness to large or irrelevant lists, so the distractor problem documented in the earlier notes is untested for them.
- I could not confirm whether Cohere Transcribe has any biasing mechanism. Neither the gated card nor news coverage mentions one.

---

## Q5. Memory needs and inference stacks (brief)

### Takeaway
All the high-value new candidates run on familiar stacks. The Parakeet derivatives use NeMo, Granite 4.1-Plus uses transformers or vLLM, MOSS uses its own repo on Python 3.12, and Musci uses transformers. All are small enough (0.6–2B) for the 8 GB RTX 3070 Ti or a cheap cloud GPU. The large models (Higgs 8.9B, Luciole 8B, VibeVoice 7B, Hojo 4B) add cost without held-out gains.

### Cited Findings
- parakeet-ft-v1 runs with `nemo_asr.models.ASRModel.from_pretrained("freetranscribe/parakeet-ft-v1")`, or with the recipe via `uv tool install "freetranscribe[nemo]"; freetranscribe transcribe recording.wav`. It was trained on one RTX 3090. — [card](https://huggingface.co/freetranscribe/parakeet-ft-v1)
- Parakeet Ultra runs via `pip install moondream`, `md.photon("moondream/parakeet-ultra")`, with segment and word timestamps. A 178 MB ternary sibling, "Parakeet Redux", targets CPUs. — [card](https://huggingface.co/moondream/parakeet-ultra)
- Musci loads with `Qwen3ASRForConditionalGeneration` in transformers, with no `qwen-asr` package or remote code needed. — [card](https://huggingface.co/Musci-research/Musci-ASR-qwen-1019-hf)
- ARK-ASR needs `trust_remote_code=True` and its official inference script. MOSS uses `git clone` of its repo with Python 3.12. The parakeet-unified and nemotron-labs-unified streaming paths use NeMo's buffered RNNT scripts. nemotron-3.5-asr-streaming also loads via `AutoModelForRNNT` in transformers. — [ARK-3B card](https://huggingface.co/Edge0/ARK-ASR-3B); [MOSS card](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize); [parakeet-unified card](https://huggingface.co/nvidia/parakeet-unified-en-0.6b); [nemotron-3.5-asr-streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Nemotron-3.5-Transcribe (already downloaded): vLLM 0.32.0 + NeMo Speech main, `VLLM_MAX_AUDIO_DECODE_DURATION_S=3600`, 1× H100 80 GB in BF16. A100 80GB is supported in BF16; FP8/NVFP4 checkpoints exist (Oct 2026). — [Nemotron-3.5 card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- Omnilingual CTC-3B needs ~8 GiB of inference VRAM. — [omniASR card](https://huggingface.co/facebook/omniASR-LLM-7B)
- TheWhisper needs TheStage's proprietary-SDK runtime (`thestage-elastic-models[nvidia]`). — [card](https://huggingface.co/TheStageAI/thewhisper-large-v3-turbo)

### Inferences
- Fit on an 8 GB GPU is inferred from parameter counts (0.6B NeMo, 0.9B MOSS, 2B Granite bf16 ≈ 4–5 GB). Long single-pass inputs (MOSS 90 min) may need more memory and are better tried in the cloud.

### Gaps
- I didn't find measured VRAM for MOSS at 90 minutes or for Granite 4.1-Plus at 9-minute segments.

---

## Q6. Ranking by expected value for this archive (new or untested candidates only)

### Takeaway
Test **parakeet-ft-v1 with NeMo GPU-PB boosting and its decoding recipe** first. It is a drop-in swap for the current Parakeet runner, it is the best open model on long-form and CORAAL, and it targets dropped passages in long talks. Next, test **Granite 4.1-2B-Plus with keyword lists** and **MOSS-Transcribe-Diarize** for Q&A talks. Musci, Parakeet Ultra and parakeet-unified are cheap side checks. Skip the rest.

### Cited Findings
(Evidence for each rank is cited in Q0–Q5 above.)

| Rank | Candidate | Why | Main risk | Effort |
|---|---|---|---|---|
| 1 | **freetranscribe/parakeet-ft-v1** (+ recipe, + GPU-PB) | Best open long-form (9.81) and CORAAL (12.35) on the leaderboard. Fixes v3's skipped passages (87 → 3 on 29.6 h of talks/podcasts). CC-BY-4.0, NeMo drop-in | Single developer; short-clip WER slightly worse; no help on names | Very low (same runner) |
| 2 | **Parakeet-v3 decoding recipe alone** (256-frame local attention, ≤90 s pause cuts, 5 s overlap) | Earnings-22 13.75 → 11.12 for v3 without retraining | Self-reported | Very low |
| 3 | **ibm-granite/granite-speech-4.1-2b-plus (v2610)** | Keyword biasing with published F1 gains, 9-min segments, incremental context, speaker attribution, word timestamps; Apache-2.0 | Vendor-only biasing numbers; Granite-family repetition under silence (older version tested); 4.1-2b base is 7.03 / private 9.16 | Medium |
| 4 | **OpenMOSS-Team/MOSS-Transcribe-Diarize** (0.9B) | 90-min single pass with diarization, timestamps, hotwords; Apache-2.0; LB 6.91 | Weak URGENT24 (12.74); high benchmark-fit rate (0.766); no long-form English numbers | Medium |
| 5 | **moondream/parakeet-ultra** | Claims v3 gains in noise (6.72 → 5.82) and TED long-form (2.71 → 1.94); CC-BY-4.0 | Vendor-only; Photon runtime, so GPU-PB support unclear | Low–medium |
| 6 | **Musci-ASR-qwen-1019-hf** | #1 open short-form (5.70); drops into the existing Qwen3-ASR runner | Trained on leaderboard train sets; no private-data gain (7.64 vs 7.58); worse URGENT24 | Very low |
| 7 | **nvidia/parakeet-unified-en-0.6b** | RNNT, so GPU-PB works; vendor offline 5.91 vs v2 6.04 | Not on LB; NVIDIA Open Model License (not CC-BY) | Low |
| 8 | Granite 5.0 470M TurboCTC / 4.1-2b-nar | Very fast non-autoregressive; TurboCTC emits no-speech tokens; useful as a ROVER second opinion | Lower accuracy (7.0–7.4) | Low |
| 9 | ARK-ASR-0.6B/3B, Hojo-ASR-V1, Higgs-v3-STT | Short-form 6.7–7.0 | High fitting rates, weak URGENT24 and private, slow (Hojo RTFx 73), remote code | Skip unless spare time |
| 10 | Canary-1B-v2 / 1B-flash | GPU-PB on AED works | 8.43 LB; 40 s inputs; 30–34% hallucination on HALAS | Skip |
| 11 | CrisperWhisper 2.0, Zipformer-XL | — | Non-commercial licenses | Skip unless research-only use is acceptable |
| — | Kyutai STT, Moonshine, OWSM-CTC v4, omniASR, Fun-ASR/SenseVoice, Dolphin, GLM-ASR-Nano, asr4all, niagara, Luciole, VibeVoice-Streaming, nemotron-3.5-asr-streaming | Weaker English (LB 8.5–17.9) or wrong target (streaming, Eastern languages, edge) | — | Skip |

### Inferences
- The model choice is now less important than long-form decoding and biasing. The biggest new evidence shows that how Parakeet chunks long audio changes WER by 2–3 points, and that a fine-tune trained on talk-like audio removes silent passage drops.
- A practical cloud bake-off addition is roughly six runs on the gold set: parakeet-ft-v1 ± boosting with the recipe, v3 with the recipe, Granite 4.1-Plus with and without keywords, MOSS with and without hotwords, and Musci. Each is small enough for a single mid-range GPU.

### Gaps
- None of these rankings is validated on archive audio. The local gold-set bake-off is the deciding evidence.
- I found no model released between 6 and 10 Nov 2026 other than the Musci HF conversion (repo created 27 Oct; added to the leaderboard 10 Nov) and the Reson8 entries (probably API).
