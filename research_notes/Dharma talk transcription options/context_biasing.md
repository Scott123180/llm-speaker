# Context Biasing / Domain-Vocabulary Conditioning for ASR (state as of Nov 2026)

Scope: every practical way to give an ASR system prior knowledge of domain vocabulary (Zen/Japanese/Sanskrit/Pali terms, lineage names) and per-talk context (title, speaker, date) for an archive of ~6,500 English dharma talks. Current baseline: OpenAI Whisper CLI `turbo`, no prompt.

Research method note: ~20 searches/fetches. Primary sources read directly: openai/whisper `decoding.py` and `transcribe.py` (main branch), SYSTRAN/faster-whisper `transcribe.py` (master), OpenAI cookbook Whisper prompting guide, OpenAI speech-to-text guide, NVIDIA NeMo "Word Boosting" docs (latest), TurboBias arXiv abstract, Qwen3-ASR technical report, Huber & Waibel arXiv 2608.05759 (full text). Hosted-API limits/prices partly come from search snippets and third-party pages and are flagged as such. Items not verified this session are in Gaps.

## 1. Whisper `initial_prompt` / `prompt` mechanics, limits, risks, best practices

### Takeaway
Whisper's prompt is not an instruction; it is fake "previous transcript" text placed after a `<|startofprev|>` token, truncated to the last 223 tokens (n_text_ctx 448 // 2 − 1). In the reference CLI it only applies to the first 30 s window unless `carry_initial_prompt=True` (newer openai-whisper) is set; otherwise it survives only indirectly via `condition_on_previous_text`. It reliably fixes spellings of names/terms that are actually spoken and transfers style (casing, punctuation), but long or list-like prompts raise hallucination risk, and `condition_on_previous_text` is the main cause of repetition loops.

