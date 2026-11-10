# LLM Post-Correction of ASR Transcripts and Domain Evaluation (state as of Nov 2026)

Scope: (a) how to do LLM post-correction of Whisper output without paraphrase drift, and (b) how to build an evaluation setup to compare ASR systems/pipelines on ~6,500 English Zen dharma talks. Project context: the current pipeline sends whole raw transcripts to Llama 3.1 8B/70B via Ollama for punctuation, paragraphs and error fixing; outputs drift and a >90% similarity gate rejected 40-60% of talks under earlier prompts.

Source-age legend: [2023] = older but foundational; [2025]/[2026] = recent. "(non-primary)" = blog, aggregator or vendor/tutorial page. Search/fetch was done through an LLM summarizer, so some numbers come from abstracts or partial page reads; noted where relevant.

---

## Q1. Generative error correction (GER) research: when does LLM correction help vs. hurt WER?

### Takeaway
LLM correction reliably helps when the LLM is **fine-tuned** (LoRA) on hypothesis-to-reference pairs, is given **N-best lists or confidence/entity evidence**, and works on **short units**; it frequently **hurts** when it is a zero-shot, small (≈8B), quantized model rewriting long, already-accurate text — which is close to this project's current setup. Whisper output in particular is a weak target for unconstrained LLM correction; gains concentrate on rare named entities when a candidate list is supplied.

