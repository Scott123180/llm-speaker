# Open techniques for rare/domain-term accuracy in open-weight ASR and speech-LLMs (as of Nov 2026)

Scope note: this builds on `reports/Dharma talk transcription options.md` ("Short per-talk term lists beat giant glossaries everywhere except NeMo" and "Post-correction must propose edits, never rewrite the text"). Facts already given there (HyPoradise, Alpha Cephei ROVER test, JSON-edit correction, RECOVER, error-aware retriever, vendor keyterm limits) are not repeated except where new numbers were found. Project-specific observations (Whisper-turbo term errors 13% -> 3% with per-talk prose prompts; prompt echo in Whisper large-v3 and Qwen3-ASR; Parakeet GPU-PB "koan" -> "Khan") come from the task brief, not from external sources.

## 1. Context prompting for speech-LLMs: formats, list length, distractor sensitivity, prompt-echo mitigation

### Takeaway
Whether a speech-LLM tolerates a term list depends on whether it was trained with distractor and negative lists. Nemotron 3.5 Transcribe was trained that way, and it keeps keyword precision at about 98% even with a whole-session vocabulary. Qwen3-ASR, Qwen3-Omni and VibeVoice lose 39–570% relative biased-WER once 250 distractors are added, and they favour terms at the start of the list. Keep lists short and specific to each clip, use the model's own trained template, and detect echo and loops in code.