### Cited Findings
- Code: in `DecodingTask._get_initial_tokens`, a string prompt is encoded as `" " + prompt.strip()` and inserted as `[sot_prev] + prompt_tokens[-(n_ctx // 2 - 1):] + tokens` — i.e. only the last 223 tokens survive (n_ctx = 448 text context), and earlier text is silently dropped. Prompt may also be a list of token IDs. — [openai/whisper decoding.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/decoding.py)
- `prefix` is different: it is appended after the SOT sequence (i.e. it forces the start of the *current* window's output), truncated to `n_ctx // 2 - sample_len`; the code comment says `prompt` is "for the previous context" and `prefix` "to prefix the current context". — [openai/whisper decoding.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/decoding.py)
- `initial_prompt` docstring: "Optional text to provide as a prompt for the first window." — [openai/whisper transcribe.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/transcribe.py)
- `carry_initial_prompt`: "If carry_initial_prompt is True, `initial_prompt` is prepended to the prompt of each internal `decode()` call"; if the context is too full the prompt is left-sliced. Code: `remaining_prompt_length = n_text_ctx // 2 - 1 - len(initial_prompt_tokens)`; `decode_options["prompt"] = initial_prompt_tokens + all_tokens[nignored:][-remaining_prompt_length:]`. CLI help warns it may reduce the effectiveness of `condition_on_previous_text`. — [openai/whisper transcribe.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/transcribe.py)
- `condition_on_previous_text`: "if True, the previous output of the model is provided as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop". — [openai/whisper transcribe.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/transcribe.py)
- Prompt reset: `if not condition_on_previous_text or result.temperature > 0.5: prompt_reset_since = len(all_tokens)` — so once temperature fallback above 0.5 occurs, the previous-text prompt is dropped (with `carry_initial_prompt` the initial prompt is still re-prepended). Related guards: `compression_ratio_threshold` (gzip ratio, default treats highly repetitive output as failed), `no_speech_threshold` + `logprob_threshold`, `hallucination_silence_threshold` (requires `word_timestamps=True`; skips silent periods longer than the threshold when a possible hallucination is detected). — [openai/whisper transcribe.py](https://raw.githubusercontent.com/openai/whisper/main/whisper/transcribe.py)
- OpenAI cookbook findings: listing correct names in the prompt made Whisper spell people/product names as intended (e.g. "P3-Quattro", "O3-Omni"); a sentence-style prompt fixed "BBQ", "whisky", "doughnuts". Whisper imitates prompt style (casing, punctuation, even ellipses); short prompts are less reliable than multi-sentence ones; only the last 224 tokens are used; instructions in prompts are not obeyed ("Format lists in Markdown" does nothing); prompts cannot override what is heard; rare styles are followed less reliably. — [OpenAI Cookbook: Whisper prompting guide](https://developers.openai.com/cookbook/examples/whisper_prompting_guide)
- OpenAI API docs (Nov 2026): "For `whisper-1`, prompts have a 224-token limit and provide less control than the recommended transcription model"; "Whisper doesn't follow instructions like a general-purpose text model." — [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- CB-Whisper authors report that long prompts raise compute cost and cause hallucinations, and that a "spoken form" prompt imitating a transcript of someone speaking reduces hallucination relative to a bare keyword list. — [CB-Whisper, arXiv 2309.09552](https://arxiv.org/abs/2309.09552v1) (search-snippet level; LREC-COLING 2024: [ACL Anthology](https://aclanthology.org/2024.lrec-main.262.pdf))

### Inferences
- For a 30–90 min talk, the plain CLI `--initial_prompt` affects only the first 30 s directly; the vocabulary "propagates" only if the terms appear in decoded text and `condition_on_previous_text` stays on. To bias every window, use `carry_initial_prompt=True` (Python API / CLI `--carry_initial_prompt True` in newer openai-whisper) or faster-whisper `hotwords` (see §2). Keep the carried prompt short (e.g. 60–120 tokens) because it eats the 223-token budget that otherwise holds the preceding transcript.
- Recommended prompt shape (from cookbook + CB-Whisper evidence): a natural, well-punctuated sentence or two in the style you want, containing the terms, rather than a comma list, e.g. `"Dharma talk by Daido Loori at Zen Mountain Monastery on the Heart Sutra (Maka Hannya Haramita Shingyo): zazen, dokusan, sesshin, koan, kensho, Dogen, Shakyamuni, Avalokiteshvara."` Per-talk prompts can be built from the title/speaker metadata plus a ~30–60 term core glossary; terms from the title are the highest-value additions.
- Because Whisper copies the prompt's style, a prompt with full punctuation/capitalization also stabilizes the output format; a lowercase or list-like prompt can degrade punctuation.
- Over-biasing failure mode for Whisper: during silence, bells and chanting, the decoder can emit prompt text or glossary words (hallucinated insertions), and with `condition_on_previous_text` a hallucinated line can repeat. Mitigations: VAD pre-segmentation (faster-whisper `vad_filter=True`, WhisperX), `hallucination_silence_threshold` with word timestamps, keep `compression_ratio_threshold`, and consider `condition_on_previous_text=False` combined with `carry_initial_prompt=True` so the glossary is present but error text doesn't snowball.

### Gaps
- No published, controlled measurement found of Whisper `initial_prompt` rare-word recall gain on long-form audio (the cookbook is qualitative). Huber & Waibel (§3) evaluated trained biasing modules, not plain prompting.
- Exact openai-whisper release version that introduced `carry_initial_prompt` was not verified (it is present on `main`).
- whisper.cpp: not verified this session. To my knowledge it exposes `--prompt` (initial prompt) and has a `--carry-initial-prompt`-style option in recent versions, but treat as unverified.

## 2. faster-whisper `hotwords` and `prefix`; whisper.cpp

### Takeaway
faster-whisper's `hotwords` is not acoustic biasing: it is just text inserted into the `<|startofprev|>` prompt slot of *every* window (ahead of the previous-text tokens), capped at ~223 tokens, and silently ignored on windows where a `prefix` is set. Functionally it is "initial_prompt carried to every window", with the same strengths and hallucination risks. No rigorous public evaluation of its effectiveness was found.

### Cited Findings
- Docstrings: `initial_prompt` — "prompt for the first window"; `prefix` — "Optional text to provide as a prefix for the first window"; `hotwords` — "Hotwords/hint phrases to provide the model with. Has no effect if prefix is not None"; `prompt_reset_on_temperature` — resets prompt if temperature above this value (only when `condition_on_previous_text` is True). — [faster-whisper transcribe.py](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py)
- `get_prompt()` logic: `if previous_tokens or (hotwords and not prefix): prompt.append(tokenizer.sot_prev)`; hotwords encoded as `" " + hotwords.strip()` and truncated to `max_length // 2 - 1`; then `prompt.extend(previous_tokens[-(max_length // 2 - 1):])`. `prefix` is passed only when `seek == 0`, while `hotwords` is passed on every window. The batched pipeline has the same `hotwords` parameter. — [faster-whisper transcribe.py](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/faster_whisper/transcribe.py)

Usage sketch (faster-whisper, consistent with the code above):
```python
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")  # fits 8 GB 3070 Ti
segs, info = m.transcribe(
    "talk.mp3",
    language="en",
    hotwords="Daido Loori, Dogen, zazen, dokusan, sesshin, koan, kensho, Avalokiteshvara",
    initial_prompt="Dharma talk at Zen Mountain Monastery on the Heart Sutra.",
    condition_on_previous_text=False,   # reduces loops; hotwords still apply every window
    vad_filter=True,                    # drop long silences/bells before decoding
)
```

### Inferences
- Since hotwords + previous tokens share the same prompt region, a long hotword string crowds out continuity context; keep the hotword list short and per-talk.
- `prefix` is mostly useless for biasing long-form audio (first window only, and disables hotwords for that window).

### Gaps
- No benchmark of faster-whisper `hotwords` vs. no-prompt rare-word recall was found.
- whisper.cpp prompt flags not verified (see §1 Gaps).

## 3. Research on Whisper contextual biasing and fine-tuning (CB-Whisper, trie/TCPGen-style, prompt-tuning, LoRA)

### Takeaway
Dedicated biasing modules trained on top of a frozen Whisper cut biased-word WER by 37–88% relative while leaving other words essentially unchanged, and they are robust to large distractor lists — more robust than speech-LLM prompting (Huber & Waibel, Aug 2026). CB-Whisper (TTS-based keyword spotting → prompt) reports >20% average recall gain. LoRA fine-tuning on in-domain data gives large domain gains but causes forgetting; alpha/rank choices matter (high alpha/r caused hallucinations). None of these research systems are turnkey for a hobby pipeline; fine-tuning requires corrected transcripts.

### Cited Findings
- Huber & Waibel, "How to Recognize New Words: A Comparison Between Context Biasing Methods and Speech LLMs" (arXiv 2608.05759, 6 Aug 2026): two Whisper-large-v2 context-biasing methods (A, B; extra context encoder via mBART-50 encoder + context attention, trained on Common Voice, Whisper frozen except new params) vs. speech LLMs Qwen3-ASR-1.7B, Qwen3-Omni-30B, VibeVoice-ASR-9B. Test sets: Earnings-21, LibriSpeech test-clean/other, Yodas (non-read YouTube). — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
  - Biasing methods: BWER improves 37–70% relative (A) and 48–88% relative (B) with the correct word in the list; UWER essentially unchanged; adding up to 250 distractors raises BWER only up to 2% (A) / 17% (B) relative; B's extra errors are mostly insertions of wrongly predicted "dynamic tokens" (i.e., over-biasing). — same source
  - Speech LLMs with context, no distractors: best BWER on LibriSpeech (Qwen3-Omni 1.10% clean / 3.57% other) and VibeVoice-ASR on Earnings-21 (9.39%) and Yodas (4.17%). But with 250 distractors BWER degrades 39–570% relative (e.g. Qwen3-ASR Yodas BWER 24.52% → 48.32%; VibeVoice Yodas 4.17% → 27.92%; Whisper+B Yodas 5.73% → 6.69%). Speech LLMs are also sensitive to word order in the prompt. — same source
  - Unbiased baselines on non-read speech: Whisper large-v2 WER 13.52% (Earnings-21) and 5.79% (Yodas) vs Qwen3-ASR 14.51% / 6.69%, Qwen3-Omni 22.57% / 7.97%, VibeVoice-ASR 16.71% / 9.63% — "speech LLMs work well for read speech but … do not generalize as well as Whisper on non-read speech." — same source
  - Filtering the list per utterance with Qwen3-Omni (yes/no "is this word in the audio") had 93.8–98.8% recall, and recovered much of the distractor loss, but speech LLMs still trailed method B on non-read sets (e.g. Yodas BWER 8.17% vs 5.73%). — same source
  - Conclusion: "dedicated context biasing methods remain the more robust choice when a clean word list can be supplied and resilience to noisy or long lists matters, whereas speech LLMs offer a more flexible" interface (free-form context, semantic disambiguation). — same source
- CB-Whisper (Li et al., 2023; LREC-COLING 2024): TTS-synthesized reference audio for each user term + CNN keyword spotter over the utterance; detected terms are passed to Whisper as a spoken-form prompt; Whisper kept frozen because fine-tuning on small data caused catastrophic forgetting; reported >20% average entity-recall gain over Whisper on Aishell, ACL and internal sets. — [arXiv 2309.09552](https://arxiv.org/abs/2309.09552v1); [ACL Anthology](https://aclanthology.org/2024.lrec-main.262.pdf) (snippet-level)
- LoRA on Whisper-small for ATC: rank 64 cut domain WER 137.2% → 18.8% but LibriSpeech WER rose 3.1% → 8.3%; higher ranks forgot more. (Single dataset, high-school journal; indicative only.) — [NHSJS 2026](https://nhsjs.com/2026/evaluating-lora-rank-selection-for-fine-tuning-whisper-on-air-traffic-control-communications/)
- Swiss German Whisper fine-tune: the common LoRA alpha = 2r heuristic caused decoder hallucinations; lowering alpha/r from 2.0 to 0.2 eliminated them and improved WER; LoRA ≈ full fine-tuning (25.32% vs 25.60%). — [arXiv 2606.07608](https://arxiv.org/html/2606.07608v1)
- LoRA forgets less than full fine-tuning on Whisper; smaller Whisper models are less tolerant to forgetting; mixing original-domain data mitigates forgetting. — [arXiv 2408.10680 (Interspeech 2024)](https://arxiv.org/pdf/2408.10680); [arXiv 2407.06800](https://arxiv.org/pdf/2407.06800)
- Task-vector fusion for rare words: fine-tuning for rare words boosts targets but causes catastrophic forgetting; task-vector approach mitigates. — [arXiv 2512.21894](https://arxiv.org/pdf/2512.21894) (snippet-level)

### Inferences
- For this archive, a LoRA fine-tune is feasible because the project already produces LLM-cleaned transcripts; a few dozen hours of human-verified talks (the same teacher, same room acoustics) is the plausible scale, but I found no source quantifying "hours needed for rare-word gains" — treat any number as a guess. Use low alpha/r, mix in general English data, and evaluate on held-out talks for hallucination in silence/chanting.
- Huber & Waibel's methods A/B are research code, not packaged; the practical analogue for open models today is NeMo GPU-PB (§4).

### Gaps
- TCPGen / trie-based deep biasing for Whisper (e.g. Sun et al.) and Whisper prompt-tuning/soft prompts were not re-verified this session; no turnkey open implementation was confirmed.
- No source gave a data-size vs. rare-word-recall curve for Whisper LoRA.

## 4. NVIDIA NeMo: Parakeet / Canary word boosting (GPU-PB / TurboBias, CTC-WS)

### Takeaway
NeMo has the most mature open, decode-time context biasing: GPU-PB ("TurboBias", ASRU 2025) is a GPU boosting-tree shallow fusion that works for CTC, RNN-T/TDT (Parakeet) and AED (Canary) in greedy and beam search, scales to ~20K phrases without noticeable slowdown, needs no retraining, and supports per-utterance phrase lists for TDT/RNN-T greedy. CTC-WS (word spotter) is an older CTC-only alternative with explicit alternative-spelling support. The docs give no headline accuracy numbers; `boosting_tree_alpha` must be tuned on your data.

### Cited Findings
- GPU-PB supports CTC, RNN-T/TDT and AED (Canary), greedy and beam search including CUDA graphs mode; applied only at decoding as shallow fusion ("You do not need to retrain the ASR model"); phrases from `boosting_tree.key_phrases_file` (one per line), `boosting_tree.key_phrases_list`, or a prebuilt `boosting_tree.model_path`. — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- Recommended params: `context_score=1.0`; `depth_scaling=2.0` for CTC/RNN-T/TDT and `1.0` for Canary; `boosting_tree_alpha` "should be tuned". For models that output capitalization (Canary, parakeet-tdt-0.6b-v2) key phrases must be capitalized in advance. — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- CLI example:
  ```bash
  python examples/asr/speech_to_text_eval.py model_path=${MODEL_NAME} dataset_manifest=${EVAL_MANIFEST} \
    ctc_decoding.strategy="greedy_batch" \
    ctc_decoding.greedy.boosting_tree.key_phrases_file=${KEY_WORDS_LIST} \
    ctc_decoding.greedy.boosting_tree.context_score=1.0 \
    ctc_decoding.greedy.boosting_tree.depth_scaling=2.0 \
    ctc_decoding.greedy.boosting_tree_alpha=${BT_ALPHA}
  ```
  Other decoders: `rnnt_decoding.greedy` / `rnnt_decoding.beam` (`malsd_batch`), `multitask_decoding.beam` (Canary). — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- Per-utterance biasing: supported for greedy label-looping RNN-T/TDT (incl. cache-aware streaming) via `enable_per_stream_biasing=True` and `BiasingRequestItemConfig(boosting_model_cfg=BoostingTreeModelConfig(key_phrases_list=[...]), boosting_model_alpha=...)` passed as `partial_hypothesis=[Hypothesis.empty_with_biasing_cfg(...)]` to `asr_model.transcribe(...)`; or a `biasing_request` field per manifest line with `asr_streaming_infer.py`. Caching via `cache_key`; "near-zero overhead" vs global boosting. — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- Evaluation helper: `scripts/asr_context_biasing/compute_key_words_fscore.py` computes key-phrase F-score. — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- CTC-WS: `scripts/asr_context_biasing/eval_greedy_decoding_with_context_biasing.py` with `apply_context_biasing`, `context_file`, `decoder_type` (ctc or rnnt head of hybrid models), `beam_threshold`, `context_score`, `ctc_ali_token_weight`; list-valued params grid-searched by WER. Context-file lines give a word plus alternative spellings separated by underscores (e.g. `nvidia_nvidia_n video`), useful to map common misrecognitions to the target. `ctc_ali_token_weight` helps prevent false acceptance of biasing words. — [NeMo Word Boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html)
- TurboBias paper (Andrusenko, Bataev, Grigoryan, Lavrukhin, Ginsburg; Aug 2025; ASRU 2025): universal framework for CTC, Transducer, AED; shallow fusion for greedy and beam; "up to 20K items" with no noticeable speed degradation; claims to surpass open-source context-biasing approaches in accuracy and speed. — [arXiv 2508.07014](https://arxiv.org/abs/2508.07014v2)
- NGPU-LM (GPU n-gram LM fusion) is listed as "Recommended for Production" and can run together with GPU-PB in the same decoding pass. — [NeMo docs (search snippet)](https://docs.nvidia.com/nemo-framework/user-guide/26.02/nemotoolkit/asr/asr_language_modeling_and_customization.html)

### Inferences
- An n-gram LM (NGPU-LM) trained on the project's own cleaned transcripts + a GPU-PB phrase list is a strong, cheap combination for this archive: the LM captures the teacher's phrasing ("the Buddha said…", "practice of zazen"), the phrase list targets rare tokens. Both run on an 8 GB GPU for 0.6B Parakeet.
- CTC-WS alternative spellings let you encode known Whisper/Parakeet errors (e.g. `dokusan_dokusan_doku san`, `sesshin_sesshin_session`) — but mapping a common English word like "session" is an over-biasing hazard; prefer only nonsense-ish misspellings.
- Caveat: Parakeet's English models are trained on read/conversational English; Japanese/Sanskrit terms are BPE-tokenized into subwords, and boosting only helps if the acoustic model gives them non-negligible probability. Expect gains for plausible-sounding words (koan, zazen), less for long Sanskrit compounds.

### Gaps
- Docs give no numeric WER/F-score gains; the TurboBias paper's tables were not extracted this session.
- Parakeet v2/v3, Canary-1B-flash, Canary-Qwen-2.5B model-card specifics (max audio length, whether Canary-Qwen accepts a text context prompt) were not verified this session. Canary-Qwen-2.5B is an LLM-decoder model; whether GPU-PB applies to it was not confirmed (the docs mention AED Canary only).
- Config key names differ across NeMo doc versions (nightly, 26.02, 3.0.0); verify against the installed version.

## 5. LLM-based / audio-language-model ASR with text context prompts

### Takeaway
Qwen3-ASR (Jan 2026, Apache-2.0, 0.6B/1.7B) is the clearest open model explicitly trained for context biasing via the system prompt and handles up to 20 min per call; VibeVoice-ASR (Microsoft, Jan 2026, MIT, 9B) takes up to 60 min per pass and accepts hotwords/background context. Both give large gains when the list is short and relevant, but degrade sharply with many irrelevant terms and are weaker than Whisper on non-read (spontaneous) English — which is what dharma talks are. Mistral Voxtral offers context biasing (up to ~100 terms) on its hosted batch API.

### Cited Findings
- Qwen3-ASR technical report (arXiv 2601.21337, v2 30 Jan 2026): models Qwen3-ASR-1.7B, Qwen3-ASR-0.6B, Qwen3-ForcedAligner-0.6B; Apache 2.0; max 1200 s (~20 min) audio per call for ASR, 300 s for the aligner; SFT includes "context biasing data" — "the model learns to utilize the context tokens inside the system prompt as background knowledge". English WER (1.7B vs Whisper-large-v3): GigaSpeech 8.45 vs 9.76; Tedlium 4.50 vs 6.84; VoxPopuli 9.15 vs 12.05; LibriSpeech clean 1.63 vs 1.51. No context-biasing numbers in the report. — [Qwen3-ASR Technical Report](https://arxiv.org/html/2601.21337)
- The report says the model was trained to behave as ASR-only and ignore natural-language instructions in the prompt (anti-injection); Alibaba Cloud docs describe passing word lists, paragraphs, or both as system-message context, capped at 10,000 tokens, and say irrelevant text is tolerated. — [Qwen3-ASR report](https://arxiv.org/html/2601.21337); [Alibaba Cloud (Qwen) docs](https://docs.platform.qianwenai.com/developer-guides/accuracy-tuning/speech-recognition) (both via search summary; the 10K-token cap is a hosted-API figure)
- Independent evaluation contradicts the "tolerates irrelevant text" claim for long lists: Qwen3-ASR Yodas BWER 24.52% with only relevant words → 48.32% with 250 distractors; Qwen3-ASR robust to ~10 distractors. — [Huber & Waibel arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- VibeVoice-ASR: released 21 Jan 2026, MIT license, 9B encoder-decoder, up to 60 min continuous audio in a single pass within 64K tokens, joint ASR + diarization + timestamps; users can supply custom hotwords / background context. — [Microsoft Tech Community announcement](https://techcommunity.microsoft.com/t5/microsoft-foundry-blog/introducing-vibevoice-asr-longform-structured-speech-recognition/ba-p/4501276); [comfyui-wiki news](https://comfyui-wiki.com/en/news/2026-01-21-microsoft-vibevoice-asr-release) (details via aggregators; exact hotword API unverified). Huber & Waibel quote its card: users can "supply customized context - ranging from hotword lists to background descriptions". — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- VibeVoice-ASR in the comparison: best BWER with relevant-only context on Earnings-21 (9.39%) and Yodas (4.17%), but Yodas BWER 27.92% at 250 distractors; unbiased WER worse than Whisper large-v2 on Earnings-21 (16.71 vs 13.52) and Yodas (9.63 vs 5.79). — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Speech LLMs can use semantic context (e.g. disambiguating "Far East" vs "forest" given "Pacific Rim" cues), which word-level biasing cannot. — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Mistral Voxtral: hosted batch endpoint accepts context biasing with up to ~100 words/phrases; realtime endpoint does not; open Voxtral Mini 4B Realtime has no prompt slot. — [GitHub issue, localvoxtral #316](https://github.com/T0mSIlver/localvoxtral/issues/316) (developer discussion, not official); Voxtral Transcribe 2 context biasing via "a simple API parameter" — [VentureBeat](https://venturebeat.com/technology/mistral-drops-voxtral-transcribe-2-an-open-source-speech-model-that-runs-on)
- Research on hotword retrieval + RL for LLM-ASR context biasing (Dec 2025) exists, indicating the distractor problem is being addressed by retrieving a small relevant subset first. — [arXiv 2512.21828](https://arxiv.org/html/2512.21828v1) (not read in detail)

### Inferences
- For Qwen3-ASR / VibeVoice, keep per-call context small: title + speaker + date + the 10–30 terms most likely in *that* talk (e.g. derived from the title, or from a first-pass Whisper transcript fuzzy-matched against the glossary). Do not paste a 500-term glossary.
- Qwen3-ASR 1.7B fits on the 8 GB 3070 Ti (bf16 ≈ 3.4 GB weights) but needs ≤20 min chunks; VibeVoice-ASR 9B (≈18 GB bf16) needs the H100/GH200 or quantization.
- Because dharma talks are spontaneous, non-read speech, Huber & Waibel's finding that speech LLMs' unbiased WER trails Whisper on non-read speech is directly relevant: test on your own audio before switching.

### Gaps
- Not verified this session: Phi-4-multimodal, IBM Granite Speech (3.3/4.x), Kimi-Audio, Step-Audio 2, Qwen2.5-Omni/Qwen3-Omni context-prompt behavior, Canary-Qwen-2.5B prompt support, Voxtral open-weight (Mini/Small) prompt support and max audio length. These are general instruction-following audio LLMs; whether a "use these spellings" prompt reliably helps them was not measured in any source I found except Qwen3-Omni in Huber & Waibel.
- VibeVoice-ASR official hotword API (parameter name) unconfirmed.

## 6. Hosted APIs with vocabulary/context features (and pricing)

### Takeaway
All major vendors now have a keyterm list and/or free-text prompt. OpenAI's newest `gpt-transcribe` adds a `keywords` field plus `prompt`; `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` are deprecated (shutdown 26 Feb 2027). Deepgram Nova-3 keyterms: 500-token budget. AssemblyAI Universal-3 Pro: up to 1,000 keyterms (+$0.05/h) or an open prompt, mutually exclusive. ElevenLabs Scribe v2: up to 1,000 keyterms in batch. Speechmatics: `additional_vocab` with `sounds_like`. Prices are ~$0.15–0.40/hour, so 6,500 talks (~5,000–7,000 h if ~1 h each) cost roughly $1–3K — but the user prefers local.

### Cited Findings
- OpenAI (Nov 2026 docs): recommended model `gpt-transcribe` — "combine the prompt with the `keywords` and `languages`"; `prompt` = "unstructured context about the recording"; `keywords` = "literal terms you expect to hear", one per line, no `<`, `>`, CR/LF (request rejected otherwise); "Keywords are hints, not required output. Include only relevant terms … evaluate whether they improve accuracy without causing unspoken terms to appear." `gpt-4o-transcribe`/`gpt-4o-mini-transcribe`/`whisper-1` deprecated, shutting down 26 Feb 2027; `gpt-4o-transcribe-diarize` doesn't support prompts; 25 MB file limit; no keyword count limit or pricing stated on the page. Python passes `keywords`/`languages` via `extra_body`. — [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- gpt-4o-transcribe pricing: commonly cited ~$0.006/min (~$0.36/h), mini ~$0.003/min (~$0.18/h); token-based billing $6/M audio input tokens also cited. Sources are third-party and disagree on basis. — [costgoat](https://costgoat.com/pricing/openai-transcription); [OpenAI community thread](https://community.openai.com/t/audio-model-pricing-is-unclear/1149806)
- Deepgram: keyterm prompting only on Nova-3 (and Flux), not Nova-2; budget of 500 tokens across all keyterms (≈100 words); earlier launch material said "up to 100 key terms"; developers report confusion about what counts as a token. — [Deepgram multilingual keyterm blog](https://deepgram.com/learn/deepgram-expands-nova-3-with-10-new-languages-and-multilingual-keyterm-prompting); [deepgram-python-sdk issue #503](https://github.com/deepgram/deepgram-python-sdk/issues/503); [Deepgram changelog 2025-12-10](https://developers.deepgram.com/changelog/2025/12/10). Nova-3 price ~$0.0043/min batch (~$0.26/h) per a third-party page — [convertaudiototext](https://convertaudiototext.com/blog/deepgram-nova-3-explained) (unverified vs. Deepgram pricing page)
- AssemblyAI: Universal-3 Pro keyterms prompting up to 1,000 words/phrases (up from 200 on Universal-2), add-on $0.05/h on a $0.21/h base; open-field prompting and keyterms are mutually exclusive — put key terms inside the prompt to get both. — [AssemblyAI U3 Pro prompt engineering blog](https://www.assemblyai.com/blog/universal-3-pro-prompt-engineering). Pricing page (via snippet) lists keyterms ≤1,000 phrases, max 6 words/phrase, for "Universal-3.5 Pro"; 100 for realtime — [AssemblyAI pricing](https://www.assemblyai.com/pricing) (model naming inconsistent across snapshots)
- ElevenLabs Scribe v2: keyterms up to 1,000 terms of ≤50 chars in batch (raised from 100), 50 terms ≤20 chars realtime; >100 keyterms imposes a 20 s minimum billable unit. — [ElevenLabs STT docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text); [ElevenLabs blog](https://elevenlabs.io/blog/scribe-v2-just-got-an-upgrade)
- Speechmatics: `additional_vocab` entries are strings or `{content, sounds_like}` objects; `sounds_like` only for en, de, es, fr, it, pt; limit reported as 1,000 entries. — [TypeWhisper issue #294](https://github.com/TypeWhisper/typewhisper-mac/issues/294) (third-party; verify with Speechmatics docs)
- Contextual Earnings-22 benchmark (Argmax authors, Mar 2026) evaluates six baselines in two families — keyword prompting and keyword boosting — and finds both reach "comparable, significantly improved accuracy" at scale. — [arXiv 2604.07354](https://arxiv.org/abs/2604.07354)

### Inferences
- `sounds_like` (Speechmatics) and CTC-WS alternative spellings (NeMo) are the only mechanisms found that let you specify pronunciation, which matters for Japanese terms pronounced anglicized (e.g. "Maka Hannya Haramita Shingyo").
- Hosted APIs are useful as a quality benchmark on a 20–50 talk sample even if production stays local.

### Gaps
- Google Gemini audio prompting (Gemini 2.5/3 audio input, ~9.5 h audio limit per request in older docs), Speechmatics official docs, and official gpt-transcribe pricing were not verified this session.
- Contextual Earnings-22's per-vendor numbers were not extracted.

## 7. Which approach is best for rare foreign-origin religious terms; over-biasing risk

### Takeaway
Evidence (Huber & Waibel 2026; OpenAI's own keyword warning; NeMo's `ctc_ali_token_weight`) says: decode-time biasing with a clean, short, per-talk list is the reliable win; huge lists hurt prompt-based systems (Whisper prompt, speech LLMs) via false insertions, while trained/shallow-fusion biasers (NeMo GPU-PB, Whisper+biasing modules) tolerate long lists. For this archive the pragmatic stack is: (1) Whisper/faster-whisper with a per-talk natural-sentence prompt carried to every window + VAD; (2) benchmark against Parakeet-TDT + GPU-PB (+ NGPU-LM trained on own transcripts); (3) optionally Qwen3-ASR with a short per-talk context; (4) keep the existing LLM cleanup stage with the glossary for post-correction, plus a glossary-term insertion audit.

### Cited Findings
- Biasing modules: BWER −37% to −88% relative with ≤2–17% relative degradation at 250 distractors; speech LLMs: 39–570% relative BWER degradation at 250 distractors and sensitive to word order. — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- Per-utterance list filtering (high-recall yes/no audio check) recovers much of the speech-LLM loss. — [arXiv 2608.05759](https://arxiv.org/pdf/2608.05759)
- OpenAI: "Keywords are hints, not required output. Include only relevant terms … evaluate whether they improve accuracy without causing unspoken terms to appear." — [OpenAI STT guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- Long prompts cause hallucinations in Whisper; spoken-form prompts reduce this. — [CB-Whisper arXiv 2309.09552](https://arxiv.org/abs/2309.09552v1)
- NeMo GPU-PB scales to 20K phrases without slowdown and supports per-utterance lists; CTC-WS `ctc_ali_token_weight` guards against false acceptance. — [NeMo docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html); [arXiv 2508.07014](https://arxiv.org/abs/2508.07014v2)

### Inferences
- Build per-talk lists, not one global list: core 20–40 high-frequency Zen terms + names from the title/speaker metadata + terms detected in a first-pass transcript (fuzzy/phonetic match of Whisper output against the full glossary, e.g. "dokusan" vs "doku son"). This mimics the paper's "filtering" step cheaply.
- Over-biasing hotspots specific to this audio: silences, bells, chanting (Heart Sutra recited in Sino-Japanese), and audience Q&A at low volume — exactly where Whisper hallucinates. Measure "glossary-term insertions per hour in non-speech regions" on a sample, comparing no-prompt vs prompt.
- Chanting segments: no biasing method will reliably transcribe Sino-Japanese chant; better to detect and label them (or replace with known liturgy text) than to bias.
- Since the pipeline already has an LLM cleanup stage and a likeness gate (>90% similarity), a glossary-aware LLM correction pass is a complementary, low-risk fix for residual misspellings — but its fixes are bounded by what ASR produced; ASR-side biasing increases the share of terms that are recoverable.
- Model scale: a small benchmark (e.g. 20 talks with hand-corrected glossary terms) measuring term recall, term false insertions, and overall WER is the deciding experiment; published numbers come from earnings calls / LibriSpeech / YouTube, not dharma talks.

### Gaps
- No published evaluation on religious/liturgical or Japanese-loanword vocabulary in English speech was found.
- No head-to-head of Whisper prompting vs NeMo GPU-PB vs Qwen3-ASR on the same long-form spontaneous English data was found (Huber & Waibel used trained Whisper biasing modules, not plain prompting, and segment-level audio).