### Cited Findings
**Foundational GER benchmarks [2023]**
- HyPoradise (NeurIPS 2023 Datasets & Benchmarks) is the first open GER benchmark: >334k N-best-hypothesis/transcription pairs across domains; the LLM *generates* the transcript instead of picking one hypothesis, and can recover tokens absent from the N-best list — [arXiv 2309.15701](https://arxiv.org/abs/2309.15701v2)
- HyPoradise fine-tuned results on Whisper N-best (WER %, baseline → best H2T-LoRA): WSJ 4.5 → 2.2; ATIS 8.3 → 1.7; CHiME-4 11.1 → 6.6; TED-LIUM 3 8.5 → 4.6; SwitchBoard 15.7 → 14.1; CORAAL 21.4 → 19.2. LLMs used: T5-large (0.75B) and LLaMA-13B with LoRA — [HyPoradise HTML](https://arxiv.org/html/2309.15701v1)
- HyPoradise also documents cases where correction **hurt**: full fine-tuning (H2T-ft) on SwitchBoard (15.9/18.4 vs 15.7) and CORAAL (23.1/22.9 vs 21.4), attributed to overfitting and utterance length; LibriSpeech test-other got worse with both methods (3.7 → 3.8/3.9); **zero-shot LLaMA-13B did not improve** on CHiME-4 or CV-accent — [HyPoradise HTML](https://arxiv.org/html/2309.15701v1)
- In-context (GPT-3.5) correction gave ~17-21% relative WER reduction only with 10 in-context examples; zero-shot (n=0) gains were small (e.g., WSJ-eval92 7.6 → 7.3) — [HyPoradise HTML](https://arxiv.org/html/2309.15701v1)
- Whispering LLaMA (EMNLP 2023) fuses Whisper acoustic features into LLaMA for N-best correction, reporting 37.66% relative WER reduction vs. N-best hypotheses; code/models at github.com/Srijith-rkr/Whispering-LLaMA — [arXiv 2310.06434](https://arxiv.org/abs/2310.06434)

**Evidence that naive correction hurts [2025-2026]**
- Confidence-guided correction paper (disordered speech): naive LLM correction on Parakeet output on TORGO **nearly doubled WER (10.83% → 20.01%)**; the paper cites prior work that LLM correctors "overcorrect when ASR outputs are already accurate, sometimes increasing word error rate" — [arXiv 2509.25048](https://arxiv.org/html/2509.25048)
- Interspeech 2025 child-conversation study: LLMs substantially improved CTC outputs but gave **minimal improvement on Whisper outputs**; adding conversational context hurt via error propagation — [Xu et al., Interspeech 2025](https://www.isca-archive.org/interspeech_2025/xu25g_interspeech.pdf) (via search summary; full text not read)
- Three-stage framework ablation: an unconstrained base LLM correction raised CER from 5.06 to 53.10 (hallucination); adding error pre-detection, iterative correction and answer verification brought it to 4.69 — [arXiv 2505.24347](https://arxiv.org/pdf/2505.24347) (via search summary)
- Practitioner experiment (Alpha Cephei, Mar 2025, Russian telephony, 5-best): 1-best 15.9 WER; **plain ROVER 14.8**; Gemini Flash 2.0 Lite 14.6; gemma-2-9b 16.0 (no gain); gemma-3-4b 16.7; Qwen2.5-7B and other ~8B 4-bit models were "unstable, WER 40 to 100+"; ~25% of 8B-class outputs hallucinated; LLMs overcorrected rare proper names they did not know; prompt formatting alone moved WER 26 → 16. Author concludes ROVER is about as accurate and far more stable — [Alpha Cephei blog (non-primary, practitioner)](https://alphacephei.com/nsh/2025/03/15/generative-error-correction.html)
- Whisper "courtside" project report (2026): LLM post-fix improved 19.2% of cases and degraded 19.5%, mean WER unchanged at 0.217; validation agents were added to block dubious name changes — [arXiv 2602.18966 (student project report)](https://arxiv.org/html/2602.18966v1)
- An overview notes prompt-only (zero/few-shot) LLM correction is "generally ineffective, often increasing error rates" — [Emergent Mind topic page (non-primary aggregator)](https://www.emergentmind.com/topics/asr-error-correction-aec)

**Where it helps: named entities with retrieval [2025-2026]**
- RAG for named-entity correction: queries generated from errorful ASR retrieve entities (phonetic + orthographic encoders), which are fed with the hypothesis to an LLM adapted for correction — [Pusateri et al., Retrieval Augmented Correction of NE Speech Recognition Errors](https://www.researchgate.net/publication/390536206_Retrieval_Augmented_Correction_of_Named_Entity_Speech_Recognition_Errors)
- DeRAGEC (ACL Findings 2025) filters retrieved name candidates with phonetic similarity and augmented definitions, without training, improving over RAGEC — [ACL Anthology](https://aclanthology.org/2025.findings-acl.786.pdf)
- Generative Annotation for ASR NE Correction (EMNLP 2025) separates retrieval (speech-sound similarity) from correction and notes generative approaches "tend to over-correct" — [ACL Anthology](https://aclanthology.org/2025.emnlp-main.1052.pdf)
- EDM 2026 classroom-speech paper: **both** a filtered context of similar-sounding names **and** explicit phonetic information were needed for the LLM to improve NE transcription — [EDM 2026](https://educationaldatamining.org/edm2026/proceedings/2026.EDM.short-papers.112/index.html)
- RECOVER (Mar 2026, under review Interspeech 2026): agentic correction using multiple ASR hypotheses + entity retrieval + constrained LLM edits; 8-46% relative reduction in entity-phrase WER across five datasets, entity recall up to +22 points, with overall WER maintained; LLM-Select (LLM chooses among hypotheses) best — [arXiv 2603.16411](https://arxiv.org/abs/2603.16411)
- RASTAR (Feb 2026): NER → top-k retrieval from an NE repository → reasoning-based selection among candidates — [arXiv 2602.12287](https://arxiv.org/html/2602.12287v1)
- Error-aware TF-IDF RAG (Jun 2026): retriever weights documents containing **historically observed misrecognitions**; on Persian FLEURS, WER 23.06% → 18.83% — [arXiv 2606.24915](https://arxiv.org/abs/2606.24915) (abstract only; LLM not named on abstract page)

### Inferences
- The project's current design (zero-shot, whole-talk, rewrite-everything, 8B/70B quantized via Ollama, 1-best Whisper input) matches nearly every "hurts" condition in the literature. The 40-60% pass rate at a 90% similarity gate is consistent with the documented overcorrection/hallucination behaviour of small instruct models on long input.
- For English lecture-style audio from Whisper turbo/large-v3, the baseline WER is likely already low on common words, so the realistic win from LLM correction is concentrated in domain terms (Japanese/Sanskrit/Pali words, teacher and sutra names) — exactly the entity-correction setting where retrieval + phonetic candidates is the recent best practice.
- If LLM correction is used broadly, the literature favours fine-tuning (LoRA on an 8B model is feasible on a rented H100) on gold pairs over zero-shot prompting; but that requires a gold set (see Q5), which is needed anyway.

### Gaps
- No published GER results specific to long-form English religious/lecture monologue or to Buddhist terminology were found.
- No head-to-head of Llama 3.1 70B zero-shot vs. fine-tuned 8B on Whisper long-form English found.
- The 2025-2026 survey "Non-Intrusive ASR Refinement" ([arXiv 2508.07285](https://arxiv.org/pdf/2508.07285)) could not be parsed (PDF decode failed); its taxonomy and conclusions are not included.

---

## Q2. Constrained correction techniques (chunking, edit-only output, glossary restriction, phonetic matching, multi-hypothesis combination)

### Takeaway
Every constraining mechanism in the literature reduces hallucination: edit-list (JSON substitution) outputs, short segment-level inputs, confidence/uncertainty markers that steer edits to doubtful words, rule-based acceptance checks, and candidate lists retrieved by phonetic similarity. Simple multi-system voting (ROVER) is a strong, stable baseline that an LLM must beat.

### Cited Findings
**Edit-only / diff-style outputs**
- Full-text Chinese ASR correction (GLM-4-9B, LoRA): at **article level**, asking for JSON error-correction pairs beat direct rewrite (error rate 12.61 baseline → 9.97 direct vs **8.41 JSON** on one set; on the hard set direct rewrite made things **worse**, 25.24 → 27.89, while JSON improved to 22.36). Authors attribute direct-output failure to "hallucinations for lengthy output". At **segment level**, direct rewrite was slightly better than JSON (8.38 vs 9.33) — [arXiv 2409.07790](https://arxiv.org/html/2409.07790v2)
- A medical-ASR study used a JSON object with a "mismatches" list (incorrect text → correct form) as the output schema — [arXiv 2501.15310](https://arxiv.org/pdf/2501.15310) (via search summary)
- Google work fine-tuned LLMs to emit compact phrasal-rewrite edit representations rather than full rewrites, measured by WER after expanding edits — [arXiv 2501.13831](https://arxiv.org/pdf/2501.13831) (via search summary)
- NLE (2026) frames LLM-based ASR as non-autoregressive transcript *editing* — [arXiv 2603.08397](https://arxiv.org/pdf/2603.08397) (title-level only; not read)

**Rule-based and verification constraints**
- Removing rule-based constraints caused the largest drop in a heuristic correction framework (CER/WER 2.89/5.23 → 6.62/9.27) — [arXiv 2509.15095](https://arxiv.org/html/2509.15095v1) (via search summary)
- Pre-detection + iterative correction + answer verification took CER from 53.10 (unconstrained) to 4.69 — [arXiv 2505.24347](https://arxiv.org/pdf/2505.24347) (via search summary)

**Confidence-guided editing**
- Word-level confidence (entropy-based, aggregated from frames) written in brackets next to each word in the prompt; Llama 3.1 8B Instruct + LoRA (rank 16, ~130k pairs). On unseen TORGO: naive correction 20.01% → confidence-guided 10.58% (baseline 10.83%); harmful edits kept to ~1-5% on high-confidence utterances — [arXiv 2509.25048](https://arxiv.org/html/2509.25048)
- whisper-timestamped produces word-level timestamps and **confidence scores** from Whisper cross-attention/DTW — [whisper-timestamped (project page, non-primary)](https://www.sourcepulse.org/projects/1850103)

**Phonetic matching against a term list**
- Twiefel et al. (AAAI 2014) post-processed cloud ASR output by converting both the domain command list and ASR results with phonetic indexing (Soundex/Metaphone) and matching — [Twiefel et al. 2014](https://www.informatik.uni-hamburg.de/wtm/ps/Twiefel_AAAI2014_CR.pdf) [older]
- Double Metaphone yields primary and secondary codes; matching can be strict (primary=primary), normal (primary of one matches either of the other) or weak; spaces break comparison so multi-word terms must be normalized — [Alteryx docs (non-primary, vendor)](https://help.alteryx.com/dataprep/en/trifacta-application/wrangle-language/string-functions/doublemetaphoneequals-function.html)
- Recent NE-correction papers all use phonetic similarity for candidate retrieval (DeRAGEC, EMNLP 2025 generative annotation, EDM 2026) — see Q1 sources: [DeRAGEC](https://aclanthology.org/2025.findings-acl.786.pdf), [EDM 2026](https://educationaldatamining.org/edm2026/proceedings/2026.EDM.short-papers.112/index.html)

**Multi-hypothesis / multi-system combination**
- ROVER (NIST) aligns multiple ASR outputs into a word transition network and picks words by (weighted) voting — [NIST ROVER doc](https://people.csail.mit.edu/joe/sctk-1.2/doc/rover/rover.htm) [older]
- ROVER depends on the choice of "skeleton" hypothesis and ordering; quality-estimation ranking before fusion gave 0.5-7.3 absolute WER improvement over standard ROVER — [Jalalvand et al. 2017, arXiv 1706.07238](https://arxiv.org/pdf/1706.07238) [older]
- 2024 study combining Transducer and Whisper small.en N-best lists then LLM correction reached 4.72% WER, ~32%/36% below the respective baselines — [arXiv 2409.09554](https://arxiv.org/pdf/2409.09554)
- RECOVER (2026) compares 1-best, entity-aware select, ROVER and LLM-Select as fusion strategies; LLM-Select best for entities while preserving WER — [arXiv 2603.16411](https://arxiv.org/abs/2603.16411)
- Practitioner: 5-best ROVER (14.8) nearly matched Gemini (14.6) and beat all small local LLMs — [Alpha Cephei (non-primary)](https://alphacephei.com/nsh/2025/03/15/generative-error-correction.html)

**Biasing at ASR time (the "get it right from the start" lever)**
- Whisper struggles with rare words such as proper nouns and domain terms; prompting is a known mitigation — [arXiv 2502.11572](https://arxiv.org/html/2502.11572v2)
- Whisper prompt is limited to ~224 tokens; sources disagree whether overflow is truncated (last 224 kept) or errors — [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1378209/how-to-leverage-whisper-model-to-do-prompt) (non-primary); [openai/whisper discussion #1824](https://github.com/openai/whisper/discussions/1824)
- Prompt is a soft bias, not an instruction; helps rare/jargon terms more than phonetically confusable speech — [okmiku blog (non-primary)](https://okmiku.com/blog/whisper-prompt-parameter-actually-does)

### Inferences
- A safe design for this project: (1) keep Whisper segments with timestamps as the unit of work; (2) ask the LLM (or a deterministic matcher) for a **JSON list of substitutions** `{segment_id, original_span, replacement, reason}`; (3) apply only edits where `original_span` exists verbatim in the segment, the replacement is a glossary term (or a casing/spelling variant), and the phonetic distance between span and replacement is under a threshold; (4) reject any segment-level change exceeding a small edit-distance budget. This turns the 90%-similarity gate from a post-hoc filter into a structural guarantee and makes edits auditable/diffable.
- The JSON-vs-direct result suggests chunk size matters: edit lists are most valuable for long inputs; for short segments direct rewrite may be fine *if* followed by alignment-based edit filtering.
- Per-talk metadata (title, speaker, date) + top-N glossary terms can go into Whisper's prompt per talk (within ~224 tokens) to bias at the source, then the same glossary drives the phonetic post-matcher.
- Multi-system ROVER (e.g., Whisper large-v3 + turbo + a non-Whisper model such as Parakeet/Canary) is a cheap, LLM-free baseline worth measuring before investing in LLM fusion.

### Gaps
- No published benchmark found comparing Double Metaphone vs phoneme-based (G2P + phone edit distance) matching for ASR term correction; Double Metaphone is English-centric and may mis-encode romanized Japanese/Sanskrit — untested.
- RECOVER's exact constraint mechanism was not visible on the abstract page.
- No public tool was found that implements ROVER directly over Whisper JSON outputs (NIST SCTK `rover` exists but requires CTM input; not verified for 2026 tooling).
- Authoritative OpenAI documentation of Whisper prompt truncation behaviour not located.

---

## Q3. Separating concerns: punctuation/casing/segmentation models and paragraphing from timestamps

### Takeaway
Punctuation, casing and sentence segmentation can be done by small dedicated token-classification models that **cannot change words**, and paragraphing can be done from Whisper timestamps (pause length) plus semantic similarity — removing the main reason to give an LLM rewrite authority over the whole text. However, Whisper already emits punctuation/casing, so a dedicated model is mainly useful when normalizing multiple ASR sources or when Whisper punctuation is poor.

### Cited Findings
- NeMo `punctuation_en_distilbert`: DistilBERT with two token-classification heads (punctuation + capitalization), supports comma, period, question mark only; input lowercased, unpunctuated English; 512-token cap — [NVIDIA NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/punctuation_en_distilbert) [older]
- `1-800-BAD-CODE/punctuation_fullstop_truecase_english` (Apache-2.0, ONNX): 6-layer, 512-dim transformer doing punctuation + true-casing + sentence-boundary detection in one pass; 256-subtoken window (the `punctuators` package handles longer text via overlapping windows). Reported F1: period 91.80, comma 78.15, question 75.56; true-casing UPPER 93.76; sentence boundary 92.49. Trained on WMT News Crawl; card warns it may perform poorly on conversational text — [Hugging Face model card](https://huggingface.co/1-800-BAD-CODE/punctuation_fullstop_truecase_english)
- `oliverguhr/fullstop-punctuation-multilang-large` (used via the `deepmultilingualpunctuation` package): punctuation only (EN/IT/FR/DE), 559M params, MIT — [Hugging Face](https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large/blob/refs%2Fpr%2F9/README.md)
- Pause-based paragraphing: patents describe starting a new paragraph at speaker changes and long pauses (example threshold ~3 s), then splitting over-long paragraphs (e.g., >50-100 words) at sentence boundaries using sentence-similarity and dynamic programming — [US patent 12299401 (Transcript paragraph segmentation)](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12299401); [US patent 12300243](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12300243)
- Older topic-segmentation research found pause duration an "excellent criterion" for chopping speech, comparable to or better than sentence boundaries — [Integrating Prosodic and Lexical Cues, arXiv cs/0105037](https://arxiv.org/pdf/cs/0105037) [older]
- Deepgram's paragraph feature uses silence duration plus linguistic markers — [tutorial page (non-primary)](https://theneuralbase.com/deepgram/learn/beginner/paragraphs-paragraph-segmentation/)
- Plain Whisper timestamps are utterance-level and can be off by several seconds; WhisperX adds wav2vec2 forced alignment for word-level timing; stable-ts improves timestamps and can align existing (corrected) text to audio at word level — [WhisperX README](https://github.com/jebdu/whisperX/blob/main/README.md); [stable-ts on PyPI](https://pypi.org/project/stable-ts/2.15.2/)
- LibriSpeech-PC benchmark defines punctuation error rate (PER) for evaluating end-to-end ASR punctuation/capitalization — [arXiv 2310.02943](https://arxiv.org/abs/2310.02943)

### Inferences
- Recommended split for this project: Whisper (words + its punctuation) → optional dedicated punctuation/casing model only if gold-set PER shows Whisper is weak → paragraphing from word timestamps (pause threshold tuned on gold set, plus a max-length rule) → LLM restricted to glossary-term substitutions. The `transcript_structured` stage could then be produced deterministically and would trivially pass the similarity gate.
- Because the 1-800-BAD-CODE and NeMo models expect lowercased unpunctuated input and are news-trained, they may not beat Whisper's native punctuation on dharma talks; this should be measured, not assumed.

### Gaps
- No published paragraph-segmentation model trained specifically on lecture/sermon transcripts was found; no benchmark comparing pause-based vs LLM paragraphing for monologues.
- No 2025-2026 comparison of Whisper-native punctuation vs dedicated punctuation models on long-form English was found.

---

## Q4. Building a domain glossary semi-automatically

### Takeaway
Use three sources: (1) curated Buddhist reference glossaries, (2) talk metadata (titles, speakers) and (3) mined misrecognitions from the existing 6,500 raw transcripts (and from gold-set alignments). Recent RAG-correction work explicitly benefits from a table of *historically observed* misrecognitions, which this project can build cheaply.

### Cited Findings
- Digital Dictionary of Buddhism (Univ. of Tokyo; terms, texts, schools, temples, persons); listed as open access but full use is restricted by contribution level — [NIHU resource guide](https://guides2.nihu.jp/index.php/resources/431)
- Sotozen-Net glossary: free online Soto Zen glossary, alphabetical by English translation — [NIHU resource guide](https://guides2.nihu.jp/index.php/resources/432)
- Inagaki, *A Glossary of Zen Terms*: ~5,500 entries on Zen terms, persons, texts, idioms, general Buddhist terms (print) — [Stone Bridge catalog / search snippet](https://stonebridge.com/catalog/a-glossary-of-zen-terms)
- *Dictionary of Japanese Buddhist Terms* (Inagaki/O'Neill; Sanskrit equivalents supplied) and Zvelebil *Dictionary of Zen Buddhist Terminology* (Pali/Sanskrit/Chinese) are print/e-book resources — [NTU Buddhism library](https://buddhism.lib.ntu.edu.tw/en/search/search_detail.jsp?seq=146517); [palmknihy](https://www.palmknihy.cz/kniha/736)
- Error-aware retrieval: a penalty matrix built from historical errors raised error-aware retrieval hit rate from 53.7% to 90.9% and reduced WER 23.06% → 18.83% — [arXiv 2606.24915](https://arxiv.org/abs/2606.24915)
- Prompting Whisper with a domain glossary is a common practice for rare terms (see Q2) — [arXiv 2502.11572](https://arxiv.org/html/2502.11572v2)

### Inferences
- Mining procedure (not from a single source; synthesized): (a) tokenize all titles/metadata and extract capitalized/non-English tokens (e.g., "Dogen", "Shobogenzo", "sesshin") as seed terms; (b) for each seed term, compute phonetic codes and search raw transcripts for n-grams that match phonetically but not orthographically — these are candidate misrecognitions (e.g., "the gen" → "Dogen"); (c) rank by frequency and have a human accept/reject; (d) store accepted pairs as `misrecognition → canonical term` with context examples. This produces both the Whisper prompt list and the post-correction candidate table.
- Gold-set alignments (reference vs Whisper) yield the highest-precision misrecognition pairs; existing LLM-cleaned outputs that passed the gate can also be diffed against raw text to harvest corrections the LLM made, but these need human verification since the LLM may have been wrong.
- Spelling conventions (macrons/diacritics, e.g., "Dōgen" vs "Dogen"; "Shobogenzo" vs "Shōbōgenzō") must be decided once in the glossary; evaluation normalization should then fold diacritics so convention differences are not counted as ASR errors (Whisper's normalizer strips diacritics — see Q5).

### Gaps
- No freely downloadable, machine-readable Zen/Japanese-English term list was confirmed; DDB download/licence terms not verified.
- No paper was found that specifically evaluates semi-automatic glossary mining from ASR transcripts for religious or Buddhist content.

---

## Q5. Evaluation: gold set design, metrics and tools

### Takeaway
Build a hand-corrected gold set sampled across eras, speakers and audio quality; score with normalized WER/CER (Whisper `EnglishTextNormalizer` + jiwer), **plus** a term-focused metric (B-WER/U-WER or entity recall against the glossary), punctuation error rate, and a non-speech hallucination check; use cpWER/WDER only if multi-speaker Q&A attribution matters. Use blockwise (per-talk) bootstrap for confidence intervals — the number of independent talks matters more than total minutes.

### Cited Findings
**Statistical design**
- Utterance-level bootstrap CIs are too optimistic because errors within a speaker/recording are correlated; blockwise bootstrap (resample blocks such as speakers) gives a consistent variance estimator for the WER difference between two systems — [Liu et al., Statistical Testing on ASR Performance via Blockwise Bootstrap, arXiv 1912.09508](https://arxiv.org/pdf/1912.09508) [older]
- Older bootstrap work: with ~7,400-8,300 words per test set, the 90% CI on WER was roughly ±1 point, and sentence-level independence assumptions give untrustworthy (too narrow) intervals — [Bisani & Ney, Bootstrap estimates for confidence intervals in ASR](https://typeset.io/pdf/bootstrap-estimates-for-confidence-intervals-in-asr-4a0uu8tnh9.pdf) [older]

**Normalization and WER/CER**
- Whisper `EnglishTextNormalizer`: lowercases; removes bracketed/parenthesized text; removes fillers (hmm, mm, mhm, mmm, uh, um); expands contractions and titles (won't → will not, mr → mister); removes digit commas; strips periods not before numbers; strips symbols and **diacritics**; converts spelled numbers to digits; maps British → American spelling; collapses whitespace — [openai/whisper normalizers/english.py](https://github.com/openai/whisper/blob/main/whisper/normalizers/english.py)
- jiwer computes WER, MER, WIL, WIP and CER via minimum edit distance (RapidFuzz); v4.0 defined behavior for empty references — [jitsi/jiwer](https://github.com/jitsi/jiwer)
- NeMo `examples/asr/speech_to_text_eval.py`: can score an existing manifest (`only_score_manifest=True`, needs `text` and `pred_text`), per-sample WER/CER (`scores_per_sample`), `use_cer`, text processing (`punctuation_marks` default ".,?", `separate_punctuation`, `do_lowercase`, `rm_punctuation`), and `use_punct_er` for dataset-level punctuation error rate — [NeMo source](https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/asr/speech_to_text_eval.py)

**Term/entity-focused metrics**
- Contextual-biasing papers report WER, U-WER (words not in bias list) and B-WER (words in bias list); an insertion counts toward B-WER if the inserted word is in the bias list, else U-WER; goal is lower B-WER without raising U-WER — [arXiv 2401.08835](https://arxiv.org/pdf/2401.08835); [Le et al. 2021, arXiv 2104.02194](https://arxiv.org/pdf/2104.02194.pdf) [older]
- Entity-phrase WER (E-WER) and entity recall are used for NE correction evaluation — [RECOVER, arXiv 2603.16411](https://arxiv.org/abs/2603.16411)
- Interspeech 2025 paper argues low WER does not necessarily mean output is good for LLM-powered pipelines and proposes an alternative metric — [Pulikodan et al., Interspeech 2025](https://www.isca-archive.org/interspeech_2025/pulikodan25_interspeech.pdf) (via search summary; details not read)

**Punctuation**
- PER = (I_P + D_P + S_P) / (I_P + D_P + S_P + C_P) over punctuation tokens only, using Levenshtein alignment; proposed because WER/CER/F1 don't distinguish word, punctuation and capitalization errors — [LibriSpeech-PC, arXiv 2310.02943](https://arxiv.org/abs/2310.02943)

**Hallucination**
- Calm-Whisper defines non-speech hallucination rate as the share of non-speech clips producing a non-empty transcript; Whisper large-v3 ~100% vs Conformer-CTC 13.52% on their set; fine-tuning a few attention heads cut it >80% with <0.1% WER degradation on LibriSpeech — [arXiv 2505.12969](https://arxiv.org/pdf/2505.12969)
- 40.3% of non-speech inputs caused Whisper hallucinations; rate rises for clips >30 s; lowest at beam size 1; proposes a "Bag of Hallucinations" filter of known phrases — [Barański et al., arXiv 2501.11378](https://arxiv.org/pdf/2501.11378)
- Hallucination region often defined with Whisper's default thresholds (avg_logprob −1.0, no_speech_prob 0.6) — [arXiv 2606.07473](https://arxiv.org/pdf/2606.07473)

**Speaker attribution (if Q&A/multi-speaker matters)**
- MeetEval supports WER, cpWER, ORC-WER, MIMO-WER and time-constrained variants (tcpWER, tcORC-WER), DI-cpWER and DER; formats STM, CTM, SegLST (JSON), RTTM (DER only); HTML alignment visualizer (`meeteval-viz html`); `pip install meeteval` — [fgnt/meeteval](https://github.com/fgnt/meeteval)
- WDER = (S_IS + C_IS)/(S + C): share of substituted+correct words with the wrong speaker label; excludes insertions/deletions so must be reported with WER — [Shafey et al. 2019, arXiv 1907.05337](https://arxiv.org/pdf/1907.05337) [older]
- WER definitions for multi-speaker systems (cpWER, ORC, MIMO) and efficient computation — [von Neumann et al., arXiv 2211.16112](https://arxiv.org/pdf/2211.16112)

### Inferences
- Gold-set sizing (synthesized, not from a source): because blocks (talks/speakers) drive variance, prefer many short excerpts from many talks over a few full talks — e.g., 30-50 talks × 5-10 min excerpts (≈3-6 audio hours, ≈25-50k words at typical lecture speaking rates) stratified by decade/era, recording equipment/quality tier, speaker, and presence of Q&A/chanting/bells. Include 1-2 full talks to evaluate paragraphing and long-form drift. This is comfortably above the ~8k-word scale where older work saw ~±1-point CIs, while giving enough talk-level blocks for a meaningful blockwise bootstrap. Add a small set of non-speech segments (bells, chanting, silence, room noise) for hallucination rate.
- Metric stack per system: (1) normalized WER/CER via Whisper normalizer + jiwer, with a custom pre-step folding diacritics/glossary spelling variants; (2) B-WER/U-WER using the glossary as the bias list (shows whether biasing/correction helps terms without harming other words); (3) PER (NeMo `use_punct_er` or own implementation) and paragraph-boundary F1 against gold paragraph breaks; (4) non-speech hallucination rate + long insertion runs; (5) for LLM stages, "edit precision": fraction of LLM edits that move text closer to gold (reference-aligned), which directly measures overcorrection.
- Note the normalizer removes fillers and bracketed text, which is desirable for a "clean read" gold standard; the gold-set transcription guidelines must specify verbatim vs. clean (fillers, false starts, repetitions) so references match the normalization.
- Keep audio-quality strata explicit, because both literature (Whisper vs CTC robustness) and the Alpha Cephei experience suggest correction value varies strongly with baseline error.

### Gaps
- No source found giving a recommended minimum hours/words for domain ASR comparison; the sizing above is an inference.
- jiwer's built-in transformation API was not confirmed on the fetched README page (the summarizer reported no transformations listed); verify against current jiwer docs before relying on it.
- No off-the-shelf B-WER implementation was located (it is typically computed with custom code on top of an alignment); pyannote.metrics was not researched in this pass.
- The alternative metric proposed in the Interspeech 2025 "LLM-powered pipelines" paper was not read in full.

---

## Q6. Practical: human correction tools and gold-set effort

### Takeaway
Correcting from an ASR draft is much cheaper than transcribing from scratch (roughly half), and effort scales with ASR error rate; the useful tooling is a word-timestamped editor with click-to-play audio, plus a forced aligner to re-time corrected text. Dedicated open-source proofreading UIs were not well covered by sources found.

### Cited Findings
- Experienced transcribers need ~5× audio duration to transcribe from scratch; starting from ASR drafts can roughly halve the time while keeping quality; less conscientious editors may miss errors — [Aigent / Medium (non-primary, practitioner)](https://medium.com/aigent/using-automated-speech-recognition-to-support-human-transcriptions-39c6b0ae7b76)
- Icelandic Parliament post-editing study: edit time directly correlated with transcription accuracy (real-time factor = edit time / audio duration), though the RTF-WER relationship was weak — [arXiv 1807.11893](https://arxiv.org/pdf/1807.11893) [older]
- Common Voice low-resource study: post-editing very bad ASR output took most of the time — [arXiv 2105.04674](https://arxiv.org/pdf/2105.04674) [older]
- Aggregator figure (unverified): ~1.32-1.36 s/word for manual transcription, >1.7 s/word for high-error segments — [Emergent Mind (non-primary)](https://www.emergentmind.com/topics/real-time-transcription-error-rates)
- aeneas: Python/C forced-alignment library (AGPL), any ffmpeg-readable audio; confused by long silences, noise, multiple speakers and inaccurate transcripts — [aeneas mirror](https://www.sourceforge.net/mirror/aeneas); [Sacha Chua, subed.el (non-primary)](https://sachachua.com/blog/2024/12/subed-el-tweaking-subtitle-times/)
- subed.el (Emacs) can re-time a selected subtitle region with aeneas, enabling local fixes without re-aligning the whole file — [Sacha Chua blog (non-primary)](https://sachachua.com/blog/2024/12/subed-el-tweaking-subtitle-times/)
- Subaligner: DNN + forced-alignment subtitle sync tool — [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fbaxtree%2Fsubaligner)
- stable-ts can align plain (corrected) text to audio at word level and export SRT/VTT/ASS/TSV — [stable-ts PyPI](https://pypi.org/project/stable-ts/2.15.2/)
- MeetEval's HTML alignment visualizer allows side-by-side inspection of reference vs multiple hypotheses — [fgnt/meeteval](https://github.com/fgnt/meeteval)

### Inferences
- Practical workflow: export Whisper (or WhisperX) output as SRT/VTT per excerpt → correct in a subtitle editor with waveform + click-to-play (e.g., Subtitle Edit, Aegisub, subed.el) using written guidelines (glossary spellings, verbatim vs clean, paragraph marks) → re-align with stable-ts/aeneas if timings are needed → export plain text reference. Use word confidence (whisper-timestamped) to highlight words to check first.
- Effort estimate (inference from the ~5× scratch and ~halving figures): ~2-3 hours of human time per audio hour for a careful single pass on decent audio, more for poor recordings; a 3-6 hour gold set is therefore roughly 1-3 person-weeks part-time including a second-pass review on a subset to measure inter-annotator agreement. Domain expertise (a practitioner familiar with the terminology) matters more than transcription speed for this corpus.
- Budget a second independent pass on ~10-20% of the gold set to estimate human disagreement; ASR differences smaller than that disagreement are not meaningful.

### Gaps
- No primary source found on oTranscribe or Label Studio for transcript correction (search returned nothing on oTranscribe); their 2026 status/features unverified.
- No published per-hour correction cost for long-form lecture monologue with domain terminology was found; the estimate above is an inference.