### Cited Findings
- **Distractor collapse (independent study).** Huber & Waibel compare Whisper large-v2 plus two trained biasing modules (A: context attention; B: dynamic vocabulary) with Qwen3-ASR-1.7B, Qwen3-Omni-30B and VibeVoice-ASR-9B on Earnings-21, LibriSpeech and Yodas. On Yodas, BWER with oracle terms only, then with 250 distractors, was: Qwen3-ASR 24.52 -> 48.32; Qwen3-Omni 5.08 -> 26.98; VibeVoice 4.17 -> 27.92; Whisper+B 5.73 -> 6.69. Unbiased WER barely moved. — [arXiv 2608.05759](https://arxiv.org/html/2608.05759)
- Without any context, Yodas BWER was 48.07 for Whisper-v2, 56.80 for Qwen3-ASR, 51.57 for Qwen3-Omni and 60.19 for VibeVoice. So even with distractors, a context list still roughly halves rare-word errors relative to no context. — [arXiv 2608.05759](https://arxiv.org/html/2608.05759)
- **Order sensitivity.** The speech-LLMs "perform better if a word is at the beginning of the prompt." The authors sorted lists alphabetically for fairness and published no numeric ablation. The trained biasing modules are order-agnostic. — [arXiv 2608.05759](https://arxiv.org/html/2608.05759)
- **Pre-filtering.** A per-word "is this word present?" check with Qwen3-Omni had 34–94% precision and 94–99% recall. At 250 distractors it recovered much of the loss (Yodas: Qwen3-ASR 48.32 -> 25.72; VibeVoice 27.92 -> 8.71). At N=0, though, filtering made BWER worse in every case (e.g. VibeVoice Yodas 4.17 -> 8.17). The authors conclude filtering "does not close the gap" with module B on non-read speech. — [arXiv 2608.05759](https://arxiv.org/html/2608.05759)
- **Nemotron 3.5 Transcribe training.** 15.5% of training examples were Contextual ASR, in five variants: fine (spoken entities), coarse (domain label only), partial, distractor (spoken entities plus "similar-sounding or related ones that are not spoken") and negative (only absent entities). Per the report, "the negative and distractor variants teach the model to ignore listed terms that are not spoken." — [Nemotron 3.5 Transcribe Technical Report](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Nemotron results.** On Contextual Earnings-22 (15 s clips), keywords raised recall from 58% to 96% when only the clip's own keywords were listed (local), and to 90% when the whole call's inventory was listed (global), "while the precision stays at 98%." Keyword F1 was 73.0 / 97.1 / 93.5 (none / local / global) and WER 12.54 / 9.58 / 10.28. Qwen3-ASR-1.7B scored F1 69 / 92 / 87 on the same test. — [Nemotron 3.5 report, Table 11](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **ContextASR-Bench (English), fine entity lists.** NE-WER: Nemotron 12.21 -> 2.20; Qwen3-ASR-1.7B 11.75 -> 2.76; Qwen3-Omni-30B 7.83 -> 1.55; Kimi-Audio 14.33 -> 6.68; Qwen2.5-Omni-7B 16.07 -> 7.38. Whisper-large-v3 with no context scored 29.56. A domain label alone ("coarse") had "little effect" for any model. — [Nemotron 3.5 report, Table 11](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Exact Nemotron templates.** For a whole-session list: `This audio may contain the following words or phrases (some may not be present in the clip): {kw1}, {kw2}, ...` followed by `Transcribe the English audio into text, ensuring all punctuation marks are included.` A domain variant reads `This audio belongs to the {domain} field and may contain the following words or phrases: ...`. — [Nemotron 3.5 report, App. A.5](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf). The NeMo docs recommend `Transcribe with punctuation and capitalization. Context terms: <names and terms>.` in the user message, with the system prompt left empty. — [NeMo docs: Nemotron 3.5 Transcribe](https://docs.nvidia.com/nemo/speech/nightly/speechlm2/nemotron_transcribe.html) (from a search snippet; the page was not fetched)
- **Reasoning mode must be off.** Inference must disable the chat template's reasoning mode (an empty `<think></think>`); otherwise "the model generates a reasoning trace that ignores the audio." — [Nemotron 3.5 report, App. B.3](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Nemotron hardware.** 30B MoE with about 4B active parameters and a 65,536-token context ([NeMo docs](https://docs.nvidia.com/nemo/speech/nightly/speechlm2/nemotron_transcribe.html), via search snippet). Supported in BF16 on A100 80GB, H100/H200, RTX PRO 6000 Blackwell (96 GB) and DGX Spark; in FP8 on L40S; NVFP4 on Blackwell. "A single H100 GPU is sufficient" with vLLM and BF16. — [Nemotron 3.5 report, Table 17 and §4](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Prompt leakage with long lists.** In LOGIC, prompting with 460+ person names on Phi-4-mini produced output that "is unpredictable and may leak the whole phrase list ... This phenomenon happens to not only Phi-4-mini but also other speech LLMs such as GPT-4o." — [LOGIC, arXiv 2601.15397](https://arxiv.org/pdf/2601.15397v1)
- **Prompt format for Whisper.** In CB-Whisper, a plain comma-separated entity list worked on in-domain test sets but could cause hallucinations on harder data. A "spoken-form" prompt that reads like transcribed speech reduced this. — [arXiv 2309.09552](https://arxiv.org/html/2309.09552v3) (from a search snippet). Keyword-Guided Adaptation found Whisper with a prompt performed *worse* than plain Whisper in its setting. — [arXiv 2406.02649](https://arxiv.org/pdf/2406.02649) (from a search snippet). Whisper's prompt is capped at 224 tokens, and attention weights later prompt tokens more heavily. — [arXiv 2410.18363](https://arxiv.org/pdf/2410.18363) (from a search snippet)
- **Loop guardrail.** Nemotron borrows Qwen3-ASR's `detect_and_fix_repetitions`, raising the maximum block to 4,096 characters: it collapses a character repeated at least 21 times, or a 1–4,096-character block repeated at least 20 times. It changed 7 of 451 long-form recordings and 6 of 20 AliMeeting sessions (cpCER 55.37 -> 34.95). It "cannot recover speech that the model skipped while looping." — [Nemotron 3.5 report, App. E](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- A 2025 Interspeech paper on ranking bias words reports that extra spoken-style prompt content can draw attention away from the true bias words when the list is large. — [Hou et al., Interspeech 2025](https://www.isca-archive.org/interspeech_2025/hou25_interspeech.pdf) (from a search snippet)

### Inferences
- Nemotron 3.5 Transcribe is the strongest open candidate for "prompt with the per-talk list." It is the only model found with published evidence of training on distractor and negative lists, and it holds 98% keyword precision with session-wide lists. That directly targets the project's prompt-echo and false-insertion problem. It needs about 80 GB in BF16 (A100/H100 80GB, RTX PRO 6000) or an L40S (48 GB) in FP8. It does not fit a 24 GB consumer card at full precision.
- For Qwen3-ASR (and probably Whisper large-v3), keep lists to the terms most likely present in each **chunk**, not the whole talk. Put the most likely terms first. Use the term-list template rather than prose for speech-LLMs; prose prompts may be what invites echo. The project's Whisper-turbo success with prose prompts fits CB-Whisper's "spoken-form prompt" finding.
- **Echo detection in code.** Flag a segment when its output shares a long n-gram (e.g. 5 or more tokens) with the prompt, when its word rate is implausible for the audio duration, or when it trips the repetition guardrail. Re-decode flagged segments without the prompt or with a shorter one. This is an inference; no paper measuring prompt-echo rates on long-form audio was found.
- Huber & Waibel's data suggest that for a 20–40-term per-talk list, of which maybe 5–15 are spoken per chunk, Qwen3-ASR would sit between their N=0 and N=250 numbers. Their N=50/100 values were not extracted.

### Gaps
- No published numbers were found for Voxtral, Granite-Speech or Kimi-Audio with distractor-laden lists. Kimi-Audio appears only in ContextASR-Bench with oracle lists.
- No study was found of prompt echo (the model outputting the prompt instead of transcribing) on long-form audio, or of the effect of chunk length on it.
- Huber & Waibel give no hardware details and no exact prompt template for the speech-LLMs; they say only that the context goes "inside the system prompt" for Qwen3-ASR.
- No numeric word-order ablation was found.

## 2. Decode-time biasing: GPU-PB/TurboBias, CTC-WS, NGPU-LM n-gram fusion, Whisper/LLM trie biasing

### Takeaway
NeMo GPU-PB is the most mature open decode-time method. With beam search it roughly doubles key-phrase recall (e.g. 29% -> 76%) at a cost of about 5–7 points of precision. It runs at negligible speed cost on a single workstation GPU and tolerates 20K-phrase lists with a lowered weight. Over-boosting is controlled with the fusion weight, `c_unk`, and by pruning short or already-recognized phrases. N-gram fusion (NGPU-LM) adds a small, complementary gain only when there is enough clean domain text. Trie/logit biasing now exists for Whisper and for speech-LLMs (LOGIC) but is research code.

### Cited Findings
- **TurboBias / GPU-PB results** (FastConformer models trained on 24K h; single RTX A6000). On CSTalks (200-phrase list), key-phrase F-score, then WER:
  - RNN-T beam: 44.2 (P97/R29) -> 82.9 (P90/R76); WER 12.8 -> 9.6
  - CTC beam: 35.0 -> 83.2; WER 13.8 -> 10.2
  - AED (Canary-style) beam-3: 53.7 -> 82.4; WER 12.5 -> 10.2

  Gains were smaller on Earnings21 (893 phrases), with RNN-T beam F-score 55.8 -> 74.0 and WER 14.3 -> 14.2. Throughput fell only about 2–5% (e.g. RTFx 1466 -> 1420). — [TurboBias, arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **Greedy vs beam.** Greedy decoding gains much less than beam search; on CSTalks, RNN-T greedy F-score went 42.5 -> 70.4. Beam search roughly doubles the recall gain. — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **Other NeMo methods (CSTalks).** CTC-WS word spotter on CTC greedy: F 79.8 (P90/R72), WER 10.9, but RTFx fell from 2232 to 906. NGPU-LM built from the context list only reached F 58.5. pyctcdecode reached F 74.0 but at RTFx 29. — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **List-size robustness.** Adding about 20K LLM-generated 1–3-word phrases to the 200-phrase list (RNN-T beam, weight lowered from 1 to 0.7 "to limit false accepts") moved F-score from 81.1 to 78.4 and WER from 9.86 to 11.42, about 5% slower. Accuracy loss was attributed to "additional false accepts." — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **Over-boosting controls used in the paper:**
  - Context score c0 = 1 for depth-1 arcs; deeper arcs use c0·β + ln(depth) with β ≈ 2.
  - Unknown-token score `c_unk` is 0 by default; "a value close to c0" is recommended to reduce accuracy loss on words outside the list.
  - The fusion weight λ is tuned on a dev set.
  - Two-letter phrases were removed from Earnings21.
  - For MultiMed, phrases the baseline already got right more than 70% of the time, and phrases occurring fewer than 10 times, were removed.
  - For AED, the EOS score is raised by the maximum tree boost so the decoder does not end early.

  — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **Complementarity.** GPU-PB plus NGPU-LM on MultiMed (CTC beam): WER 15.09 -> 13.55. Each method alone gave 14.47 and 14.00. — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2)
- **NGPU-LM from domain text.** In NVIDIA's ATCO2 guide, a KenLM n-gram built from about 4.8K normalized words of Gold text plus a small external set (converted to `.nemo` for NGPU-LM) moved fine-tuned Parakeet only from 19.72% to 19.14% WER, and Nemotron streaming from 19.96% to 19.86%. English WER rose slightly (2.30 -> 2.33). — [HF blog: Fine-tune ASR with NVIDIA speech skills](https://huggingface.co/blog/nvidia/fine-tune-asr-with-nvidia-nemotron-speech-skills). NeMo docs call NGPU-LM GPU fusion for CTC/RNN-T/TDT/AED, "recommended for production." — [NeMo docs](https://docs.nvidia.com/nemo/speech/3.0.0/asr/asr_language_modeling_and_customization.html) (from a search snippet)
- **NGPU-LM failure mode.** A GitHub issue reports that MALSD beam decoding with LM fusion often improves overall WER, but some utterances suffer severe deletions on parakeet-tdt-0.6b-v2 at `ngram_lm_alpha` ≥ 0.1. — [NVIDIA-NeMo/Speech #14907](https://github.com/NVIDIA-NeMo/Speech/issues/14907) (from a search snippet)
- **Trie biasing for Whisper.** A zero-shot prefix-trie module for Whisper beam search adds uniform per-token rewards and uses synthetic multi-pronunciation variants of hotwords, with no fine-tuning. — [arXiv 2508.17796](https://arxiv.org/html/2508.17796) (from a search snippet; numbers not extracted). K-step prediction avoids "reward revocation" in trie biasing. The same paper notes that a synthetic-TTS accent mismatch hurt biasing. — [arXiv 2509.09196](https://arxiv.org/pdf/2509.09196) (from a search snippet)
- **LOGIC, trie biasing in a speech-LLM's logits** (Phi-4-mini-MM; 460–2,100 person names per locale; 11 locales):
  - Average 9% relative entity-WER reduction with only +0.30% false-alarm rate, at a "robust" bonus λ ≈ 0.4–0.6.
  - An "aggressive" λ of 0.8–1.0 gives 17% average, up to 29% on fr-FR.
  - Latency is +2.8% RTF on A100.
  - Uses an initial prefix bonus plus revocation when the full entity is not completed.
  - Microsoft paper; no public code link was found.

  — [LOGIC, arXiv 2601.15397](https://arxiv.org/pdf/2601.15397v1)
- **Two-stage speech-LLM biasing.** PTC-Bias selects at most K bias words by phoneme-level temporal competition before prompting, evaluated with 100–2,000 distractors (Rare5k protocol). — [arXiv 2609.28727](https://arxiv.org/html/2609.28727) (from a search snippet; numbers not extracted)

### Inferences
- **"koan" -> "Khan".** This fits the paper's false-accept pattern. Practical controls:
  - Raise `c_unk` toward c0.
  - Lower λ.
  - Drop glossary entries that the baseline Parakeet already gets right (the MultiMed ">70% already correct" rule), and short or common-sounding items.
  - Use per-talk lists rather than the full 687-term glossary for the boosting tree, or a two-tier list with a lower weight for the general core.
  - Pre-capitalize to match model output.
  - Tune on the gold set by key-phrase precision and recall, not WER alone.
- **Building an NGPU-LM.** The ATCO2 result (about 5K words of text, about 0.6 absolute WER gain) suggests the LM needs far more text. The roughly 6,000 existing Whisper transcripts (tens of millions of words) are large but contain the very misspellings to be fixed. Correct them first with the glossary's `misheard -> right` map, or drop sentences containing known misheard forms, then train a token-level n-gram with the model's own tokenizer, as the guide does. Tune `ngram_lm_alpha` below 0.1 and watch for deletions.
- **Hardware.** GPU-PB and NGPU-LM run on any CUDA GPU that runs Parakeet (0.6B). The paper used one RTX A6000 (48 GB); a 12–24 GB card should suffice for inference. This is an inference; VRAM was not stated.

### Gaps
- No published GPU-PB numbers were found for romanized Japanese, Chinese or Sanskrit terms in English speech, or for terms that are acoustically far from English.
- No independent replication of TurboBias gains outside NVIDIA authors was found.
- Whisper trie-biasing numbers (arXiv 2508.17796) and faster-whisper `hotwords` effectiveness were not quantified in sources found this session.
- No evidence was found on data size versus gain for an archive-scale (more than 10M words) domain n-gram used with Parakeet.

## 3. Fine-tuning on a few hours of in-domain data and/or synthetic TTS for rare terms

### Takeaway
Fine-tuning gives the largest gains when the vocabulary is truly new. Synthetic TTS of term-dense text, mixed with real speech and replayed general data, is the standard recipe. Nemotron's medical case study halved WER with about 150 h of synthetic speech in about 14 GPU-hours. A Whisper LoRA on about 22 h of synthetic entity audio took about 7 A10G-hours per language. Risks:
- Regressions on general speech, from about 0.1–0.3 points up to 9 points.
- Overfitting to TTS voices.
- Terms never seen in training are still missed.

About 4 h of gold is better spent on dev/test than on training.

### Cited Findings
- **Nemotron 3.5 Transcribe medical case study.** About 150 h of synthetic speech from LLM-written medical text and catalogs (MagpieTTS and Kokoro voices), mixed with real accented and medical speech:
  - WER fell from 24.03% (base model, best prompt) to 12.06% on held-out speakers, versus 14.92% for Whisper-large-v3.
  - "The entire process took about 14 GPU-hours, including text generation and speech synthesis" (single GB300).
  - LibriSpeech test-clean went from 1.49% to 1.75%.
  - Limitation: drug brands "never heard in training are not" recognized.

  — [Nemotron 3.5 report, App. B.2](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Distractor-aware prompts during fine-tuning.** "Some prompts include a term list with near-miss distractors, in which the correct term is missing a quarter of the time, so that the model learns to copy a spelling only when the audio supports it." — [Nemotron 3.5 report, App. B.2](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Nemotron fine-tuning recipe.**
  - For about 10 h of in-domain data, freeze the model and train the ASR encoder branch, the projection, and LoRA (dim 32, alpha 64) on the LLM. This "typically outperforms partial unfreezing of the LLM, which in turn outperforms full fine-tuning."
  - Learning rate 1e-4, 300–2,000 steps; below about 20 h of audio, size batches for 15–25 steps per epoch.
  - Select checkpoints by decoding the dev set; check a general-domain set as well.
  - Checkpoint averaging and ROVER across independently trained runs are "reliable" gains.
  - "Blending an out-of-domain corpus into a small in-domain one usually hurt"; relabel any auxiliary corpus with the model itself.
  - References teach surface form: unpunctuated references teach the model to drop punctuation.
  - Run-to-run variance is 1–6 points on small test sets.

  — [Nemotron 3.5 report, App. B.1/B.3](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Nemotron fine-tuning VRAM.** Training LoRA, encoder and projection with activation checkpointing takes "about 65 + 0.95 × B/1000 GB" for B tokens per batch, so even small batches need an 80 GB-class GPU or larger. Full fine-tuning needs about 6× the BF16 weight memory. A toolkit with LoRA merge and vLLM evaluation is in NeMo Speech `examples/speechlm2/finetuning`. — [Nemotron 3.5 report, App. B](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **Parakeet and Nemotron-streaming fine-tuning (ATCO2).** Staged recipe: 314.7 h silver plus English replay (80/20), then 0.42 h gold plus English (85/15). Parakeet TDT 0.6B v3 went from 53.08% to 20.00% WER, with English 2.17 -> 2.31. Gold-only tuning without silver gave 26.09% domain WER but raised English WER to 5.16%. GPU hours were not reported. — [HF blog: NVIDIA speech skills](https://huggingface.co/blog/nvidia/fine-tune-asr-with-nvidia-nemotron-speech-skills)
- **Whisper LoRA with synthetic entity-dense audio (Indic).**
  - Data: about 19,500 TTS clips (about 22 h) after a CER filter that rejected 10–15%, mixed at 20–30% synthetic with 70–80% real speech.
  - LoRA rank 16, α 32, on q/k/v/out in encoder and decoder, 4,000 steps, LR 4e-5.
  - Compute: about 7 GPU-hours on an A10G (24 GB), about $13 per language.
  - Entity hit rate rose from 0.027 to 0.473 on Telugu.
  - A FLEURS-only LoRA control left entity hit rate unchanged (0.020), so the synthetic entity audio drove the gain.
  - Costs: read-prose WER regressed by up to +9.4 points (Hindi FLEURS); the authors flag possible overfitting to the TTS acoustic family, a single-speaker native check, and contraindicated adapters for two languages.

  — [TTS–STT Flywheel, arXiv 2605.03073](https://arxiv.org/html/2605.03073)
- **Synthetic-only adaptation** of Whisper with decoder-side LoRA has been demonstrated for domains such as music, weather and sports. — [arXiv 2501.12501](https://arxiv.org/html/2501.12501v1) (from a search snippet). Fine-tuning on synthetic data helps, but a gap to real audio remains, attributed to distribution mismatch. — [arXiv 2509.09196](https://arxiv.org/pdf/2509.09196) (from a search snippet)
- **Qwen3-ASR fine-tuning (non-peer-reviewed).**
  - A blog reports LoRA on Qwen3-ASR-1.7B with Qwen3-TTS synthetic speech plus balanced replay cut a domain CER from 24.54% to 5.61%. — [evergreentree.github.io](https://evergreentree.github.io/speech2text/) (from a search snippet)
  - An Arabic-dialect model card reports LoRA "degraded it (0.510, overfit)." Full fine-tuning of the 0.6B model on one 32 GB GPU for about 102 minutes worked instead. — [friendli.ai model card](https://friendli.ai/models/oddadmix/qwen3-asr-0.6b-arabic-dialectal) (from a search snippet)
  - Another card used LoRA rank 64 with ms-swift on H100s. — [friendli.ai Lemura](https://friendli.ai/models/lemuralabs/lemura-arabic-asr-qwen3) (from a search snippet)

### Inferences
- **Fine-tuning plan for this archive.**
  - Write term-dense English sentences in dharma-talk style with each glossary term, using several plausible pronunciations, in the model's own style.
  - Synthesize them with several TTS voices, ideally including the cloned voices of the main teachers if licensing allows.
  - Mix with real archive audio whose existing transcripts agree with a second system: high-agreement segments serve as "silver," following the ATCO2 staged recipe.
  - Add general-English replay.
  - Train prompts with near-miss distractors and the correct term absent 25% of the time.
  - Keep the 4 h gold set as dev/test only.
- **GPU estimates.**
  - Parakeet or Whisper LoRA: a single 24 GB GPU (A10G, RTX 4090) for single-digit to tens of GPU-hours.
  - Qwen3-ASR 0.6B full fine-tuning: one 32 GB GPU for about 2 h.
  - Nemotron 3.5 fine-tuning: one 80 GB+ GPU (H100/H200, or an RTX PRO 6000 96 GB) for roughly 10–20 GPU-hours, based on the 14 GPU-hour medical case on GB300.

  These are extrapolations from the cited runs.
- The Nemotron finding that unseen brand names stay wrong means fine-tuning should cover the whole 687-term glossary. Decode-time or prompt biasing is still needed for terms added later.

### Gaps
- No study was found of fine-tuning ASR on Japanese, Chinese or Sanskrit loanwords in English speech, or on religious or lecture domains.
- No controlled numbers were found on how many synthetic utterances per rare term are needed. The Indic paper deferred its synthetic-fraction ablations.
- No reliable Qwen3-ASR VRAM or GPU-hour figures were found beyond model cards and blogs.
- No Whisper large-v3 or Parakeet result was found showing forgetting with only about 4 h of real in-domain data.

## 4. Multi-system combination: ROVER, LLM hypothesis fusion (N-best GER), confidence selection

### Takeaway
LLM-based correction helps with rare words only when the LLM is fine-tuned on matched (synthetic) error pairs, sees N-best hypotheses, and gets a light phonetic hint. Zero-shot and N-best-only prompting barely move rare-word recall. Classic ROVER is a cheap, reliable gain across independently trained systems or runs, but needs diverse systems. The earlier report's conclusion still stands: any LLM step should propose constrained edits.

### Cited Findings
- **Yamashita et al., Interspeech 2025** (Whisper-large-v3-turbo; Llama-3.3-70B or GPT-4o-mini for GER):
  - Prompt-only and N-best-only baselines gave "modest" gains (CSJ CER 15.5 -> 15.6; recall 44.5 -> 47.5).
  - Fine-tuning the GER LLM on synthetic rare-word error pairs (LLM text -> TTS -> ASR) plus N-best raised MedTxt rare-word recall from 27.6% to 85.0% (GPT-4o-mini).
  - With Llama, MedTxt CER went 18.8 -> 10.3 (recall 27.6 -> 84.7).
  - Adding full IPA hurt badly (overfitting to rare words; MedTxt CER 21.9, CSJ 25.2).
  - An LLM-generated "simplified phonetic" hint gave the best WER/CER, e.g. LibriSpeech 2.7 -> 2.6, where without it WER rose to 2.9 from over-correction.
  - The Llama runs used LoRA rank 16 on 8×H100 for 10 epochs.

  — [arXiv 2505.17410](https://arxiv.org/pdf/2505.17410)
- **Hallucinated entities.** LOGIC's authors note that GEC "can generate entity phrases that are not even spoken," motivating decode-time biasing instead. — [arXiv 2601.15397](https://arxiv.org/pdf/2601.15397v1)
- **ROVER across runs.** The Nemotron fine-tuning guidance lists "voting over the hypotheses of independently trained runs (e.g., with ROVER)" as a reliable gain. — [Nemotron 3.5 report, App. B.3](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **ROVER over one model's N-best.** An early study found ROVER over a single model's N-best was worse than the 1-best baseline. Another uses ROVER as a training-free baseline whose output then feeds LLM correction. — [Cambridge thesis/paper](https://www.repository.cam.ac.uk/bitstreams/55e62442-b4f4-4212-bbd1-a6e24d427dc1/download) (from a search snippet)
- **Phoneme-augmented correction.** PMF-CEC claims faster and more robust correction than LLM methods under large biasing lists. — [arXiv 2506.11064](https://arxiv.org/pdf/2506.11064) (from a search snippet)

### Inferences
- **Cheapest combination.** Run 2–3 diverse systems (e.g. Parakeet+GPU-PB, Nemotron or Qwen3-ASR with a prompt, Whisper with a prompt). Align them and accept a glossary term only when at least 2 systems produce it or a phonetic match to a known `misheard` form agrees. Otherwise keep the majority word. This also counters prompt echo: an echoed phrase in one system is outvoted.
- **GER only with proper training.** If an LLM corrector is used, the evidence favours fine-tuning a mid-sized open LLM on synthetic error pairs. The pairs can be generated by running the project's own ASR systems on TTS of glossary-dense text. Give it N-best or multi-system hypotheses plus a simplified phonetic hint, and keep the JSON-edit constraint from the earlier report. A 70B LoRA needs multi-GPU (8×H100 in the paper). An 8B-class model on one 24–48 GB GPU is plausible but untested here.

### Gaps
- No 2026 independent study of LLM fusion across multiple open ASR systems for rare words was found this session.
- No numbers were found for confidence-based per-segment selection between systems for rare-word accuracy.

## 5. Evaluating biasing: biased/unbiased WER, term recall vs false insertions, keyword F-score

### Takeaway
Report at least four numbers per system on the gold set: overall WER, BWER on the listed terms, UWER on everything else, and keyword precision/recall/F1. Precision captures false insertions such as prompt echo or "koan" -> "Khan." Run each under two list conditions: an oracle per-clip list, and the realistic per-talk list with its absent terms.

### Cited Findings
- **BWER and UWER.** Huber & Waibel report both, with N=0 and N=250 distractor conditions. Biasing can lower BWER while raising UWER, e.g. module B on LibriSpeech test-other: UWER 5.68 -> 6.48 at 250 distractors. — [arXiv 2608.05759](https://arxiv.org/html/2608.05759)
- **Key-phrase F-score with P/R.** TurboBias reports F-score with precision and recall, plus WER and RTFx. Precision drops (97 -> 90) as recall rises (29 -> 76), which makes false accepts visible. — [arXiv 2508.07014](https://arxiv.org/html/2508.07014v2). NeMo ships a key-phrase F-score script for this. — [NeMo word boosting docs](https://docs.nvidia.com/nemo/speech/latest/asr/asr_customization/word_boosting.html) (as cited in the earlier project report)
- **Local vs global lists.** Contextual Earnings-22 reports WER plus keyword P/R/F1 under "local" (only the clip's spoken keywords) and "global" (whole-call inventory) lists, scored with OpenBench normalization. — [Nemotron 3.5 report](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **ContextASR-Bench** adds named-entity WER and named-entity false-negative rate (NE-FNR) under no-context, coarse and fine settings. — [Nemotron 3.5 report](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf)
- **LOGIC** reports entity WER, entity recall and false-alarm rate (ΔFAR). — [arXiv 2601.15397](https://arxiv.org/pdf/2601.15397v1)
- **Rare-word recall and precision** are reported in the style of earlier work; WER is the primary objective, then recall without loss of precision. — [arXiv 2505.17410](https://arxiv.org/pdf/2505.17410)
- **Run-to-run variance** on small test sets was 1–6 points for fine-tuned Nemotron, so small differences need repeated runs or bootstrap intervals. — [Nemotron 3.5 report, App. B.1](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3.5-Transcribe-Technical-Report.pdf). The Indic paper explicitly lacked bootstrap CIs, with n = 86–102 entity items. — [arXiv 2605.03073](https://arxiv.org/html/2605.03073)

### Inferences
- **Metrics for `eval/report.py`:**
  - (a) BWER over gold-set occurrences of glossary terms, and UWER on all other words.
  - (b) Term precision: correct glossary-term outputs divided by all glossary-term outputs. This catches false insertions such as "Khan", or an echoed term not in the reference.
  - (c) Term recall.
  - (d) An echo/insertion rate: words in the hypothesis that appear in the prompt but not in the reference.
  - (e) Run every biasing method with both an oracle list and the realistic per-talk list.
  - (f) Bootstrap confidence intervals over talks, since about 4 h of gold gives only a few hundred term occurrences.
- Use alignment-based scoring (as in NeMo's script or OpenBench) rather than bag-of-words, so that a term inserted in the wrong place is not counted as a hit.

### Gaps
- No standard metric specific to prompt echo was found in the literature. The project's own prompt-echo metric (from the Phase 2 bake-off) appears novel relative to sources found.
- Exact OpenBench keyword-matching rules were not fetched.
