# Speaker Diarization Options for Dharma Talks (state as of Nov 2026)

Scope: open-source and hosted "who spoke when" tools, plus speaker identification across files, for about 6,500 mostly-monologue English dharma talks (about 5,000–8,000 h). Research date: 2026-11-08. All DER figures are as reported by the cited source. **Vendor-run benchmarks are flagged [VENDOR].** DER is not comparable across sources that use different collars, overlap handling, or reference labels.

---

## 1. pyannote.audio: speaker-diarization-3.1 vs. community-1 (4.x) vs. pyannoteAI Precision-2/3

### Takeaway
community-1 (pyannote.audio 4.0, Sep 2025) is the current open-weight pyannote pipeline. It is modestly better than 3.1 on most benchmarks, is CC-BY-4.0, needs a click-through acceptance on Hugging Face, and is what WhisperX now uses. pyannoteAI's hosted Precision-2, and now Precision-3 (Sep 2026), are clearly more accurate, but those figures come from the vendor. The main known problem on long files is a reported VRAM increase in 4.x, roughly 9.5 GB on a 72-minute file, which matters for the 8 GB RTX 3070 Ti.

### Cited Findings
- **community-1 license and gating:** CC-BY-4.0. The repo is gated: you must accept the conditions and share your contact info on Hugging Face, and you agree to receive occasional emails from pyannote. — [HF model card: community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
- **community-1 compatibility:** "Compatible with pyannote.audio 4.x." pyannote.audio 4.0 launched with community-1 on Sep 29, 2025 and requires Python 3.10+. — [HF model card](https://huggingface.co/pyannote/speaker-diarization-community-1); [pyannoteAI changelog](https://www.pyannote.ai/changelog)
- **DER table [VENDOR]** (pyannote's own benchmark; no collar, overlap scored, fully automatic; updated 2025-09), as 3.1 / community-1 / precision-2:
  - AISHELL-4: 12.2 / 11.7 / 11.4
  - AliMeeting ch1: 24.5 / 20.3 / 15.2
  - AMI IHM: 18.8 / 17.0 / 12.9
  - AMI SDM: 22.7 / 19.9 / 15.6
  - AVA-AVD: 49.7 / 44.6 / 37.1
  - CALLHOME pt2: 28.5 / 26.7 / 16.6
  - DIHARD 3 full: 21.4 / 20.2 / 14.7
  - Ego4D dev: 51.2 / 46.8 / 39.0
  - MSDWild: 25.4 / 22.8 / 17.3
  - RAMC: 22.2 / 20.8 / 10.5
  - REPERE ph2: 7.9 / 8.9 / 7.4 (community-1 is *worse* than 3.1 here)
  - VoxConverse v0.3: 11.2 / 11.2 / 8.5 (community-1 ties 3.1)
  - Source: [HF model card](https://huggingface.co/pyannote/speaker-diarization-community-1)
- **What changed in community-1:** better speaker assignment (fewer confusion errors) and better speaker counting. Segmentation (VAD and overlap detection) is described as **the same as 3.1**. No GPU inference timings are published. The "15x speed-up" claim refers to training. — [pyannoteAI blog: community-1](https://www.pyannote.ai/blog/community-1)
- **Exclusive diarization:** community-1 adds `exclusive_speaker_diarization`, which allows only one active speaker at a time. It was backported from precision-2 to simplify aligning STT word timestamps with speaker labels. — [HF model card](https://huggingface.co/pyannote/speaker-diarization-community-1); [community-1 blog](https://www.pyannote.ai/blog/community-1)
- **CPU by default:** pipelines run on CPU unless you call `pipeline.to(torch.device("cuda"))`. Input is downmixed to mono and resampled to 16 kHz. No maximum speaker count; `num_speakers`, `min_speakers` and `max_speakers` are optional hints. — [HF model card](https://huggingface.co/pyannote/speaker-diarization-community-1)
- **Precision-2 [VENDOR]:** launched Sep 2, 2025. Claimed +14% accuracy vs Precision-1 and +28% vs OSS 3.1, and correct speaker count on 70% of the hardest benchmark (up from 50%). — [pyannoteAI changelog](https://www.pyannote.ai/changelog)
- **Precision-3 [VENDOR]:** launched Sep 17, 2026 on the API and on-prem. Average DER drops from 16.02 to 14.35 across 15 datasets (−10.4% vs Precision-2), with 18.7% fewer wrong-speaker assignments. Adds `vadSensitivity` and `crosstalkSensitivity` parameters plus output scores. Pricing is unchanged from Precision-2. — [pyannoteAI changelog](https://www.pyannote.ai/changelog)
- **Independent benchmark (arXiv 2509.26177, also listed at ICML 2026):** pyannoteAI precision-2 had the best overall DER at 11.2%, with DiariZen next at 13.3%. Setup: 0.25 s collar, overlap not skipped, A6000 GPUs. pyannoteAI led on English at 6.6% DER. — [Benchmarking Diarization Models, arXiv](https://arxiv.org/html/2509.26177v1); [ICML listing](https://icml.cc/virtual/2026/77326)
- **Speed (independent):** pyannote 3.1 averaged about 45x faster than real time on an RTX A6000, against about 20x for DiariZen and about 210x for Sortformer v2. — [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1)
- **Another third-party DIHARD III figure:** Gladia reports pyannoteAI at 23% DER on DIHARD III. Gladia is a competitor and ran the test itself. — via search summary of [Gladia](https://www.gladia.io/product/audio-intelligence/speaker-diarization) (not fetched directly)
- **Known issue, VRAM on long files:** GitHub issue #1963 reports that pyannote.audio 4.0.3 used about 9.54 GB VRAM on a 72-minute file, for both community-1 and 3.1. pyannote 3.3.2 with 3.1 used 1.59 GB, so this is about 6x more. The embedding step appears to be the main cost. No fix was found in these results. — [pyannote-audio issue #1963 (mirror)](https://github-users.yhajoa.workers.dev/pyannote/pyannote-audio/issues/1963)
- **Other long-file and speed issues:** a crash on audio over 8 hours on an RTX 4090 ([discussion #1562](https://www.github.com/pyannote/pyannote-audio/discussions/1562)). Slowness from low GPU utilization, with embedding extraction as the bottleneck ([#1652](https://github.com/pyannote/pyannote-audio/issues/1652), [#1687](https://www.github.com/pyannote/pyannote-audio/issues/1687)). Community workaround: chunk with overlap and clear the GPU cache between chunks. — [bearblog write-up](https://askthegame.bearblog.dev/i-had-to-build-a-memory-efficient-speaker-diarization-for-large-podcast-episodes/)
- **pyannoteAI hosted pricing:** Developer plan €19/month for up to 125 h of premium processing (Precision-2 and Community-1); Starter €99/month for up to 825 h; Enterprise is custom, with self-hosting available. Prices date from Oct 6, 2025. Hosted community-1 is described as "available at cost". — [changelog](https://www.pyannote.ai/changelog); [community-1 blog](https://www.pyannote.ai/blog/community-1)
- **pyannoteAI STT orchestration:** launched Dec 11, 2025. One API call returns aligned diarization and transcription. Supports Precision-2 with NeMo Parakeet; Whisper large-v3-turbo was added on Jan 15, 2026. — [changelog](https://www.pyannote.ai/changelog)
- **Streaming:** a beta launched May 4, 2026 (up to 8 speakers). Live-1 reached GA on Jul 7, 2026 at about €0.17–0.198/h. Not relevant for batch archives. — [changelog](https://www.pyannote.ai/changelog)

### Inferences
- With an 8 GB 3070 Ti, community-1 on 60–90 minute talks may run out of memory if the #1963 regression applies. Options are pinning pyannote.audio 3.3.x with 3.1, chunking the audio, or running on the rented H100/GH200, where VRAM is not a concern.
- At about 45x real time (the 3.1 figure on an A6000; community-1 should be similar but was not measured), about 7,000 h of audio needs roughly 155 GPU-hours. That is cheap on rented hardware but slow on one 3070 Ti.
- Precision-3's −10% DER claim is vendor-reported and unverified independently. Precision-2's lead was confirmed by one independent paper.
- For 7,000 h, the Starter plan's 825 h/month would take about 9 months unless Enterprise or overage pricing is negotiated (overage terms not found).

### Gaps
- No published GPU real-time factor for community-1, and none for 3.1 on an 8 GB consumer GPU.
- Whether #1963 was fixed in a later 4.0.x or 4.1 release could not be confirmed.
- Precision-3 per-dataset numbers were not retrieved; only the 15-dataset average is in the changelog.
- pyannoteAI overage pricing and any batch or bulk discounts were not found.

---

## 2. NVIDIA NeMo: Sortformer (v1, streaming v2/v2.1), Nemotron-3-Diarization, MSDD and clustering

### Takeaway
NVIDIA's end-to-end Sortformer line is now very fast and permissively licensed. The newest model, **Nemotron-3-Diarization** (Sep 23, 2026; 8 speakers; ~100M params; OpenMDW license, commercial use allowed), reports large DER gains over Streaming Sortformer v2.1 and runs at over 1,000x real time in offline mode. These models cap the number of speakers at 4 (Sortformer) or 8 (Nemotron). Dharma talks with a teacher and a few questioners usually stay within that, but large Q&A sessions might not. The cascaded clustering diarizer with MSDD has fewer speaker and length restrictions, but it is older.

### Cited Findings
- **Streaming Sortformer v2 (`nvidia/diar_streaming_sortformer_4spk-v2`):** FastConformer-Transformer, about 117M params. Uses an Arrival-Order Speaker Cache to track speakers on long audio. **Maximum 4 speakers**, and the card says performance degrades with 5 or more. Handles recordings "several hours long", but "performance may degrade on very long recordings". Trained primarily on English. CC-BY-4.0. — [HF model card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2)
- **v2 DER, with post-processing (0 s collar on DIHARD; 0.25 s on CALLHOME):**

  | Latency | RTF | DIHARD III ≤4spk | DIHARD III full | CALLHOME full |
  |---|---|---|---|---|
  | 30.4 s | 0.002 | 13.45 | 18.85 | 9.54 |
  | 1.04 s | 0.093 | 13.24 | 18.91 | 10.70 |

  RTF measured on an RTX 6000 Ada at batch size 1. — [HF model card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2)
- **Training data:** about 2,445 h of real conversations (Fisher, AMI, VoxConverse, ICSI, DIHARD III dev, DiPCo) plus about 5,150 h of simulated mixtures. — [HF model card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2)
- **Running Sortformer:** `SortformerEncLabelModel.from_pretrained(...)` then `.diarize(audio=...)` in NeMo (installed from GitHub main). There is also a Q8_0 GGUF of about 147 MB for NeMo-Speech.cpp, which can add speaker tags to transcripts. — [HF model card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2)
- **Nemotron-3-Diarization (`nvidia/nemotron-3-diarization`):** released Sep 23, 2026. 31-layer RoPE Transformer, about 100M params, **up to 8 speakers**. No fixed length limit with chunked inference. Uses the AOSC and FIFO speaker cache adapted from Streaming Sortformer. **OpenMDW License v1.1**, commercial and non-commercial use allowed. Linux and NVIDIA GPUs only. — [HF model card](https://huggingface.co/nvidia/nemotron-3-diarization)
- **Nemotron-3 DER [VENDOR, NVIDIA]** at 30.4 s latency, against Sortformer 4spk-v2.1 at the same latency:
  - DIHARD III: 12.73 vs 19.09
  - CALLHOME pt2: 9.10 vs 10.32
  - AMI SDM: 11.14 vs 21.42
  - AliMeeting Far: 10.47 vs 13.69
  - NOTSOFAR1 single-channel: 11.00 vs 30.49
  - Speaker-count accuracy on DIHARD III: 81.5% vs 75.3%
  - The card warns that forced-alignment reference labels change the results, and it gives **no comparison to pyannote or DiariZen**.
  - Source: [HF model card](https://huggingface.co/nvidia/nemotron-3-diarization)
- **Nemotron-3 speed:** RTFx of 1,340 eager and 4,385 compiled at batch size 1 in 30.4 s offline mode, and over 12,000 at batch size 32. Measured on a Blackwell RTX PRO 5000 in BF16. — [HF model card](https://huggingface.co/nvidia/nemotron-3-diarization)
- **Independent benchmark (arXiv 2509.26177):** tested `diar_sortformer_4spk-v1` and `diar_streaming_sortformer_4spk-v2`. **Sortformer v1 needed chunking for recordings over 12 minutes** because self-attention memory grows quadratically on the authors' A6000 hardware. Sortformer v2 was the fastest system, at RTFx of about 210, and stayed competitive with DiariZen when speaker counts were low. Sortformer models showed more speaker confusion than other systems, and their scores worsened as speaker counts grew. SF v2-stream had the best AliMeeting DER at 7.0%. — [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1)
- **Cascaded NeMo diarizer (VAD, speaker embeddings, clustering, then MSDD neural diarizer):** NeMo docs say cascaded systems have "less restriction on the number of speakers and session length" than end-to-end ones, but give no numbers. — [NeMo docs: speaker diarization intro](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html)
- **TitaNet-Large** (the embedding model used in NeMo's cascaded pipeline): about 23M params, EER 0.66% on VoxCeleb1 cleaned, CC-BY-4.0, English training data. Exposes `get_embedding()` and `verify_speakers()`. — [HF: speakerverification_en_titanet_large](https://huggingface.co/nvidia/speakerverification_en_titanet_large)

### Inferences
- For mostly-monologue talks with 1–4 speakers, Nemotron-3-Diarization or Sortformer v2 would process the whole archive in GPU-minutes to single-digit GPU-hours: about 7,000 h at more than 1,000x is under 7 h even uncompiled. Diarization compute is not the bottleneck.
- The 4- or 8-speaker cap is the main risk. A Q&A with many questioners will merge some of them, which is acceptable if the goal is "teacher vs. other". Arrival-order labels also make the first speaker the "speaker 0" track, often the introducer rather than the teacher, so labels still need embedding-based identification.
- Because Nemotron-3 is two months old and only vendor-benchmarked, treat its DER gains as provisional.

### Gaps
- No independent benchmark of Nemotron-3-Diarization was found, and no head-to-head with pyannote community-1 or DiariZen.
- The exact maximum audio length of the original `diar_sortformer_4spk-v1` (non-streaming) was not confirmed from the model card; only the paper's "chunk >12 min" note was found.
- The Sortformer v2.1 model card was not fetched (it is only referenced as Nemotron's baseline).
- The status of MSDD (deprecated or maintained) in current NeMo was not confirmed. The docs page gave no detail beyond the description.
- The Nemotron "ASR Integration Guide" was linked but not retrieved.

---

## 3. DiariZen (BUT), 3D-Speaker, WeSpeaker and other recent open models

### Takeaway
DiariZen (WavLM plus EEND, then clustering) is the strongest *fully open* local pipeline in independent testing, about 2 DER points behind pyannoteAI precision-2. **Its weights are CC BY-NC 4.0 (research and academic use only)**, which may or may not be a problem for a nonprofit archive; needs review. 3D-Speaker (Apache-2.0) and WeSpeaker (Apache-2.0) mainly matter as speaker-embedding sources for identifying the teacher. As whole diarizers they are weaker or less benchmarked.

### Cited Findings
- **DiariZen models:** Base-s80, Large-s80 and Large-s80-v2. Code is MIT; **pretrained weights are CC BY-NC 4.0**, "research and academic purposes" only, because of non-commercial training data. — [GitHub BUTSpeechFIT/DiariZen](https://github.com/BUTSpeechFIT/DiariZen)
- **DiariZen DER [self-reported by authors]** (no collar), pyannote 3.1 vs Large-s80-v2:
  - AMI-SDM: 22.4 vs 13.9
  - AISHELL-4: 12.2 vs 10.1
  - AliMeeting far: 24.4 vs 10.8
  - NOTSOFAR-1: no pyannote score vs 16.7
  - MSDWild: 25.3 vs 15.8
  - DIHARD3 full: 21.7 vs 14.5
  - RAMC: 22.2 vs 11.0
  - VoxConverse: 11.3 vs 9.1
  - Source: [DiariZen GitHub](https://github.com/BUTSpeechFIT/DiariZen)
- **DiariZen updates:** Large-s80-v2 benchmarks were added on 2025-12-09, and multi-channel WavLM support on 2026-01-31. — [DiariZen GitHub](https://github.com/BUTSpeechFIT/DiariZen)
- **DiariZen independent results:** 13.3% overall DER, second only to pyannoteAI. Best VoxConverse result at 5.2% (0.25 s collar). Slowest system tested at about 20x real time on an A6000. — [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1)
- **3D-Speaker (Alibaba/ModelScope):** Apache-2.0. Modular pipeline: optional overlap detection, VAD, segmentation, embeddings and clustering. DER: AISHELL-4 10.30, AliMeeting 19.73, AMI_SDM 21.76, VoxConverse 11.75. The same table lists pyannote at 11.3 on VoxConverse and **DiariZen_WavLM at 28.39**. That DiariZen figure contradicts DiariZen's own 9.1 and the independent 5.2, probably because of an older DiariZen version or different settings. — [GitHub modelscope/3D-Speaker](https://github.com/modelscope/3D-Speaker); contradicted by [DiariZen GitHub](https://github.com/BUTSpeechFIT/DiariZen) and [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1)
- **3D-Speaker embeddings (VoxCeleb1-O EER):** CAM++ 0.65% (7.2M params), ERes2NetV2 0.61%, ERes2Net-large 0.52%. Diarization recipes were last updated in 2024-12, so the project looks less active for diarization. — [3D-Speaker GitHub](https://github.com/modelscope/3D-Speaker)
- **WeSpeaker:** Apache-2.0 speaker-embedding toolkit with a CLI (`wespeaker --task embedding|similarity|diarization`). VoxCeleb1-O EER: 293-layer ResNet 0.447%, ResNet34 0.723%, ECAPA-TDNN-c1024 0.728%. Has a VoxConverse diarization recipe (UMAP plus HDBSCAN) but publishes no DER. Recent updates: w2v-BERT2 (2025-12), ReDimNet2 (2026-07), U³-xi uncertainty-aware embeddings (2026-09-22). — [GitHub wenet-e2e/wespeaker](https://github.com/wenet-e2e/wespeaker)
- **Note:** pyannote's own pipelines use a WeSpeaker ResNet34 embedding internally (from memory, not fetched); see Gaps.

### Inferences
- For a fully local, commercially safe pipeline, the realistic open choices are pyannote community-1 (CC-BY-4.0, gated) and NVIDIA Nemotron-3 or Sortformer (OpenMDW / CC-BY-4.0). DiariZen is more accurate than community-1 but has the NC weights caveat and is about 2x slower than pyannote.
- For identifying the teacher across talks, any of TitaNet-L, WeSpeaker ResNet, CAM++ or ERes2Net is accurate enough on clean speech (EER 0.4–0.7% on VoxCeleb). Cassette-era channel mismatch matters more than the choice of model.

### Gaps
- No independent speed numbers for 3D-Speaker or WeSpeaker diarization.
- I did not confirm from a primary source which embedding model community-1 uses internally.
- No new 2026 open diarizer besides Nemotron-3 was found in this pass. Others may exist (for example, newer DiariZen variants or EEND-TA models). The search was not exhaustive.

---

## 4. Integration with ASR output (WhisperX, NeMo, Parakeet and Canary timestamps)

### Takeaway
WhisperX now uses pyannote **community-1** for diarization and assigns speakers to words with `assign_word_speakers`. It is the simplest drop-in for the existing Whisper pipeline, but word-level speaker assignment stays imperfect around overlaps and for unalignable tokens such as numbers. The NVIDIA route pairs Sortformer or Nemotron with Parakeet through NeMo or NeMo-Speech.cpp. pyannoteAI offers a hosted pipeline that aligns diarization with transcription, which it calls "STT orchestration".

### Cited Findings
- **WhisperX diarization:** uses pyannote `speaker-diarization-community-1` (CC-BY-4.0). Needs an HF read token (`--hf_token` or `token=`) and acceptance of the model's user agreement. API: `DiarizationPipeline(token=..., device=...)`, then `whisperx.assign_word_speakers(diarize_segments, result)`, with optional `min_speakers`/`max_speakers`. — [GitHub m-bain/whisperX](https://github.com/m-bain/whisperX)
- **WhisperX stated limitations:** "Diarization is far from perfect." Improving word-level diarization is "harder than first thought." Overlapping speech is "not handled particularly well by whisper nor whisperx." Tokens such as "2014." or "£13.60" can't be aligned and get no timestamps. Alignment needs a language-specific wav2vec2 model. — [WhisperX GitHub](https://github.com/m-bain/whisperX)
- **WhisperX memory:** under 8 GB for large-v2 with beam 5 on the faster-whisper backend; reduce batch size or use int8 when memory is short. Requires CUDA 12.8. — [WhisperX GitHub](https://github.com/m-bain/whisperX)
- **Exclusive diarization** (community-1 and precision-2+) is meant specifically to simplify mapping STT word timestamps to a single speaker. — [community-1 card](https://huggingface.co/pyannote/speaker-diarization-community-1)
- **NVIDIA integration:** NeMo-Speech.cpp can add word-level speaker tags to transcripts (`--diarize` / `--diar-model`) using Nemotron-3 or Sortformer GGUFs. Sortformer is also deployed in NVIDIA Riva ASR with diarization. NeMo docs mention tutorials that combine ASR transcripts with speaker labels. — [Nemotron-3 card](https://huggingface.co/nvidia/nemotron-3-diarization); [Sortformer v2 card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2); [NeMo docs](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html)
- **pyannoteAI STT orchestration** (Dec 2025): Precision-2 with Parakeet or Whisper large-v3-turbo in one call. Claims better tcpWER than typical STT providers but gives no figures [VENDOR]. — [pyannoteAI changelog](https://www.pyannote.ai/changelog)

### Inferences
- The project already has Whisper `turbo` text output. The lowest-friction path is to rerun through WhisperX, or to run community-1 or Nemotron separately on the audio and align with word timestamps. Assigning each Whisper *segment* or sentence to the speaker with maximum time overlap is usually enough for teacher-vs-questioner labeling; per-word assignment is unnecessary.
- The LLM cleanup stage (Llama) rewrites text, so speaker labels should be attached *before* cleanup as paragraph or turn markers, and the cleanup prompt must preserve them. Otherwise the `likeness.py` similarity gate may also be affected.

### Gaps
- The exact matching logic of `assign_word_speakers` (overlap-based, plus a "fill nearest" option) was not described on the README fetched. It is recalled from memory and needs checking in the code.
- No primary source was found for a documented NeMo Python recipe that combines Parakeet word timestamps with Sortformer or Nemotron output; only NeMo-Speech.cpp's flag is documented on the cards.
- The current WhisperX version and release date were not stated on the README.

---

## 5. Identifying the same speaker across files (teacher enrollment)

### Takeaway
This is straightforward with open embedding models. Enroll each known teacher from a few clean clips, compute a centroid embedding, then label each diarized cluster by cosine similarity to the enrolled teachers, with a threshold below which the cluster becomes "Questioner/Other". pyannoteAI sells this as a hosted voiceprint API (Precision-2+ only). Open equivalents are TitaNet-L, WeSpeaker, CAM++/ERes2Net, or pyannote's own embedding model.

### Cited Findings
- **pyannoteAI voiceprints:** two steps. `/v1/voiceprint` creates a voiceprint from up to 30 s of clean single-speaker audio. `/v1/identify` diarizes and labels speakers with enrolled names or "unknown". Limits: up to 50 voiceprints per job, files up to 24 h or 1 GiB. Works with **Precision-2 only, not community-1**. Voiceprints are billed per creation and identification per audio hour. Voiceprints do not improve diarization accuracy. — [pyannoteAI docs: identification with voiceprints](https://docs.pyannote.ai/tutorials/identification-with-voiceprints); [API ref: identify](https://docs.pyannote.ai/api-reference/identify.md); [blog: recurring meetings](https://www.pyannote.ai/blog/speaker-identification-system-recurring-meetings)
- **Open embedding models and VoxCeleb1-O EER:**
  - TitaNet-L (CC-BY-4.0, NeMo): 0.66%. Source: [HF](https://huggingface.co/nvidia/speakerverification_en_titanet_large)
  - WeSpeaker ResNet293 (Apache-2.0): 0.447%; ResNet34: 0.723%; ECAPA-c1024: 0.728%. Source: [WeSpeaker](https://github.com/wenet-e2e/wespeaker)
  - CAM++ and ERes2NetV2 (Apache-2.0): 0.65% and 0.61%. Source: [3D-Speaker](https://github.com/modelscope/3D-Speaker)
- **Tooling:** TitaNet provides `get_embedding()` and batch extraction through `extract_speaker_embeddings.py` with a manifest. WeSpeaker provides a CLI with `--task embedding` and `--task similarity`. — [TitaNet card](https://huggingface.co/nvidia/speakerverification_en_titanet_large); [WeSpeaker](https://github.com/wenet-e2e/wespeaker)
- **WeSpeaker 2026 U³-xi** (uncertainty-aware embeddings and scoring) is potentially relevant for variable-quality audio, but this is untested here. — [WeSpeaker](https://github.com/wenet-e2e/wespeaker)

### Inferences
- **Recommended open approach:**
  1. Diarize.
  2. For each cluster, average the embeddings of its longer segments (more than 3 s).
  3. Compare against per-teacher centroids built from several talks per teacher, ideally spanning cassette and modern recordings to cover channel variation.
  4. Assign the teacher label if similarity is above a threshold tuned on a small hand-labeled set, otherwise "Other".
  5. As a prior, in most talks the teacher is the cluster with the most speaking time.
- The talk metadata in the CSV/JSON likely already names the speaker. That gives weak labels for building teacher centroids automatically: take the dominant cluster of talks attributed to teacher X, then remove outliers.
- Cassette transfers and modern recordings differ in channel, so expect lower same-speaker similarity across eras. Per-era centroids or score normalization (AS-Norm, as in WeSpeaker) may be needed.

### Gaps
- No published benchmark was found for cross-decade or cassette-vs-digital speaker verification robustness with these models.
- pyannoteAI voiceprint and identification prices were not found.

---

## 6. Chanting, overlapped speech, bells and silence

### Takeaway
No diarizer is designed for group chanting. Expect it to appear as a spurious speaker cluster, or as heavy overlap, or to be absorbed into the teacher's cluster. Singing-like speech is known to cluster separately from the same person's normal speech. Bells and music can cause speaker splitting. Silence is handled by each system's VAD; missed speech at segment boundaries is the dominant error in independent tests.

### Cited Findings
- In the independent benchmark, missed speech was the dominant error for most models (except Sortformer, which had more speaker confusion). Missed segments averaged about 350 ms, attributed mainly to onset and offset timing. — [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1)
- community-1's segmentation (VAD and overlap detection) is unchanged from 3.1. pyannote claims to handle overlap better than STT models do, but gives no numbers. — [community-1 blog](https://www.pyannote.ai/blog/community-1)
- Precision-3 adds tunable `vadSensitivity` and `crosstalkSensitivity` [VENDOR]. — [changelog](https://www.pyannote.ai/changelog)
- Background music can split one speaker into several clusters; one mitigation is merging clusters whose centroids are very similar. — via search summary of [Bixby VoxSRC-21 system, arXiv 2109.13518](https://arxiv.org/pdf/2109.13518) (not fetched in full)
- Singing changes the time-frequency structure of a voice, so the same speaker's sung and spoken segments can cluster apart. — [Mehrabani & Hansen, Speech Communication 2013](https://personal.utdallas.edu/~jxh052100/Publications/JP-90-SpeechComm-Mehrabani-Hansen-SigningSpeakerCluster-Mar2013.pdf)
- Choral singing is called unsuitable for standard simulated training data in singer-diarization research. — via search summary of [arXiv 2406.16315](https://web3.arxiv.org/pdf/2406.16315) (not fetched in full)
- Sortformer models are trained with MUSAN noise augmentation (Nemotron-3) and on mostly conversational English data; neither card addresses music or singing. — [Nemotron-3 card](https://huggingface.co/nvidia/nemotron-3-diarization); [Sortformer v2 card](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2)

### Inferences
- Practical handling options:
  1. Run an audio tagger or music/singing detector (e.g., a PANNs or AST-style AudioSet classifier) to mark chanting and bell regions and exclude them from diarization and identification.
  2. Label any short-lived, high-overlap cluster that doesn't match an enrolled teacher as "Chanting/Group" rather than "Questioner".
  3. Whisper often hallucinates or outputs repeated text over chanting, so the same masks help ASR cleanup.
- Long silences are generally harmless to diarization (VAD drops them), but they lengthen wall-clock time slightly for chunked end-to-end models.

### Gaps
- No benchmark or primary source was found on diarizer behavior on liturgical or group chanting specifically. This needs empirical testing on a sample of talks.
- The AudioSet tagger suggestion is my own inference; no source was fetched for a specific model.

---

## 7. Hosted options (AssemblyAI, Deepgram, pyannoteAI, Speechmatics, ElevenLabs Scribe, Gemini)

### Takeaway
Hosted diarization is cheap. Third-party comparisons put STT with diarization at roughly $0.15–0.60 per audio hour, which would be about $1k–4k for 7,000 h. Accuracy claims are mostly vendor-run. pyannoteAI has the best independently verified diarization (Precision-2), but it's a diarization specialist, not full ASR, unless you use its orchestration feature. Pricing data below comes from secondary aggregators and should be re-checked.

### Cited Findings
- **AssemblyAI:** diarization add-on reported at $0.02/h for recorded audio ($0.12/h real-time). With base STT plus speaker labels, about $0.17/h (March 2026 comparison). — via search summaries of [costbench AssemblyAI vs Deepgram](https://costbench.com/compare/assemblyai-vs-deepgram) and [brasstranscripts](https://brasstranscripts.com/blog/assemblyai-vs-deepgram-pricing-high-volume-comparison) (third-party, not fetched)
- **Deepgram:** diarization add-on about $0.002/min ($0.12/h). One comparison put Nova-3 with diarization at about $0.58/h, but sources disagree on the base price. — same third-party sources (not fetched)
- **ElevenLabs Scribe v2:** diarization is batch-only, about $0.22–0.27/h base per third-party and competitor pages (Soniox page updated Sep 2026). — [Soniox pricing compare](https://soniox.com/compare/stt/pricing); [Speechmatics vs ElevenLabs (competitor page)](https://www.speechmatics.com/how-we-compare/elevenlabs-scribe-alternative.md)
- **Speechmatics:** claims real-time diarization at no extra charge [VENDOR]. — [Speechmatics comparison page](https://www.speechmatics.com/how-we-compare/elevenlabs-scribe-alternative.md)
- **pyannoteAI:** €19/month (125 h) and €99/month (825 h) plans; Precision-3 at the same price as Precision-2; voiceprint identification; up to 24 h per file. — [changelog](https://www.pyannote.ai/changelog); [pyannoteAI docs](https://docs.pyannote.ai/tutorials/identification-with-voiceprints)
- pyannoteAI publishes a "top 7 speaker diarization APIs and models in 2026" comparison. **It is a vendor ranking and should not be treated as neutral.** — [pyannoteAI blog](https://www.pyannote.ai/blog/top-7-speaker-diarization-apis-and-models-in-2026)

### Inferences
- At these prices, a hosted pass over the whole archive costs on the order of the GPU rental for a local pass. The deciding factors are the stated preference for local and open-weight models, data handling for the archive, and whether hosted ASR is better than the existing Whisper turbo output.
- A hybrid is plausible: run local open diarization everywhere, and send only the talks flagged as multi-speaker (Q&A) to Precision-3 or an STT API.

### Gaps
- **No independent DER numbers** were found for AssemblyAI, Deepgram, Speechmatics or ElevenLabs diarization on standard benchmarks.
- **Gemini diarization:** no primary source on quality, limits or price was found in this pass.
- Vendor pricing pages were not fetched directly; all prices above are from aggregators and dated 2026. Verify before budgeting.

---

## 8. Is full diarization worth it for mostly-monologue talks? Cheaper heuristics

### Takeaway
For about 6,500 mostly single-teacher talks, a lightweight "VAD, then embedding similarity to the teacher" approach is probably enough for most files. Full diarization is worth running mainly on talks with Q&A or introductions. Modern open diarizers are fast enough (Sortformer and Nemotron at hundreds to thousands of times real time; pyannote about 45x) that running full diarization on everything is also affordable on one rented H100. The real cost is in handling chanting and old audio, and in validating labels, not in compute.

### Cited Findings
- Speed context: Sortformer v2 about 210x real time, pyannote 3.1 about 45x, DiariZen about 20x (A6000); Nemotron-3 offline over 1,300x at batch size 1 (Blackwell, vendor). — [arXiv 2509.26177](https://arxiv.org/html/2509.26177v1); [Nemotron-3 card](https://huggingface.co/nvidia/nemotron-3-diarization)
- Speaker-counting errors are a major residual problem even for top systems. Precision-2 counted speakers correctly on only 70% of files in pyannote's hardest benchmark [VENDOR], and Nemotron-3 had 81.5% speaker-count accuracy on DIHARD III [VENDOR]. — [changelog](https://www.pyannote.ai/changelog); [Nemotron-3 card](https://huggingface.co/nvidia/nemotron-3-diarization)
- Embedding verification is very accurate on clean speech (EER about 0.5–0.7%). — [WeSpeaker](https://github.com/wenet-e2e/wespeaker); [TitaNet](https://huggingface.co/nvidia/speakerverification_en_titanet_large)

### Inferences
- **Suggested tiered approach (inference, not sourced as a recipe):**
  1. Run VAD, then compute embeddings on sliding windows (about 1.5–3 s) over each talk.
  2. Score each window against the enrolled teacher centroid; also take the talk's own dominant-speaker centroid, which helps when metadata names the speaker.
  3. If more than about 97–98% of speech is the teacher, label the whole talk as monologue and mark the few non-matching spans as "Other".
  4. Only on talks with a meaningful share of non-teacher speech (Q&A, introducer), run full diarization (community-1, Nemotron-3, or Precision-3 hosted) and identify clusters against the teacher centroids.
- Because talks run 30–90 minutes with 1–5 speakers, end-to-end models with a 4- or 8-speaker cap (Sortformer v2, Nemotron-3) fit well, and their speed lets you diarize everything anyway. Run diarization everywhere, then run teacher identification on the clusters. The cheap heuristic then mostly serves as a sanity check.
- Validation: hand-label 20–50 talks across eras (cassette vs. modern; with and without Q&A) to tune thresholds and compare community-1, Nemotron-3 and DiariZen locally. Public benchmarks (meetings, telephone, broadcast) do not resemble single-mic dharma talks with chanting.

### Gaps
- No published study was found on diarization error rates for long monologue lectures or sermons specifically. Benchmarks focus on meetings, telephone, broadcast and in-the-wild video.
- No measured comparison of "VAD plus embedding heuristic" against full diarization on lecture-style audio was found.
