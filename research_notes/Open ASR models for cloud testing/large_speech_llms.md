# Large open-weight speech LLMs and audio-capable LLMs for long-form English transcription (as of 10 Nov 2026)

Scope: open-weight models of several billion parameters or more (speech LLMs, omni models, MoE audio models) that could transcribe 30–90-minute English dharma talks. Hosted APIs are out of scope. Nemotron‑3.5‑Transcribe‑30B‑A4B is already downloaded, so only new findings about it are listed. The earlier report (`reports/Dharma talk transcription options.md`) already tabulates Whisper, Parakeet, Qwen3‑ASR‑1.7B, Nemotron‑3.5, Cohere, Granite 5.0 2B, Canary‑Qwen and VibeVoice‑ASR with leaderboard numbers. This file adds the larger and omni models it skipped.

Method note: the HF Open ASR Leaderboard Space did not render for fetching (it returned only the loading shell), so I could not re-read live leaderboard rows. Leaderboard figures below are the 6 Nov 2026 snapshot quoted in the earlier report, or the "Open ASR leaderboard" figures that vendors print on their own model cards. Card figures use the **pre-Oct-2026 methodology** (which still included LibriSpeech), so they are not comparable with the new averages.

## 1. Which large open-weight candidates exist (license, size, architecture, date)

### Takeaway
Only a handful of large open-weight models are realistic long-form English transcribers: Nemotron‑3.5‑Transcribe (34B MoE, 1 h), VibeVoice‑ASR (9B, 60 min), Voxtral Small (24B, 30 min) and Qwen3‑Omni‑30B‑A3B (40 min). Most other "audio LLMs" are chat or agent models with short audio windows, non-commercial licences, or weights that turn out to be API-only. Several autumn‑2026 releases (Qwen‑Audio‑3.1‑ASR, Voxtral 3) look open in aggregator listings but appear to be closed.

### Cited Findings

**Primary candidates (open weights, long audio per call)**
- **Nemotron‑3.5‑Transcribe‑30B‑A4B** (NVIDIA). OpenMDW‑1.1, and the card states "ready for commercial or non-commercial use". It is a Mamba‑2/Transformer hybrid MoE built on Nemotron‑3.5 Lightning 30B‑A3B, with a ~600M ASR encoder and a ~99M speaker encoder. Totals are 34B parameters, ~4.3B active including the ~800M audio encoder, and ~3.5B active in the LLM. It takes up to 1 h within a 65,536‑token context. — [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- Nemotron release date: one aggregator lists 7 Oct 2026 — [The Open Weights](https://theopenweights.com/categories/asr-stt). The earlier report gives 28 Oct 2026 — [earlier report table](../../reports/Dharma%20talk%20transcription%20options.md). These conflict, and neither is the vendor's own dated announcement.
- **VibeVoice‑ASR** (Microsoft). MIT, ~9B, BF16 safetensors. It handles up to 60 min of continuous audio in one pass within a 64K‑token context, and runs ASR, diarization and timestamps jointly. — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR). Release listed as 21 Jan 2026 — [The Open Weights](https://theopenweights.com/categories/asr-stt)
- **Voxtral Small 24B (2507)** (Mistral). Apache‑2.0, 24B, released July 2025. It transcribes up to 30 min (40 min for understanding) within a 32k‑token context. — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507)
- **Qwen3‑Omni‑30B‑A3B** (Instruct / Thinking / Captioner) (Alibaba). Apache‑2.0, a 30B MoE with ~3B active, released 20 Sep 2025. — [HF paper page 2509.17765](https://huggingface.co/papers/2509.17765); [The Open Weights](https://theopenweights.com/categories/asr-stt). It handles audio "up to 40 minutes per instance" — [alphaXiv overview](https://alphaxiv.org/overview/2509.17765v1)

**Secondary / mid-size audio LLMs (open weights, built for chat, ≤~10B)**
- **Kimi‑Audio‑7B** (Moonshot). Built on Qwen2.5‑7B. Code derived from Qwen is Apache‑2.0 and the rest is MIT. — [Kimi‑Audio GitHub](https://www.github.com/MoonshotAI/Kimi-Audio); [Kimi‑Audio report](https://arxiv.org/pdf/2504.18425)
- **Step‑Audio 2 mini** (StepFun). Apache‑2.0 (mini and mini Base). — [Step‑Audio 2 mini card](https://huggingface.co/stepfun-ai/Step-Audio-2-mini). Released 28 Aug 2025. A newer "StepAudio 3 Realtime" (11 Sep 2026) is omni/real-time interaction, with size and licence not stated. — [The Open Weights](https://theopenweights.com/categories/asr-stt)
- **MiMo‑Audio‑7B‑Instruct** (Xiaomi), 18 Sep 2025 — [The Open Weights](https://theopenweights.com/categories/asr-stt); [MiMo‑Audio paper](https://arxiv.org/html/2512.23808v1). Xiaomi's dedicated **MiMo‑V2.5‑ASR** (23 Apr 2026) is MIT and covers Mandarin/Cantonese/English, size not stated — [The Open Weights](https://theopenweights.com/categories/asr-stt)
- **Phi‑4‑multimodal‑instruct** (Microsoft) recommends at most **40 s** of audio for speech tasks (30 min for summarization). It was trained on ≤30 s for ASR, so longer recordings must be segmented. — [Phi‑4‑MM card](https://huggingface.co/microsoft/Phi-4-multimodal-instruct); [Phi‑4‑Mini report](https://arxiv.org/html/2503.01743v2); [HF discussion #39](https://huggingface.co/microsoft/Phi-4-multimodal-instruct/discussions/39)
- **Gemma 4 (E2B, E4B, 12B "Unified")** is trained for multilingual ASR, but audio input is capped at **30 s per clip** (25 tokens/s). — [Google Gemma audio docs](https://ai.google.dev/gemma/docs/capabilities/audio). A user report says 12B Unified did "substantially worse" than E4B in zero-shot ASR, with empty outputs and refusals — [HF discussion](https://huggingface.co/google/gemma-4-12B/discussions/6). Another developer measured 13.82% WER for E4B Q4_K_M on their own data, against the card's 4.17% on LibriSpeech‑clean — [dev.to write-up](https://dev.to/mdemin729/shipping-gemma-4-speech-recognition-in-a-windows-net-desktop-app-a-5-variant-model-selection-tour-2l8i)
- **Audio Flamingo 3** (NVIDIA): checkpoints are "for non-commercial use only" — [AF licence file](https://huggingface.co/nvidia/audio-flamingo/blob/main/LICENSE)
- **MERaLiON‑2‑10B** (Singapore A*STAR/IMDA): licence "other / meralion-public-license-v3". I could not read the commercial terms — [MERaLiON‑2‑10B card](https://huggingface.co/MERaLiON/MERaLiON-2-10B)

**Released in the last ~3 months (flag: new, and mostly aggregator-only evidence)**
- **Apriel Voice 27B Preview** (ServiceNow, ~28–29 Oct 2026). MIT, built on **Gemma 4 26B‑A4B** with a Whisper encoder plus adapter. It outputs text and tool calls, and its reported benchmarks are reasoning and agent tasks (Big Bench Audio 98.90, Speech‑BFCL 81.13), with **no WER published**. The vLLM recipe example uses 4 GPUs. — [AI Weekly](https://aiweekly.co/alerts/servicenow-open-sources-apriel-voice-27b-with-tool-calling); [explainx](https://explainx.ai/blog/apriel-voice-27b-preview-servicenow-open-speech-model-gemma-4-mit-tool-calls-2026)
- **Qwen‑Audio‑3.1‑ASR** (Alibaba, Sep/Oct 2026). Flash, Flash‑Filetrans, Flash‑Streaming, Flash‑Message and Next variants on an MoE decoder. It supports 30 languages, hotword customization (P0 person-name recall 99.43% with hotwords, internal set) and speaker-diarized output with 80 ms segment timestamps. The report gives no parameter counts and no weight release. English results are LibriSpeech clean/other 1.23/2.19 and FLEURS‑en 4.72. — [arXiv 2610.28711](https://arxiv.org/html/2610.28711v1). **Licence conflict:** "Apache 2.0, open" per [The Open Weights](https://theopenweights.com/news/qwen-audio-3-1-asr-u6lx), but "closed, API-only" per [LLMLearner](https://llmlearner.com/models/qwen-audio-3-1-asr), and Alibaba points to QwenCloud — [Qwen on X](https://x.com/Alibaba_Qwen/status/2102687258990026993?lang=en)
- **Voxtral 3** (Mistral, ~20 Oct 2026): batch and realtime STT with diarization and context biasing, but "No public weights; on-prem only via Mistral sales". Single source. — [MarkTechPost](https://www.marktechpost.com/2026/10/20/mistral-voxtral-3-speech-models-voice-agent-sdk/). The only 2026 open Voxtral STT weights are **Voxtral‑Mini‑4B‑Realtime‑2602** (Apache‑2.0, 8.87 GB). Batch Voxtral Mini Transcribe V2 and its 100‑term context biasing are API-only. — [Simon Willison](https://simonwillison.net/2026/Feb/4/voxtral-2/). The open realtime model reportedly has no text slot for bias terms — [localvoxtral issue #316](https://github.com/T0mSIlver/localvoxtral/issues/316)
- **VibeVoice‑ASR‑Streaming‑7B** (Microsoft, 2 Sep 2026; streaming, multilingual) and **VibeVoice ASR BitNet** (24 Jul 2026; CPU) — aggregator listing only; neither appears on the main VibeVoice‑ASR card — [The Open Weights](https://theopenweights.com/categories/asr-stt); [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR)
- **KRAFTON Raon‑Speech‑9B** (30 Mar 2026; English/Korean ASR+TTS) and **A.X‑K2 Raon Speech 21B‑A3B** (27 Jul 2026; MoE, any-to-any). Also **MOSS Transcribe‑Diarize** (OpenMOSS, 19 May 2026; long-form with diarization and timestamps) and **Falcon ASR** (TII, 7 Oct 2026). All are aggregator listings with no licence or WER found. — [The Open Weights](https://theopenweights.com/categories/asr-stt)
- **Granite Speech:** no 8B in the 5.0 generation. Granite Speech 5.0 ships as **2B** (Oct 2026) and **470M Turbo CTC** (Aug 2026; Apache‑2.0 plus a CC‑BY‑NC‑SA‑4.0 variant). The 8B size existed only in the 3.3 generation. — [runtimewire](https://runtimewire.com/article/ibm-granite-speech-5-turboctc-transcription); [OrcaRouter](https://www.orcarouter.ai/blog/granite-speech-5-0-470m-turboctc-apache-explained); [Granite 3.3 speech paper](https://www.arxiv.org/pdf/2505.08699)

### Inferences
- For "large, open, long-form, commercial-OK", the realistic test set is Nemotron‑3.5, VibeVoice‑ASR, Voxtral Small 24B and Qwen3‑Omni‑30B‑A3B. Kimi‑Audio, Step‑Audio 2 mini and MiMo‑Audio are ~7–8B chat models evaluated on short clips. They would need VAD chunking and offer no clear advantage over Qwen3‑ASR‑1.7B.
- Gemma 4 (30 s cap) and Phi‑4‑MM (40 s recommended) can be dropped. Their windows are shorter than Whisper's in practice, and they bring no biasing evidence.
- Apriel Voice 27B is an agent model with no ASR numbers, so it is not worth GPU time for transcription.
- The two most interesting autumn releases with built-in hotwords plus diarization (Qwen‑Audio‑3.1‑ASR, Voxtral 3) appear **not** to be open weights. Treat them as out of scope unless HF repos appear.

### Gaps
- Exact parameter counts and HF availability for Qwen‑Audio‑3.1‑ASR. Its official licence was not found.
- MERaLiON public licence v3 commercial terms (PDF not readable).
- No primary source was found for VibeVoice‑ASR‑Streaming‑7B, Raon‑Speech, MOSS Transcribe‑Diarize or Falcon ASR (sizes, licence, English WER).
- Step‑Audio 2 mini parameter count was not confirmed from the primary card in this session.

## 2. English ASR accuracy: leaderboard and independent numbers

### Takeaway
Bigger speech LLMs are **not** more accurate on spontaneous speech. In the only independent head-to-head found, Qwen3‑Omni‑30B was markedly worse than Whisper large‑v2 and Qwen3‑ASR‑1.7B on Earnings‑21 and YouTube (Yodas), and VibeVoice‑ASR‑9B was also worse than Whisper. Nemotron‑3.5 remains the only large open model with a strong long-form leaderboard result. Voxtral Small and Kimi‑Audio sit around a 6.6% mean on the old leaderboard mix, which is mid-pack.

### Cited Findings
- **Huber & Waibel 2026 (independent), unbiased WER, no context:**
  - Earnings‑21: Whisper large‑v2 13.52, Qwen3‑ASR‑1.7B 14.51, **Qwen3‑Omni‑30B 22.57**, VibeVoice‑ASR‑9B 16.71
  - Yodas: 5.79 / 6.69 / 7.97 / 9.63
  - LibriSpeech test‑other: 7.82 / 5.58 / 4.46 / 8.73
  - test‑clean: 3.66 / 2.98 / 2.56 / 3.49
  - Authors: speech LLMs "work well for read speech but they do not generalize as well as Whisper on non-read speech". Also, although D and E are 30B and 9B, "they perform worse on Earnings‑21 and Yodas."
  - Source: [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- **Nemotron‑3.5 vendor card (old 9-set methodology):** short-form mean 4.71 (AMI 7.81, Earnings22 5.29, GigaSpeech 7.18, LS clean 1.09 / other 2.60). Long-form mean 10.98 (CORAAL 13.39, Earnings21 7.57, Earnings22 11.99). URGENT24 11.00, HALAS robustness 31.50. — [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B). On the new 6 Nov 2026 leaderboard: short-form 6.13, long-form 10.52 (best open), private 8.29, URGENT24 10.94 — [earlier report](../../reports/Dharma%20talk%20transcription%20options.md), citing the [HF Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard). Vendor and leaderboard numbers differ because of the methodology change.
- **VibeVoice‑ASR on the new leaderboard:** short-form 9.54, private 14.13, URGENT24 19.50, which is the weakest of the tabulated open models — [earlier report](../../reports/Dharma%20talk%20transcription%20options.md). Its card shows only DER/cpWER/tcpWER charts, with no English WER in text — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR)
- **Voxtral Small 24B:** "Mean WER 6.62, RTFx 54.09 on hf-audio/open-asr-leaderboard" and AMI 15.27, both self-reported on the card under the old methodology — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507). A 2026 paper's table also has Kimi‑Audio‑Instruct and Voxtral‑Small at a 6.62 average over its English ASR sets, and Step‑Audio‑R1.1 at 7.91 — [arXiv 2607.05196](https://arxiv.org/pdf/2607.05196) (via search snippet; table not fully read)
- **Kimi‑Audio** reports LibriSpeech 1.28 clean / 2.42 other (vendor) — [Kimi‑Audio report](https://arxiv.org/pdf/2504.18425). A third-party table gives Step‑Audio 2 mini ~1.33 on LibriSpeech clean, with unclear column order — [hwlibre guide](https://en.hwlibre.com/what-is-stepfun-ai-step-audio-2-mini-complete-guide/)
- **Qwen3‑Omni** vendor/press figure: LibriSpeech‑other 2.48 — [VentureBeat](https://venturebeat.com/ai/chinas-alibaba-challenges-u-s-tech-giants-with-open-source-qwen3-omni-ai)
- **Qwen‑Audio‑3.1‑ASR** (weights likely closed): LS clean 1.23 / other 2.19, FLEURS‑en 4.72, against Qwen3‑ASR‑1.7B at 1.63 / 3.38 in the same table — [arXiv 2610.28711](https://arxiv.org/html/2610.28711v1)

### Inferences
- LibriSpeech-type wins for the big omni models do not carry over to spontaneous English. Qwen3‑Omni's Earnings‑21 WER is ~9 points worse than Whisper large‑v2. Dharma talks are spontaneous monologue, so the prior for Qwen3‑Omni, Kimi‑Audio, Step‑Audio and MiMo as *primary* transcribers is poor.
- No model in this group, apart from Nemotron‑3.5 and the earlier report's models, has an independent score on CORAAL, CHiME or URGENT24.

### Gaps
- No independent long-form or noisy-set (URGENT24, CHiME, CORAAL) numbers were found for Voxtral Small, Qwen3‑Omni, Kimi‑Audio, Step‑Audio 2 or MiMo‑Audio. I could not confirm whether any of them appear on the new leaderboard, because the Space did not render.

## 3. Long-form handling (max audio per call, chunking)

### Takeaway
Only Nemotron‑3.5 (1 h) and VibeVoice‑ASR (60 min) can take most talks whole. Voxtral Small (30 min) and Qwen3‑Omni (40 min) need 2–3 chunks for a 90-minute talk. Everything else needs VAD chunks of 30–40 s.

### Cited Findings
- Nemotron‑3.5: up to 1 h per request, 65,536‑token context. The 30 s encoder chunking is internal and not a recording limit. — [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- VibeVoice‑ASR: 60 min in one pass, 64K tokens — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR)
- Voxtral Small: 30 min for transcription, 40 min for understanding — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507)
- Qwen3‑Omni: up to 40 min per instance — [alphaXiv overview](https://alphaxiv.org/overview/2509.17765v1). The pretraining stage extended to 32,768 tokens with more long audio — [Qwen3‑Omni search summary / HF paper](https://huggingface.co/papers/2509.17765)
- Phi‑4‑MM: 40 s recommended for ASR — [Phi‑4‑MM card](https://huggingface.co/microsoft/Phi-4-multimodal-instruct). Gemma 4: 30 s maximum — [Gemma audio docs](https://ai.google.dev/gemma/docs/capabilities/audio)
- Qwen‑Audio‑3.1‑ASR handles long form by conditioning each segment on recently recognized text from the same session. Evidence is qualitative only. — [arXiv 2610.28711](https://arxiv.org/html/2610.28711v1)
- Research on long-form speech-LLM KV caching uses Voxtral‑mini‑3B on LibriSpeech‑Long — [WnW, arXiv 2608.22704](https://arxiv.org/pdf/2608.22704)

### Inferences
- Even with 1 h windows, splitting 90-minute talks at long silences (zazen gaps) into ≤30 min pieces is simple and lets every candidate run on identical inputs. The same VAD pass defends against hallucination.

### Gaps
- No published accuracy-versus-length curve was found for any of these models (for example, does WER drift late in a 60-minute single pass?).

## 4. Context / biasing (term lists, prompts, echo, false insertions)

### Takeaway
Nemotron‑3.5 is the only large open model with **published** contextual-ASR gains under a documented prompt format. VibeVoice accepts hotwords and posts the best correct-list BWER in Huber & Waibel, but it collapses with distractors. Qwen3‑Omni is a poor transcriber but a good **term-presence judge**, recovering most of the distractor loss when used to filter lists. Voxtral Small's open transcription mode documents no biasing input.

### Cited Findings
- **Nemotron‑3.5** prompt: "Transcribe with punctuation and capitalization. Context terms: <names and terms>." No term limit is stated.
  - Vendor WER: ContextASR‑Bench 3.33 → 1.71 with fine-grained context; Contextual Earnings22 12.54 (none) → 10.28 (global) → 9.58 (local); Preference‑ASR 7.56 → 6.16
  - Named-entity WER on ContextASR‑Bench: 12.21 → 2.20
  - The card also warns that "error rates can exceed 100% with many insertions".
  - Source: [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- **Huber & Waibel 2026** (independent), BWER with the correct words only (N=0) versus 250 distractors:
  - VibeVoice‑ASR: Earnings‑21 9.39 → 16.38; Yodas 4.17 → 27.92; LS‑other 7.88 → 24.63
  - Qwen3‑Omni: Earnings‑21 13.12 → 18.44; Yodas 5.08 → 26.98; LS‑clean 1.10 → 3.83
  - Qwen3‑ASR: Yodas 24.52 → 48.32
  - Overall degradation is "39% and 570% relative", mainly from new insertions of list words.
  - A trained biasing module on Whisper (model B) moved only 5.73 → 6.69 on Yodas.
  - Source: [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- **Same paper, filtering step:** prompting Qwen3‑Omni per utterance and per word ("is this word present?") gave **recall 93.8–98.8%**, with precision 34.1–93.7%, and cut lists to 1.0–3.7 words per utterance. Downstream BWER no longer collapsed: VibeVoice Yodas 8.17–8.71 and Qwen3‑Omni 8.46–8.71 across N=0–250. However, BWER with no distractors was worse than with the unfiltered correct list (for example, VibeVoice 8.17 vs 4.17). — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Speech LLMs can use semantic background text, not only word lists, for example favouring "Far East" over "forest" given related cues. The paper did not measure this. — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- **VibeVoice‑ASR** accepts hotwords and background info. The format is not documented on the card. — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR)
- **Voxtral Small**: transcription examples pass only language, audio and temperature, and no context or term input is documented — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507). Mistral's context biasing (≤100 terms) exists only for API models — [Simon Willison](https://simonwillison.net/2026/Feb/4/voxtral-2/); [localvoxtral #316](https://github.com/T0mSIlver/localvoxtral/issues/316)
- **Kimi‑Audio** is flagged for severe hallucination in transcription under ContextASR‑Bench's fine-grained context setting — [ContextASR‑Bench, arXiv 2507.05727](https://arxiv.org/pdf/2507.05727) (via search summary)

### Inferences
- For per-talk term lists, Nemotron‑3.5 is the only large model with both a documented prompt and vendor-measured gains. Its "context terms" are still prompt text, so the Huber & Waibel distractor pattern probably applies. That is untested for Nemotron.
- The Huber & Waibel filtering recipe fits this project's plan of building per-talk lists from first-pass phonetic matches. Qwen3‑Omni (or Nemotron's own understanding mode) could act as the "is X said in this 30 s window?" judge, with list words checked against the gold set's B‑WER/U‑WER and insertion counts.
- Using Voxtral Small's chat/understanding mode with a system prompt carrying terms might work. It is undocumented and would carry prompt-echo risk similar to Qwen3‑ASR.

### Gaps
- No independent biasing evaluation was found for Nemotron‑3.5, Voxtral Small, Kimi‑Audio, Step‑Audio 2 or MiMo‑Audio.
- No study measured prompt echo (verbatim prompt prose in output) for the large models. Echo is known for Qwen3‑ASR and Whisper from this project's own bake-off.

## 5. Hallucination on silence/music, timestamps, diarization

### Takeaway
Nemotron‑3.5 is the most complete package: no-speech abstention training, a loop guardrail, CTC word timestamps and built-in speaker tags. VibeVoice gives joint diarization and timestamps. The omni/chat models offer no timestamps and limited silence evidence. HalluAudio rates Step‑Audio 2 and MiMo‑Audio well on hallucination detection, but that is not the same as transcription hallucination.

### Cited Findings
- **Nemotron‑3.5:**
  - Hallucination: trained on no-speech abstention data with empty targets. "In rare cases, generation can loop", and the card ships a post-processing guardrail.
  - Timestamps: word timestamps come from bundled CTC heads via vLLM (V1 runner, middleware flag). They are unavailable with DFlash2 speculative decoding and in SGLang‑Omni.
  - Diarization: `<spk:N>` speaker tags, with cpWER AMI‑IHM 10.29 and CALLHOME 11.50.
  - Source: [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- **VibeVoice‑ASR**: joint speaker, time and content output. The card lists no hallucination limitations. — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR)
- **HalluAudio (ACL 2026)**: MiMo‑Audio and Step‑Audio‑2 perform well, Qwen‑Audio and others fall below 50% on several subtasks, and Kimi‑Audio shows "inconsistent recognition on transcription-related prompts". No long-form audio was tested. — [HalluAudio, arXiv 2604.19300](https://arxiv.org/html/2604.19300v1)
- A music-hallucination study of audio-language models exists ([arXiv 2609.20195](https://arxiv.org/pdf/2609.20195)). I did not read it, so no model-specific findings are reported.
- **Gemma 4 12B Unified**: empty outputs and refusals on ASR prompts (user report) — [HF discussion](https://huggingface.co/google/gemma-4-12B/discussions/6)
- **Qwen‑Audio‑3.1‑ASR**: its RL stage has a hallucination-suppression reward, but no rates are reported — [arXiv 2610.28711](https://arxiv.org/html/2610.28711v1)

### Inferences
- The chant, bell and silence clip set planned in the earlier report is the only way to rank these models on hallucination. No public benchmark covers long silences inside lectures.

### Gaps
- No silence or music insertion rates were published for Voxtral Small, Qwen3‑Omni or VibeVoice‑ASR.
- Timestamp support for Voxtral Small and Qwen3‑Omni was not documented on the pages read.

## 6. Memory footprint and inference stacks (brief)

### Takeaway
Nemotron‑3.5 needs about one 80 GB GPU (FP8 and NVFP4 builds exist). Voxtral Small needs ~55 GB in bf16. Qwen3‑Omni‑30B is in the same class. VibeVoice‑ASR (9B) fits on a 24 GB card. All have vLLM paths.

### Cited Findings
- **Nemotron‑3.5**: recommended 1× H100 80 GB. BF16, FP8 and NVFP4 builds exist (L40S FP8 only; RTX 5090 NVFP4 only), with no int4.
  - Stacks: NeMo, vLLM 0.32.0 with a NeMo plugin, Transformers (from source), SGLang‑Omni 0.2.0 (whole-file only), and GGML (RTX 5090 / PRO 6000).
  - A DFlash2 draft model is offered for speculative decoding. No smaller or streaming sibling is listed.
  - Source: [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B)
- **Voxtral Small 24B**: ~55 GB GPU RAM in bf16/fp16. Runs on vLLM ≥0.10.0 with `vllm[audio]` and Transformers ≥4.54. — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507). Community GGUF builds exist for transcribe.cpp — [handy-computer GGUF](https://huggingface.co/handy-computer/Voxtral-Small-24B-2507-GGUF)
- **VibeVoice‑ASR**: Transformers and vLLM. The card lists 12 quantizations. — [VibeVoice‑ASR card](https://huggingface.co/microsoft/VibeVoice-ASR). ~18 GB in bf16 — [earlier report](../../reports/Dharma%20talk%20transcription%20options.md)
- **Apriel Voice 27B**: the vLLM example uses 4 GPUs — [AI Weekly](https://aiweekly.co/alerts/servicenow-open-sources-apriel-voice-27b-with-tool-calling)

### Inferences
- Qwen3‑Omni‑30B‑A3B at bf16 is roughly 60–70 GB of weights (30B × 2 bytes plus audio and talker modules), so it needs an 80 GB GPU unless quantized. This is an estimate from the parameter count, not a sourced figure.

### Gaps
- No sourced memory or quantization figures were found for Qwen3‑Omni, Kimi‑Audio, Step‑Audio 2 mini or MiMo‑Audio. A separate researcher covers hardware.

## 7. Ranking by expected value for this archive, and what to test first

### Takeaway
Run **Nemotron‑3.5** first (already downloaded): it is the strongest open long-form model and the only large one with documented, measured context biasing. Second is **VibeVoice‑ASR 9B** with short per-talk hotword lists (cheap, MIT, 60 min, diarization), despite weak leaderboard numbers. Third is **Voxtral Small 24B** as a no-context generalist and second opinion for disagreement flagging. Use **Qwen3‑Omni‑30B** as a per-window term-presence filter, not as the transcriber. Skip the rest unless new open weights appear.

### Cited Findings (basis for ranking)
- Nemotron: best open long-form (10.52) on the new leaderboard, 1 h window, context-terms gains, timestamps and diarization — [Nemotron card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B); [earlier report](../../reports/Dharma%20talk%20transcription%20options.md)
- VibeVoice: best BWER with correct-only lists on Earnings‑21 and Yodas, but worse than Whisper unbiased and fragile to distractors — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Qwen3‑Omni: worst unbiased Earnings‑21 WER (22.57) but 93.8–98.8% recall as a word-presence judge — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Voxtral Small: Apache‑2.0, 30 min, 6.62 old-board mean, no documented biasing — [Voxtral Small card](https://huggingface.co/mistralai/Voxtral-Small-24B-2507)

### Inferences (ranking)
1. **Nemotron‑3.5‑Transcribe‑30B‑A4B.** Test with and without per-talk context terms (≤~30 terms), measuring B‑WER, U‑WER and insertions on silence/chant clips. Check the loop guardrail.
2. **VibeVoice‑ASR (9B).** Use the same short lists. It is worth a run because a 60‑min pass, joint diarization and the best correct-list BWER suit monologue plus Q&A. Expect worse U‑WER than Nemotron.
3. **Voxtral Small 24B.** No-context baseline only. It is useful as a ROVER partner or disagreement flagger. Its 55 GB bf16 footprint makes it cost about the same as Nemotron while offering less.
4. **Qwen3‑Omni‑30B‑A3B as filter.** Re-implement the Huber & Waibel step over 30 s VAD windows to prune each talk's candidate list before Nemotron or VibeVoice decoding.
5. **Low priority:** Kimi‑Audio‑7B, Step‑Audio 2 mini and MiMo‑Audio‑7B (short-clip chat models, mixed hallucination evidence); Phi‑4‑MM and Gemma 4 (30–40 s windows); Apriel Voice 27B (no ASR numbers); Audio Flamingo 3 (non-commercial); MERaLiON‑2 (licence unclear, Singapore-English focus).
6. **Watch list (not testable as open weights today):** Qwen‑Audio‑3.1‑ASR (hotwords plus diarization, MoE; licence conflict), Voxtral 3 (reportedly no public weights), VibeVoice‑ASR‑Streaming‑7B, MOSS Transcribe‑Diarize, Raon‑Speech. All of these need primary-source checks.

### Gaps
- No public evidence covers how any of these models handle Sino-Japanese or Sanskrit romanizations specifically. Only the gold set can answer that.
- Nemotron "new variants": the card lists none beyond the DFlash2 draft model, NIM serving and FP8/NVFP4 builds. The latter part of the card (characters 100k–142k) was not read, so smaller details may be missing.
