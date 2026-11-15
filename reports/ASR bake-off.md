# ASR bake-off

_Generated 2026-11-15 12:02 by `eval/report.py`. Re-run after adding systems or references._

**Gold set:** 50 speech excerpts (5.0 h, one per talk, stratified by era / speaker / content / audio difficulty) and 76 non-speech clips (38 min of bells, silence and room noise where VAD finds <10% speech). **Corrected references: 0/50.**

## Findings

_Hand-written interpretation (`eval/findings.md`, last edited 2026-11-15). The tables below are regenerated each run; re-check this section when they change._

These notes cover 30 setups from 6 model families, on 38 stratified speech excerpts plus 12 book excerpts, and 76 non-speech clips. **No transcript has been fully hand-corrected.** Items 1–7 use metrics that don't need a reference. From item 8 on, accuracy is measured against automatic (silver) references: a vote across model families, checked against the glossary, the edited book text, an LLM review of flagged spots and 40 spots settled by ear. The latest results are items 19–20 and the recommendation at the end; earlier items keep the numbers measured at the time.

### What we learned

1. **The per-talk prompt works, and Whisper turbo uses it safely.**
   - **Misheard terms:** turbo's share drops from 13.0% to 3.2% with the prompt, while only 2.2% of words change. The fixes are the ones we wanted: dokusan, sesshin, Maezumi, Daido Roshi, gassho, Urban Upaya.
   - **Side effects:** turbo with the prompt never echoed the prompt and never looped, at the same speed (about 150× real time, about 2 days for the archive on this PC).

2. **Whisper large-v3 with the prompt is unsafe as configured.**
   - **Best spelling:** it has the lowest misheard share of any Whisper setup, at 1.9%.
   - **Prompt echo:** in 12 of 38 clips it *replaced whole 30-second windows with prompt text*. For example, "Liberating Sexuality Retreat Part 1" stands in for about 60 words of speech, four times in one clip. That's 2.3% of all speech audio lost, which is why its word rate falls from 110 to 104 per minute.
   - **Speed:** it is also 2.5× slower than turbo.
   - **If we use it at all:** detect echoes and redo those windows without the prompt.

3. **Qwen3-ASR needs VAD, and a term list rather than prose.**
   - **Without VAD,** it invents text on almost every silent clip ("The."×24). With the prose prompt it reads the prompt aloud ("This is a dharma talk by…"×54).
   - **With VAD,** non-speech output drops from 74 of 76 clips to 7, the same as Whisper.
   - **A comma-separated term list** gives 0 prompt echoes, where the prose prompt gave 5 clips.
   - **Misheard share** is the lowest of all, at 1.7–2.3%. But see point 6: this metric flatters non-Whisper systems.
   - **Cost:** it is about 7× slower than turbo, about 12 days for the archive on this PC. It's a candidate for a cloud run or a second pass on hard talks.

4. **Parakeet boosting is a trade-off we can't settle without references.**
   - **Strong boosting** (alpha 0.5–1.0) fixes names, e.g. Obakra → Obaku. It also invents terms from ordinary words: "koan"/"Khan" ×4–6, "So" → "Soz".
   - **Gentle boosting of hard terms only** (0.3) avoids those insertions but fixes little: misheard share is 13.0%, against 13.7% plain.
   - **Speed:** Parakeet is the fastest system (about 190–220× real time) and the least prone to inventing text on silence.
   - **Weakness:** it misspells far more names than prompted Whisper, and its output keeps every "um"/"uh".

5. **The residual non-speech output is mostly the clips' fault, not the systems'.** The same handful of clips trigger output in nearly every system. One begins "Sentient beings are…", the start of a chant. They likely hold faint speech or chanting, so the clips need checking by ear (`verified` in the manifest). The real contrast is legacy and Qwen without VAD (nearly 100%) against everything else (5–9%).

6. **Known metric biases.**
   - **Non-Whisper systems look better than they are.** The misheard list was mined from Whisper output, so it catches Whisper's misspellings and misses other systems' ("Mizumi" was added only after Parakeet produced it).
   - **The legacy transcripts look worse than they are on non-speech.** The non-speech clips were chosen where they had invented text.
   - **A prompt can push the misheard share down by inserting terms nobody said.** That only shows up as false insertions, which need references to measure.

7. **The archive has audio problems that no model fixes.**
   - **Two excerpts excluded:** one is a near-silent talk (29856, about −61 dB). The other is a "Sounds" talk window with no speech in it (29668).
   - **Many more suspect talks:** across the archive, 59 talks have legacy transcripts that are more than half "Thank you"-style filler, and 88 more are 15–50% filler. They should be checked for broken or quiet recordings before transcription.

### Output analysis: silver references and the book (2026-11-10)

These results cover 50 speech clips: the 38 stratified clips plus 12 talks from 1981–85 that also appear, edited, in *Mountain Record of Zen Talks* (1988).

8. **Context helps, judged against an independent text.**
   - On the book clips, I counted the names and terms that both the book and the audio clearly contain (45 occurrences).
   - Whisper turbo with the prompt spells 84% of them as the book does. That's the best result; the unprompted Whisper systems reach 78%.
   - Context raises Parakeet from 62% to 80% with boost 1.0, and Qwen from 76% to 80% with VAD and the term list.
   - The sample is small, so treat differences under about 10 points as noise.

9. **What the prompt changes.** For each prompted system, I took every glossary term the prompt introduced and checked the matching spot in the unprompted twin's output:

   | System | Corrections | Insertions | Precision |
   |---|---|---|---|
   | Whisper turbo + prompt | 58 | 3 | about 95% |
   | Parakeet boost 1.0 | 35 | 7 | about 83% |
   | Qwen + term list | 36 | 17 | about 68% |
   | Qwen + prose prompt | 53 | 65 | about 45% |
   | large-v3 + prompt | 44 | 70 | about 39% |

   - A **correction** means the twin had a misspelling there: Maizumi → Maezumi, doksan → dokusan, gasho → gassho, Yakujo → Hyakujo.
   - An **insertion** means the twin had nothing similar there.
   - Qwen with the prose prompt inserts "Zen Mountain Monastery" ×7 and "John Daido Loori" ×5.
   - large-v3 with the prompt inserts "of" → "Fukanzazengi", "you" → "Kashyapa", "how" → "Vimalakirti".
   - Parakeet's gentle boost (0.3, hard terms only) changes almost nothing: 3 corrections, 1 insertion.

10. **faster-whisper drops runs of real speech.**
    - **How much:** it loses 1.6–2.4% of words in runs of 4+ words, in 20–24 of 50 clips. Turbo with the prompt loses 2.4%, plain turbo 1.6%, and large-v3 with the prompt 7.4% (prompt echo).
    - **For comparison:** the legacy Whisper CLI, which used no voice detection, loses 0.5%; parakeet-ft-v1 and Qwen with VAD about 0.2%.
    - **Where:** about a third of these drops fall where the voice detector found no speech. That's mostly quiet audience questions and chanted refuges.
    - **The rest** were detected but skipped by the decoder. Often these are disfluent stretches, but sometimes content.
    - **Fixes worth testing:** a lower VAD threshold or more padding, and smaller batches or no batching.

11. **parakeet-ft-v1 does fix Parakeet's skipped passages.** Plain v3 drops 1.5% of words in runs and the fine-tune 0.2%. That matches its model card's 87 → 3 skipped passages. Its names are no better (64% book-term recall), so it needs boosting.

12. **Each family has its own failures** (reading every flagged spot; the book settles some):
    - **Whisper** is best at real names and content words. It was right on 67% of the disputed content words the book settles, against 56% for Parakeet and 45% for Qwen. Examples: Nhat Hanh, oxherding, Sosan, Remington. It drops quiet speech and repeated words.
    - **Parakeet** is the most complete: right on 85% of disputed function words, and it rarely loses a phrase. But it spells by sound: oxerting, arvicious, Kunjan, cons (koans), versus (verses), liver (river), Moo (Mu).
    - **Qwen** paraphrases and normalizes (obtrusive for avaricious, "Just move" for "Just Mu"), and it drops small words. It sometimes outputs long passages no other system has, which could be faint speech or invention; the flags mark them for review.
    - **Q&A with quiet questioners** is where the systems diverge most, and most flagged regions are there.

13. **The book is a useful but imperfect judge.**
    - The editors replaced words: "meditation" became "zazen", "he" became "Avalokiteshvara". So where the book differs from every system, it's usually editing, not a shared error.
    - It also has its own errors: "Kongen", "Yoshita" for Kangen, Yoshida.
    - It does catch some errors every system makes: "sequential steps", which the systems wrote as "sequent", "sequence" and "sequined".

14. **Silver-reference changes made from this (2026-11-14).**
    - **Ties:** a glossary term, or a known mishearing of one, wins over other words. A real word wins over a non-word ("oxherding" over "oxerting"). After that, the vote goes to the family most often right on that kind of word, measured on disputes the book settles:

      | Family | Content words | Function words |
      |---|---|---|
      | Whisper | 67% | 53% |
      | Parakeet | 59% | 86% |
      | Qwen | 43% | 47% |

    - **Glossary:** lookups strip possessives, so "Yunmin's" becomes "Yunmen's". New misheard forms: Tiknad Han, Tikkadhan → Thich Nhat Hanh.
    - **Book:** where every system was near the book's word, the book's spelling is used ("sequent"/"sequined" → "sequential"). "Book differs" no longer raises a flag. A book-unresolved word with a 2/3 majority counts as medium confidence.
    - **Effect:** these changes cut the flagged spots from 338 to 202.

15. **LLM review of the flagged spots** (`eval/goldset/judge.json`). I read all 202 spots as text, with each voter's words, the prompted turbo output and the book passage.
    - **Rule:** a fix may only use words that some system, the glossary or the book wrote. Spots that need the audio are marked *unclear*.
    - **Results:** 71 fixes, 101 kept, 30 unclear.
    - **What the fixes catch** is what voting can't: a real word in the wrong place. Examples: "This koan is human's attempt" → Yunmen's, "Einstein didn't say yes" → Nansen, "the denture rings" → densho, "Mr. Ruben Sanza" → "As Ryushin Sensei", "just grafted that off" → scraped.
    - **What it can't settle:** names no system spelled right, quiet audience speech, mantras, dates (Nansen's birth year, which the systems wrote as 1748 or 1948).
    - **After review,** 31 flagged regions remain in the 50 clips. That's a short listening list.
    - **Scores:** silver WER drops 0.1–0.2 points for every system and the ranking doesn't change, so the earlier comparisons hold.
    - **Caveats:**
      - A decision is located by the words around it, so it applies in only 63–78% of the leave-one-family-out rebuilds.
      - An LLM judge prefers fluent text, which could favour systems that paraphrase. That's why it may only choose among existing words.
      - Use `eval/silver.py score --no-judge` for the voting-only numbers.

16. **Listener pass (2026-11-15).**
    - **What was settled:** in the viewer, a listener settled 40 spots in 20 clips: 35 corrections or confirmations, and 5 they couldn't make out. Two flagged regions remain, including the 30 s of noise that opens 30643.
    - **Overlap with the LLM review:** most of the listener's decisions resolved spots the LLM review had marked unclear. Example: "up and must a down" became "up unless there's a down", matching the book.
    - **What it doesn't measure:** the LLM's 71 fixes weren't flagged, so they haven't been checked by ear yet.
    - **Scores:** silver WER moves by 0.01–0.07 points and the ranking is unchanged.

17. **Whisper turbo's dropped speech: fixed by decoding one window at a time (2026-11-15).** `eval/drops.py` counts reference words lost in runs of 4+:

    | turbo + prompt, variant | Silver WER | Book clips | Words lost in runs | Misheard | Silent clips with text | Speed |
    |---|---|---|---|---|---|---|
    | batched (previous default) | 6.50% | 5.53% | 1.74% | 3.9% | 7/76 | 151× |
    | batched, VAD 0.35 / 800 ms pad | 6.12% | | 1.28% | 4.3% | 10/76 | 128× |
    | batched, no-speech skip off | 6.50% | | 1.74% | 3.9% | 7/76 | 153× |
    | sequential | 6.10% | | 0.92% | 3.9% | 7/76 | 87× |
    | sequential, VAD 0.35 / 800 ms | 5.63% | 4.39% | 0.74% | 3.8% | 10/76 | 83× |
    | **+ prompt-echo filter + hallucination_silence 2 s** | **5.59%** | **4.20%** | **0.71%** | **3.8%** | **7/76** | **80×** |
    | same, longer prompt (`data/context-long`) | 5.44% | 4.66% | 0.54% | 4.8% | 10/76 | 82× |
    | sequential, no VAD | 6.50% | | 0.52% | 3.2% | 72/76 | 68× |
    | plain turbo, no prompt, for comparison | 5.79% | 5.38% | 0.99% | 13.1% | 7/76 | 150× |

    - **Batching is the main cause.** It cuts audio into 30 s windows at voice-detector boundaries, and decoding several at once loses words. A more sensitive detector helps a bit more.
    - **"No-speech skip off" changes nothing.** Batched decoding doesn't use that setting.
    - **No voice detection is unusable.** It writes text on 72 of 76 silent clips.
    - **The prompt-echo filter** removes segments that only repeat the prompt, e.g. "This is a dharma talk" read into the noise at the start of 30643.
    - **The longer prompt scores 0.15 points better overall, within noise.** It spells terms worse and recited a term list on a silent clip ("Doshinji, shikantaza, nirvana, nirvana…"), so it's not recommended.

18. **First A10 cloud run (2026-11-15, $2.32).**
    - **Run status:**
      - Parakeet-ft on whole clips and Granite (± term list) finished.
      - VibeVoice crashed at clip 27 on malformed output; the runner now salvages it and caps output length.
      - Nemotron didn't start: the server binary was built without HTTP; the build script is fixed.
    - **Granite as a fourth voter:**
      - It is the most reliable family on content words against the book (70%; Whisper 67%, Parakeet 63%, Qwen 51%).
      - Ties are now decided by these reliability weights and become medium confidence when the weights clearly favour one side.
      - The reference's timing always comes from a system with word timestamps (Whisper or Parakeet). Before, Granite or Qwen could be the pivot, and seeking was off in those clips.
      - Decisions survive a changed vote: a nearby partial match of their context words is accepted. Applied now: 162 of 172 LLM decisions, and all 36 current listener decisions.
    - **Silver WER with four families:**
      - Production Whisper setup: 5.16%, and 3.84% on the book clips, best of all.
      - parakeet-ft + VAD: 5.18%, but misheard terms are 16.6% against 3.8%.
      - Plain turbo: 5.35%. Qwen + VAD: 5.71%.
      - Granite: 7.7%. It skips stretches mid-chunk, losing 3.0% of words in runs, and runs at about 20× real time. Its book-clip WER is good (4.4%). Its term list helps spelling a little (13.0% → 10.3% misheard). Not a production candidate.
    - **VibeVoice (18 speech clips so far):** no lost stretches at all and very few deletions (0.4%). It keeps disfluencies (120 words/min), so its insertions are higher. Worth finishing.

19. **Second A10 run: Nemotron and VibeVoice finished, six voting families (2026-11-15, $3.05; $5.43 for all three launches).**
    - **References:** six families now vote (Whisper, Parakeet, Qwen, Granite, VibeVoice, Nemotron), so each system is scored against five others. 167 regions are flagged. 169 of 172 LLM decisions and all 36 current listener decisions apply. A decision that falls in a long stretch the vote left empty now matches by the gap's time, not the next word's (it had dropped "sheep on strong longing funny" in 31039).
    - **One clip left out of WER:** `30643_s01710` is mostly unintelligible (62 reference words in 6 minutes; settled by ear as unclear). Every system writes unrelated text there, and VibeVoice loops ("uh, this is" ×1,600, 3,297 words), which alone added 6 points to its WER. It stays in the loop and non-speech checks (`unscored` in the manifest).
    - **Silver WER (49 clips), with the paired difference from the production Whisper setup:**

      | System | WER | 95% range | vs production | Book clips | Lost in runs | Misheard terms | Silent clips with text |
      |---|---|---|---|---|---|---|---|
      | Nemotron 3.5 + term list | **2.9%** | 2.2–3.8% | −1.9 (−2.6 to −1.3) | **3.0%** | **0.09%** | **0.4%** | 10/76 |
      | Nemotron 3.5 | 2.9% | 2.2–3.8% | −1.9 | 3.0% | 0.09% | 4.0% | 10/76 |
      | VibeVoice + term list | 3.4% | 2.3–4.9% | −1.4 (−2.2 to −0.6) | 4.3% | 0.04% | 1.8% | 3/76 |
      | Parakeet-ft + VAD | 3.6% | 2.6–4.7% | −1.2 (−1.9 to −0.5) | 3.7% | 0.35% | 16.6% | 4/76 |
      | VibeVoice | 3.8% | 2.5–5.3% | −1.1 (−2.0 to −0.2) | 4.2% | 0.17% | 5.3% | 4/76 |
      | Qwen + VAD | 4.7% | 3.4–6.4% | −0.1 (−1.0 to +0.9) | 5.5% | 0.57% | 2.9% | 7/76 |
      | Production Whisper setup | 4.8% | 3.8–6.0% | — | 3.7% | 0.81% | 3.8% | 7/76 |

    - **The book agrees, independently of the vote.** Where the book settles a disputed word, the share each family got right:

      | Family | Content words | Function words |
      |---|---|---|
      | Nemotron | **80%** | 80% |
      | VibeVoice | **80%** | **88%** |
      | Granite | 70% | 68% |
      | Whisper | 66% | 61% |
      | Parakeet | 62% | 86% |
      | Qwen | 51% | 58% |

      These shares also set the tie-break weights in the vote.
    - **Part of Whisper's gap is style.** Its errors are mostly deletions (2.8%, against 0.5% for Nemotron): it tidies "you know", leading "and" and repeated words, which the other five families write verbatim. Collapsing repeated words in reference and output narrows the gap from 1.9 to 1.6 points; "you know" and "and" account for roughly another 0.3–0.5. The rest is real: lost speech (0.8% vs 0.1%) and misheard words.
    - **Nemotron's term list fixes spelling without hurting accuracy:** misheard terms 4.0% → 0.4% (2 of 455) at the same WER. With the term list it spells names better than any other system.
    - **Nemotron caveats:**
      - It ran without voice detection and writes text on 10 of 76 silent clips. Two of these hold real chanting ("Sentient beings are numberless…", "Kanzeon… namu…"). The others are loops ("Knock knock knock…", "Yeah, yeah, yeah…"), so production needs VAD.
      - It returns plain text with no timestamps through NeMo-Speech.cpp's server. Paragraphs by pauses and audio sync would need its words aligned to Whisper or Parakeet timings (as `eval/silver.py` already does).
      - It keeps "uh"/"um" and punctuates less (12 marks per 100 words against 16).
      - It needs a 24 GB GPU (22 GB in use), so it can't run on the 8 GB 3070 Ti.
    - **VibeVoice** is accurate but slow (item 20), loops on noise, and writes sound tags ("[Music]", "[Lyric]") that need stripping.

20. **Throughput: running several clips at once on one A10 (`asr/throughput.py`, report section "Throughput").**

    | Setup | One stream | Best parallel setting | Gain | Archive on one A10 | Cost at $1.29/h |
    |---|---|---|---|---|---|
    | Whisper production setup | 70× | 2 processes: 87× | 1.25× | 3.1 days | about $96 |
    | Whisper batched (drops speech) | 144× | 2 processes: 199× | 1.4× | 1.4 days | about $42 |
    | Nemotron 3.5 (4-bit) | 50× | 4 requests in flight: 85–90× | 1.7× | 3.1 days | about $95 |
    | VibeVoice | 6× | batch of 4: 9× | 1.5× | 31 days | about $950 |

    - **Whisper's sequential decoding leaves the GPU 39% idle,** but more processes don't fill it usefully: 4–8 processes reach 96–98% busy at 77–84×. Two is the sweet spot.
    - **One Whisper stream is faster on the 3070 Ti (80×) than on the A10 (70×).** Locally, a second process doesn't fit next to the desktop's GPU use (tested: out of memory).
    - **Nemotron benefits most from parallel work:** its server decodes up to 4 requests together.
    - **VibeVoice keeps the GPU 95% busy even one clip at a time,** so batching helps little. A batch of 4 fits in 21 GB.
    - Several GPUs divide the time but not the cost; at these prices a full archive pass on A10s costs about $95 for Nemotron or Whisper.

21. **Nemotron on an A100 40 GB: about half the A10's cost per audio hour (2026-11-15, $1.04).** Same 4-bit model, 50 speech clips (5.2 h) per setting, $1.99/h:

    | A100 setting | Throughput | GPU memory | Archive on one A100 | Cost | Silver WER |
    |---|---|---|---|---|---|
    | 4 requests, A10 settings (no speculative decoding) | 142× | 22.0 GB | 1.9 days | $91 | 2.90% |
    | 16 requests | 183× | 24.4 GB | 1.5 days | $71 | 2.86% |
    | 16 requests, speculative decoding (`mtp_draft=7`) | 215× | 26.0 GB | 1.3 days | $60 | 2.91% |
    | **32 requests, speculative decoding** | **259×** | 29.2 GB | **1.0 day** | **$50** | 3.00% |
    | *A10, 4 requests (item 20)* | *85×* | *21.7 GB* | *3.2 days* | *$95* | *2.91%* |

    - **The saving comes from memory, not raw speed:** at the A10's settings the A100 is 1.7× faster but 1.5× the price, so it costs about the same. Room for more requests in flight and for speculative decoding (the model drafts up to 7 tokens per step and checks them) is what halves the cost.
    - **Accuracy doesn't change:** all four settings score 2.86–3.00% against the A10 run's 2.91%. The texts differ slightly (batched arithmetic), but not the error rate.
    - **32 requests on 50 clips leaves the GPU half idle for the last wave,** so the archive, with thousands of requests queued, should do a little better than 259×. 29 GB of 40 GB was in use; 48 requests might fit.
    - **Larger cards were not available to test.** GH200 (96 GB, $2.29/h, ARM) and H100 (80 GB, $3.29–4.29/h) could take far more requests at once; NeMo-Speech.cpp's docs suggest 240 on 80 GB+.
    - Model download and build took 20 minutes on this instance (7 on the A10), so a run's fixed cost is about $0.70.

### Recommendation (provisional, 2026-11-15)

- **Switch the archive run to Nemotron 3.5 + term list on a cloud A100,** if a pilot confirms it on full talks. It's the most accurate system tested (2.9% silver WER, 1.9 points better than the Whisper setup, of which about 1.3–1.6 is not style), it loses almost no speech and spells names best (0.4% misheard). With 32 requests in flight and speculative decoding it costs about $50 for the archive on one A100 40 GB (about a day), against about $95 on an A10 (item 21).
  ```
  uv run python asr/run_nemotron_cpp.py --terms --concurrency 32 --salm max_sequences=32 \
      --salm n_ctx_per_sequence=4096 --salm max_context=73728 --salm mtp_draft=7 --salm n_batch=4096 --salm encoder_max_batch=32
  ```
  Before that it needs: voice detection (decode VAD speech spans, as Parakeet does), word timings by alignment to a timed system, filler removal, and a check on full-length talks.
- **Fallback and free local option:** the production Whisper setup (item 17), about 3.4 days on this PC. It's the safest on silent clips and keeps timestamps, but it's clearly less accurate.
  ```
  uv run python asr/run_whisper.py --model large-v3-turbo --context --batch-size 0 \
      --vad-threshold 0.35 --vad-pad-ms 800 --drop-prompt-echo --hallucination-silence 2
  ```
- **Not recommended:**
  - VibeVoice for the full archive: accurate, but about $950 and loops on noise. It could serve a few hard talks.
  - Granite: skips speech mid-chunk.
  - large-v3 with a prompt: echoes the prompt.
  - Qwen with a prose prompt: echoes and inserts.
- **Remaining measurement gap:** every number here is against automatic references. A mistake all six families share stays invisible, and only the 12 book clips and the listener's 40 spots are independent checks.

> **Accuracy (WER) is not measured yet.** No corrected references exist, so this report shows only what can be measured without them: speed, hallucination on non-speech, how each system spells glossary terms, repetition loops, and agreement between systems. Correct the drafts in `eval/goldset/drafts/` into `eval/goldset/refs/` (see `eval/CONVENTIONS.md`) and re-run to add WER, term recall and per-stratum results.

## Systems

| System | Model | Context | Device | Speed (× real time) | GPU peak | Archive time on this PC* |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | openai-whisper CLI turbo (existing transcripts) | — | unknown | — | — | — |
| `granite-5.0-2b` | ibm-granite/granite-speech-5.0-2b | — | cuda | 19 | 5497 MB | 14.1 days |
| `granite-5.0-2b+terms` | ibm-granite/granite-speech-5.0-2b | keyword list (hard terms, max 20) | cuda | 20 | 5499 MB | 13.3 days |
| `nemotron-3.5-iq4_nl` | nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B (IQ4_NL GGUF) | — | cuda | 90 | 22185 MB | 3.0 days |
| `nemotron-3.5-iq4_nl+terms` | nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B (IQ4_NL GGUF) | context terms (hard terms, max 20) | cuda | 88 | 22187 MB | 3.1 days |
| `parakeet-ft-v1` | freetranscribe/parakeet-ft-v1 | — | cuda | 189 | 5086 MB | 1.4 days |
| `parakeet-ft-v1+vad90` | freetranscribe/parakeet-ft-v1 | — | cuda | 189 | 3509 MB | 1.4 days |
| `parakeet-v3` | nvidia/parakeet-tdt-0.6b-v3 | — | cuda | 228 | 5003 MB | 1.2 days |
| `parakeet-v3+boost0.3f` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.3, hard terms (difficulty>=0.15, with evidence) | cuda | 194 | 5003 MB | 1.4 days |
| `parakeet-v3+boost0.5` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.5, top 40 talk terms | cuda | 193 | 5003 MB | 1.4 days |
| `parakeet-v3+boost1` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=1.0, top 40 talk terms | cuda | 194 | 5003 MB | 1.4 days |
| `qwen3-asr-1.7b` | Qwen/Qwen3-ASR-1.7B | — | cuda | 22 | 5160 MB | 12.4 days |
| `qwen3-asr-1.7b+ctx` | Qwen/Qwen3-ASR-1.7B | system prompt = talk prompt | cuda | 21 | 5649 MB | 12.7 days |
| `qwen3-asr-1.7b+vad` | Qwen/Qwen3-ASR-1.7B | — | cuda | 21 | 5396 MB | 12.7 days |
| `qwen3-asr-1.7b+vad+terms` | Qwen/Qwen3-ASR-1.7B | system prompt = hard-term list | cuda | 21 | 5310 MB | 12.7 days |
| `vibevoice-asr` | microsoft/VibeVoice-ASR-HF | — | cuda | 7 | 21399 MB | 37.1 days |
| `vibevoice-asr+terms` | microsoft/VibeVoice-ASR-HF | prompt = hard terms (max 20) | cuda | 8 | 21401 MB | 31.9 days |
| `whisper-large-v3` | faster-whisper large-v3 | — | cuda | 61 | 4501 MB | 4.4 days |
| `whisper-large-v3+ctx` | faster-whisper large-v3 | hotwords=talk prompt | cuda | 58 | 4995 MB | 4.7 days |
| `whisper-turbo` | faster-whisper large-v3-turbo | — | cuda | 150 | 3320 MB | 1.8 days |
| `whisper-turbo+ctx` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 151 | 3336 MB | 1.8 days |
| `whisper-turbo+ctx+nsoff` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 153 | 3324 MB | 1.8 days |
| `whisper-turbo+ctx+seq` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 87 | 2394 MB | 3.1 days |
| `whisper-turbo+ctx+seq+novad` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 68 | 2426 MB | 4.0 days |
| `whisper-turbo+ctx+seq+vadlo` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 83 | 2490 MB | 3.2 days |
| `whisper-turbo+ctx+seq+vadlo+echo` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 84 | 2394 MB | 3.2 days |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 80 | 2426 MB | 3.4 days |
| `whisper-turbo+ctx+vadlo` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 128 | 3322 MB | 2.1 days |
| `whisper-turbo+ctxlong` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 151 | 3324 MB | 1.8 days |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 82 | 2394 MB | 3.3 days |

\* 6,500 h of audio at the measured speed on short clips (includes per-clip overhead, so full talks run somewhat faster). `legacy-whisper-cli` = the existing transcripts (Whisper CLI turbo, no VAD, no prompt, `condition_on_previous_text=True`).

## Summary

| System | Non-speech clips with invented text | Glossary terms misheard | Prompt echo | Loops | Words/min | Punct./100 words |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | 76/76 (100%) | 11.3% (48 of 425) | — | 3 | 112 | 13.7 |
| `granite-5.0-2b` | 7/76 (9%) | 13.0% (44 of 339) | — | 0 | 106 | 15.7 |
| `granite-5.0-2b+terms` | 7/76 (9%) | 10.3% (37 of 360) | 0 clips | 0 | 106 | 8.7 |
| `nemotron-3.5-iq4_nl` | 10/76 (13%) | 4.0% (18 of 450) | — | 1 | 112 | 11.7 |
| `nemotron-3.5-iq4_nl+terms` | 10/76 (13%) | 0.4% (2 of 455) | 0 clips | 1 | 112 | 12.2 |
| `parakeet-ft-v1` | 3/76 (4%) | 16.3% (59 of 362) | — | 1 | 111 | 11.9 |
| `parakeet-ft-v1+vad90` | 4/76 (5%) | 16.6% (61 of 367) | — | 1 | 111 | 12.4 |
| `parakeet-v3` | 4/76 (5%) | 14.2% (51 of 360) | — | 1 | 109 | 15.5 |
| `parakeet-v3+boost0.3f` | 7/76 (9%) | 13.6% (49 of 359) | 0 clips | 1 | 109 | 15.5 |
| `parakeet-v3+boost0.5` | 5/76 (7%) | 10.9% (41 of 375) | 0 clips | 1 | 109 | 15.5 |
| `parakeet-v3+boost1` | 5/76 (7%) | 10.8% (42 of 388) | 0 clips | 1 | 109 | 15.4 |
| `qwen3-asr-1.7b` | 74/76 (97%) | 2.3% (8 of 354) | — | 0 | 110 | 16.7 |
| `qwen3-asr-1.7b+ctx` | 74/76 (97%) | 2.1% (10 of 476) | 6 clips (1.4% of audio) | 1 | 110 | 16.6 |
| `qwen3-asr-1.7b+vad` | 7/76 (9%) | 2.9% (11 of 374) | — | 0 | 109 | 16.6 |
| `qwen3-asr-1.7b+vad+terms` | 7/76 (9%) | 1.9% (8 of 415) | 0 clips | 0 | 110 | 16.5 |
| `vibevoice-asr` | 4/76 (5%) | 5.3% (20 of 380) | — | 2 | 124 | 21.8 |
| `vibevoice-asr+terms` | 3/76 (4%) | 1.8% (8 of 444) | 0 clips | 2 | 123 | 19.8 |
| `whisper-large-v3` | 7/76 (9%) | 8.0% (33 of 411) | — | 1 | 106 | 15.9 |
| `whisper-large-v3+ctx` | 7/76 (9%) | 2.5% (12 of 475) | 13 clips (2.0% of audio) | 0 | 100 | 16.9 |
| `whisper-turbo` | 7/76 (9%) | 13.1% (55 of 421) | — | 0 | 107 | 16.0 |
| `whisper-turbo+ctx` | 7/76 (9%) | 3.9% (17 of 440) | 0 clips | 0 | 106 | 16.6 |
| `whisper-turbo+ctx+nsoff` | 7/76 (9%) | 3.9% (17 of 440) | 0 clips | 0 | 106 | 16.6 |
| `whisper-turbo+ctx+seq` | 7/76 (9%) | 3.9% (18 of 463) | 1 clips (0.1% of audio) | 2 | 107 | 16.4 |
| `whisper-turbo+ctx+seq+novad` | 72/76 (95%) | 3.2% (15 of 462) | 2 clips (0.3% of audio) | 2 | 109 | 16.5 |
| `whisper-turbo+ctx+seq+vadlo` | 10/76 (13%) | 3.8% (17 of 450) | 2 clips (0.1% of audio) | 2 | 108 | 16.4 |
| `whisper-turbo+ctx+seq+vadlo+echo` | 9/76 (12%) | 3.8% (17 of 448) | 0 clips | 2 | 108 | 16.4 |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | 7/76 (9%) | 3.8% (17 of 444) | 0 clips | 1 | 108 | 16.4 |
| `whisper-turbo+ctx+vadlo` | 10/76 (13%) | 4.3% (19 of 441) | 0 clips | 0 | 106 | 16.6 |
| `whisper-turbo+ctxlong` | 7/76 (9%) | 3.6% (16 of 448) | 0 clips | 0 | 106 | 16.8 |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | 10/76 (13%) | 4.8% (22 of 457) | 0 clips | 1 | 108 | 16.6 |

How to read this:
- **Non-speech clips with invented text**: any words output on a clip with no speech. All of them are errors, so lower is better. Most of these clips were *chosen* at spots where the legacy transcripts invented text, so legacy's score there is near 100% by construction. Compare the new systems with each other.
- **Glossary terms misheard**: share of glossary hits that use a known *wrong* spelling ("Yakujo" for Hyakujo, "doksan" for dokusan). Lower is better. This only counts misspellings already listed in the glossary, and a prompt can push the share down by inserting terms that weren't said, so check it against the false-insertion column once references exist.
- **Prompt echo**: speech clips where a stretch of output repeats the context prompt instead of what was said (the speech there is lost), and the share of speech audio replaced that way. Only systems given a prompt or term list can do this; any non-zero value is serious.
- **Loops**: speech clips where the output repeats a phrase over and over (a classic Whisper failure).
- **Words/min**: big differences from the other systems suggest dropped audio or invented text.

## Accuracy against silver references (automatic, no human)

Each speech clip's reference is built without a human, by `eval/silver.py`:
- **Vote:** a word-level majority vote across one plain system per model family.
- **Glossary:** known misheard spellings are corrected.
- **Book:** for the 12 *book* clips, disputed words are settled against Daido Roshi's edited talks.
- **Ties:** a glossary term or real word wins over a misspelling, then the family most often right on that kind
  of word (measured against the book).
- **Review:** an LLM read every remaining flagged spot as text, without audio (`eval/goldset/judge.json`).
  It could only choose words that some system, the glossary or the book wrote, or mark the spot *unclear*.
- **Listener:** spots settled by ear in the viewer are saved to the same file and override everything else.

**No system grades itself.** Each system is scored against a reference rebuilt *without its own family*.
The *voters* column shows how many families that reference used, and with fewer than about 4 the reference
is weak.

**Errors every system makes go unseen** unless the glossary or the book catches them. Treat these numbers
as a ranking aid until corrected references exist. Browse the flagged spots with `uv run python eval/viewer.py`.

**Ranges:** *95% range* resamples the clips (2,000 bootstrap draws). *vs production* is the paired
difference from `whisper-turbo+ctx+seq+vadlo+echo+hst` on the clips both systems have, in percentage points; a range that
includes 0 means the two can't be told apart on this gold set.

| System | Silver WER (all) | 95% range | vs production | substitutions / deletions / insertions | Stratified set | Book set | Clips | Voters |
|---|---|---|---|---|---|---|---|---|
| `nemotron-3.5-iq4_nl+terms` | 2.9% | 2.2–3.8% | -1.93 (-2.6 to -1.3) | 1.2% / 0.5% / 1.3% | 2.9% | 3.0% | 49 | 5.0 |
| `nemotron-3.5-iq4_nl` | 2.9% | 2.2–3.8% | -1.92 (-2.6 to -1.3) | 1.2% / 0.5% / 1.3% | 2.9% | 3.0% | 49 | 5.0 |
| `vibevoice-asr+terms` | 3.4% | 2.3–4.9% | -1.40 (-2.2 to -0.6) | 1.6% / 0.7% / 1.1% | 3.2% | 4.3% | 49 | 5.0 |
| `parakeet-ft-v1+vad90` | 3.6% | 2.6–4.7% | -1.23 (-1.9 to -0.5) | 1.6% / 0.6% / 1.4% | 3.6% | 3.7% | 49 | 5.0 |
| `vibevoice-asr` | 3.8% | 2.5–5.3% | -1.06 (-2.0 to -0.2) | 1.7% / 0.8% / 1.3% | 3.6% | 4.2% | 49 | 5.0 |
| `parakeet-ft-v1` | 4.0% | 2.9–5.3% | -0.81 (-1.6 to -0.1) | 1.8% / 0.9% / 1.3% | 3.9% | 4.6% | 49 | 5.0 |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | 4.6% | 3.5–5.9% | -0.21 (-0.5 to +0.1) | 1.2% / 2.6% / 0.8% | 4.8% | 4.0% | 49 | 5.0 |
| `qwen3-asr-1.7b+vad` | 4.7% | 3.4–6.4% | -0.08 (-1.0 to +0.9) | 2.4% / 1.6% / 0.7% | 4.5% | 5.5% | 49 | 5.0 |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | 4.8% | 3.8–6.0% | — | 1.3% / 2.8% / 0.7% | 5.1% | 3.7% | 49 | 5.0 |
| `whisper-turbo+ctx+seq+vadlo+echo` | 4.8% | 3.8–6.0% | +0.01 (-0.0 to +0.0) | 1.3% / 2.8% / 0.8% | 5.1% | 3.8% | 49 | 5.0 |
| `whisper-turbo+ctx+seq+vadlo` | 4.9% | 3.8–6.0% | +0.03 (-0.0 to +0.1) | 1.3% / 2.8% / 0.8% | 5.1% | 3.9% | 49 | 5.0 |
| `qwen3-asr-1.7b` | 5.0% | 3.6–6.6% | +0.15 (-0.8 to +1.1) | 2.5% / 1.6% / 0.8% | 4.8% | 5.8% | 49 | 5.0 |
| `whisper-turbo+ctx+seq+novad` | 5.0% | 3.9–6.1% | +0.16 (-0.2 to +0.5) | 1.4% / 2.4% / 1.2% | 5.2% | 4.1% | 49 | 5.0 |
| `whisper-large-v3` | 5.1% | 3.9–6.6% | +0.29 (-0.3 to +1.0) | 1.1% / 3.7% / 0.3% | 5.1% | 5.0% | 49 | 5.0 |
| `whisper-turbo` | 5.1% | 3.8–6.7% | +0.29 (-0.3 to +1.0) | 1.3% / 3.4% / 0.4% | 5.0% | 5.5% | 49 | 5.0 |
| `whisper-turbo+ctx+vadlo` | 5.3% | 3.8–7.1% | +0.45 (-0.2 to +1.3) | 1.2% / 3.6% / 0.5% | 5.5% | 4.3% | 49 | 5.0 |
| `legacy-whisper-cli` | 5.3% | 4.1–6.7% | +0.46 (-0.5 to +1.6) | 1.6% / 1.6% / 2.2% | 5.5% | 4.7% | 49 | 5.0 |
| `parakeet-v3+boost1` | 5.3% | 3.9–7.0% | +0.51 (-0.5 to +1.6) | 1.8% / 2.5% / 1.1% | 5.0% | 6.6% | 49 | 5.0 |
| `whisper-turbo+ctx+seq` | 5.3% | 4.0–6.9% | +0.52 (+0.1 to +1.1) | 1.3% / 3.3% / 0.8% | 5.4% | 5.3% | 49 | 5.0 |
| `parakeet-v3+boost0.5` | 5.4% | 3.9–7.1% | +0.56 (-0.5 to +1.7) | 1.8% / 2.5% / 1.1% | 5.1% | 6.4% | 49 | 5.0 |
| `whisper-turbo+ctxlong` | 5.5% | 3.9–7.5% | +0.65 (-0.1 to +1.8) | 1.1% / 4.0% / 0.4% | 5.5% | 5.6% | 49 | 5.0 |
| `parakeet-v3` | 5.5% | 4.0–7.2% | +0.69 (-0.4 to +1.8) | 1.9% / 2.6% / 1.1% | 5.2% | 6.9% | 49 | 5.0 |
| `qwen3-asr-1.7b+ctx` | 5.5% | 4.0–7.4% | +0.72 (-0.4 to +1.9) | 2.4% / 1.7% / 1.4% | 5.4% | 6.0% | 49 | 5.0 |
| `parakeet-v3+boost0.3f` | 5.6% | 4.1–7.3% | +0.73 (-0.3 to +1.9) | 1.9% / 2.6% / 1.1% | 5.2% | 6.9% | 49 | 5.0 |
| `whisper-turbo+ctx` | 5.8% | 4.1–7.8% | +0.96 (+0.2 to +2.1) | 1.1% / 4.3% / 0.4% | 5.8% | 5.7% | 49 | 5.0 |
| `whisper-turbo+ctx+nsoff` | 5.8% | 4.1–7.8% | +0.96 (+0.2 to +2.1) | 1.1% / 4.3% / 0.4% | 5.8% | 5.7% | 49 | 5.0 |
| `qwen3-asr-1.7b+vad+terms` | 6.1% | 3.4–9.9% | +1.25 (-1.0 to +4.6) | 2.4% / 1.7% / 2.0% | 6.3% | 5.4% | 49 | 5.0 |
| `granite-5.0-2b+terms` | 7.4% | 5.4–9.7% | +2.56 (+1.0 to +4.6) | 1.8% / 4.6% / 1.0% | 8.2% | 4.5% | 49 | 5.0 |
| `granite-5.0-2b` | 7.4% | 5.3–9.8% | +2.58 (+0.8 to +4.7) | 1.9% / 4.6% / 0.9% | 8.2% | 4.3% | 49 | 5.0 |
| `whisper-large-v3+ctx` | 11.0% | 8.3–14.0% | +6.15 (+4.1 to +8.5) | 1.6% / 9.0% / 0.3% | 11.3% | 9.9% | 49 | 5.0 |

## Throughput: running several clips at once

One transcription stream rarely keeps a GPU busy. `asr/throughput.py` measures how much more audio per hour
one GPU gets through when it works on several clips at once: parallel processes (each on its share of the
clips), concurrent requests to one server, or batches inside one model.

- **Throughput** is steady-state (model loading excluded): total audio ÷ the slowest process's decoding time.
- **Archive** is 6,500 h of audio at that throughput on one such GPU; **cost** at Lambda's on-demand price
  (A10 $1.29/h, A100 40 GB $1.99/h).
  Several GPUs divide the time but not the cost.

### Nemotron 3.5 (4-bit GGUF) on an A100

_GPU: NVIDIA A100-SXM4-40GB, $1.99/h._

| Configuration | Processes | Clips | Throughput (× real time) | vs first row | GPU memory peak | GPU busy | Archive | Cost |
|---|---|---|---|---|---|---|---|---|
| 4 requests, A10 settings | 1 | 52 | 142× | 1.0× | 22.0 GB | 94% | 1.9 days | $91 |
| 16 requests | 1 | 52 | 183× | 1.3× | 24.4 GB | 91% | 1.5 days | $71 |
| 16 requests, speculative | 1 | 52 | 215× | 1.5× | 26.0 GB | 90% | 1.3 days | $60 |
| 32 requests, speculative | 1 | 52 | 259× | 1.8× | 29.2 GB | 89% | 1.0 days | $50 |

### Nemotron 3.5 (4-bit GGUF, NeMo-Speech.cpp)

_GPU: NVIDIA A10, $1.29/h._

| Configuration | Processes | Clips | Throughput (× real time) | vs first row | GPU memory peak | GPU busy | Archive | Cost |
|---|---|---|---|---|---|---|---|---|
| 1 request | 1 | 12 | 50× | 1.0× | 21.4 GB | 92% | 5.4 days | $168 |
| 4 requests | 1 | 12 | 85× | 1.7× | 21.7 GB | 91% | 3.2 days | $99 |

### VibeVoice-ASR

_GPU: NVIDIA A10, $1.29/h._

| Configuration | Processes | Clips | Throughput (× real time) | vs first row | GPU memory peak | GPU busy | Archive | Cost |
|---|---|---|---|---|---|---|---|---|
| batch 1 | 1 | 8 | 6× | 1.0× | 17.1 GB | 95% | 45.1 days | $1,398 |
| batch 2 | 1 | 8 | 7× | 1.2× | 18.4 GB | 96% | 38.1 days | $1,181 |
| batch 4 | 1 | 8 | 9× | 1.5× | 20.9 GB | 96% | 30.8 days | $953 |

### Whisper turbo, production setup

_GPU: NVIDIA A10, $1.29/h._

| Configuration | Processes | Clips | Throughput (× real time) | vs first row | GPU memory peak | GPU busy | Archive | Cost |
|---|---|---|---|---|---|---|---|---|
| one stream per process | 1 | 52 | 70× | 1.0× | 2.4 GB | 61% | 3.9 days | $120 |
| one stream per process | 2 | 52 | 87× | 1.3× | 4.7 GB | 87% | 3.1 days | $96 |
| one stream per process | 4 | 52 | 77× | 1.1× | 9.4 GB | 96% | 3.5 days | $108 |
| one stream per process | 6 | 52 | 84× | 1.2× | 14.0 GB | 98% | 3.2 days | $100 |
| one stream per process | 8 | 52 | 79× | 1.1× | 18.5 GB | 97% | 3.4 days | $107 |
| batched 8 | 1 | 52 | 144× | 2.1× | 3.3 GB | 59% | 1.9 days | $58 |
| batched 8 | 2 | 52 | 199× | 2.9× | 6.6 GB | 87% | 1.4 days | $42 |

## Effect of per-talk context

| Base → variant | Misheard terms: base → variant | Non-speech output: base → variant | Disagreement between the two |
|---|---|---|---|
| `granite-5.0-2b` → `granite-5.0-2b+terms` | 13.0% → 10.3% | 7 → 7 clips | 2.3% of words |
| `nemotron-3.5-iq4_nl` → `nemotron-3.5-iq4_nl+terms` | 4.0% → 0.4% | 10 → 10 clips | 1.2% of words |
| `parakeet-ft-v1` → `parakeet-ft-v1+vad90` | 16.3% → 16.6% | 3 → 4 clips | 2.3% of words |
| `parakeet-v3` → `parakeet-v3+boost0.3f` | 14.2% → 13.6% | 4 → 7 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost0.5` | 14.2% → 10.9% | 4 → 5 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost1` | 14.2% → 10.8% | 4 → 5 clips | 1.1% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+ctx` | 2.3% → 2.1% | 74 → 74 clips | 2.6% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+vad` | 2.3% → 2.9% | 74 → 7 clips | 4.0% of words |
| `qwen3-asr-1.7b+vad` → `qwen3-asr-1.7b+vad+terms` | 2.9% → 1.9% | 7 → 7 clips | 2.3% of words |
| `vibevoice-asr` → `vibevoice-asr+terms` | 5.3% → 1.8% | 4 → 3 clips | 13.0% of words |
| `whisper-large-v3` → `whisper-large-v3+ctx` | 8.0% → 2.5% | 7 → 7 clips | 8.1% of words |
| `whisper-turbo` → `whisper-turbo+ctx` | 13.1% → 3.9% | 7 → 7 clips | 2.0% of words |
| `whisper-turbo+ctx` → `whisper-turbo+ctx+nsoff` | 3.9% → 3.9% | 7 → 7 clips | 0.0% of words |
| `whisper-turbo+ctx` → `whisper-turbo+ctx+seq` | 3.9% → 3.9% | 7 → 7 clips | 3.1% of words |
| `whisper-turbo+ctx+seq` → `whisper-turbo+ctx+seq+novad` | 3.9% → 3.2% | 7 → 72 clips | 5.1% of words |
| `whisper-turbo+ctx+seq` → `whisper-turbo+ctx+seq+vadlo` | 3.9% → 3.8% | 7 → 10 clips | 2.8% of words |
| `whisper-turbo+ctx+seq+vadlo` → `whisper-turbo+ctx+seq+vadlo+echo` | 3.8% → 3.8% | 10 → 9 clips | 0.0% of words |
| `whisper-turbo+ctx+seq+vadlo+echo` → `whisper-turbo+ctx+seq+vadlo+echo+hst` | 3.8% → 3.8% | 9 → 7 clips | 0.2% of words |
| `whisper-turbo+ctx` → `whisper-turbo+ctx+vadlo` | 3.9% → 4.3% | 7 → 10 clips | 3.2% of words |
| `whisper-turbo` → `whisper-turbo+ctxlong` | 13.1% → 3.6% | 7 → 7 clips | 1.7% of words |
| `whisper-turbo+ctxlong` → `whisper-turbo+ctxlong+seq+vadlo+echo` | 3.6% → 4.8% | 7 → 10 clips | 3.8% of words |

Disagreement is the word error rate between the two outputs: how much of the text the context changed.

## Most frequent misheard glossary terms

| System | Top known misspellings in its output |
|---|---|
| `legacy-whisper-cli` | Zhao, Yakujo, Shapa, Maizumi, doksan, Daito, Ingo, Huiko, Ongan, Setsho, Zazengi, Wutsu |
| `granite-5.0-2b` | gasho, kohan, Yakujo, doksan, dogan, Genjo, Shugan, Uman, Yastani, Shapa, Ongo, Zenda |
| `granite-5.0-2b+terms` | dogan, Maizumi, kohan, doksan, Yakujo, Shapa, Shugan, Ongo, Zenda, gasho, Genjo |
| `nemotron-3.5-iq4_nl` | Mazumi, Shapa, Huiko, Yunman, Daito, dogan, Shibiyama, Genjo |
| `nemotron-3.5-iq4_nl+terms` | dogan, Daito |
| `parakeet-ft-v1` | dogan, gasho, Yakujo, Secho, Mizumi, Mayakaya Shapa, Shapa, kohan, Orioki, Ingo, Huiko, Ongo |
| `parakeet-ft-v1+vad90` | dogan, gasho, Yakujo, Secho, Mizumi, Mayakaya Shapa, Shapa, kohan, Orioki, Zhao, Ingo, Huiko |
| `parakeet-v3` | gasho, Yakujo, Secho, Mizumi, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, seshin, Orioki |
| `parakeet-v3+boost0.3f` | gasho, Secho, Mizumi, Yakujo, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, Orioki, seshin |
| `parakeet-v3+boost0.5` | gasho, Yakujo, Mizumi, Secho, Mayakaya Shapa, Shapa, doksan, Orioki, Ingo, seshin, Ongo, Zazengi |
| `parakeet-v3+boost1` | gasho, Yakujo, Mizumi, Secho, Mayakaya Shapa, Shapa, doksan, Orioki, Ingo, seshin, Ongo, Zazengi |
| `qwen3-asr-1.7b` | Mazumi, Ongo, seshin, doksan, Zhao, Uman |
| `qwen3-asr-1.7b+ctx` | Shapa, Mazumi, Ongo, doksan, Genjo |
| `qwen3-asr-1.7b+vad` | Shapa, doksan, Uman, Ongo, Doxan, Tikkadhan, Genjo |
| `qwen3-asr-1.7b+vad+terms` | doksan, Dogon, Tikkadhan, Genjo |
| `vibevoice-asr` | doksan, Shapa, Daito, Orioki, Huiko, Sashin, Ongo, Sashen, Zenda, Doxan, Shibiyama, Uman |
| `vibevoice-asr+terms` | Mazumi, Shapa |
| `whisper-large-v3` | Yakujo, Shapa, Maizumi, doksan, Setsho, Huiko, Daito, Ingo, Mayakaya Shapa, Mizumi, Yunmin, Ongo |
| `whisper-large-v3+ctx` | Shapa, Mayakaya Shapa, Setsho, Zenda, Dogon |
| `whisper-turbo` | doksan, Yakujo, Shapa, gasho, Maizumi, Gashow, Setsho, Mayakaya Shapa, Huiko, Daito, Zhao, Ingo |
| `whisper-turbo+ctx` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |
| `whisper-turbo+ctx+nsoff` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |
| `whisper-turbo+ctx+seq` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, Sashin, Zenda, Sazen |
| `whisper-turbo+ctx+seq+novad` | Shapa, Yakujo, Mayakaya Shapa, Setsho, Yastani, Sashin, Sashen, Zenda |
| `whisper-turbo+ctx+seq+vadlo` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |
| `whisper-turbo+ctx+seq+vadlo+echo` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |
| `whisper-turbo+ctx+vadlo` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Dogon's, Zenda, Sazen |
| `whisper-turbo+ctxlong` | Shapa, Yakujo, Mayakaya Shapa, Sashen, Setsho, Yastani, seshin, Zenda |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | Shapa, doksan, Setsho, Yakujo, Mayakaya Shapa, Sashen, Yastani, seshin, Zenda |

## What systems output on non-speech

- `legacy-whisper-cli`: "Thank you."×73; "thank you"×3
- `granite-5.0-2b`: "Señor Presidente,"×2; "Elle est en ligne."×1; "de la mano."×1; "Thank you."×1; "Ah!"×1; "St. John Beens on."×1
- `granite-5.0-2b+terms`: "はい。"×1; "Elle est en ligne."×1; "de la mano."×1; "thank you"×1; "ああ。"×1; "おっ"×1
- `nemotron-3.5-iq4_nl`: "Knock knock knock knock knock knock knock knock knock knock "×1; "Yeah, I think I'm gonna go- go ahead and do that. I'm gonna "×1; "Yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, "×1; "Um, uh, I think I'm gonna go- go ahead and do that."×1; "Kan ze aan, namelijk, eh, het zeeën. Kan ze aan, namelijk, e"×1; "Sentient beings are numberless, I vow to save them. Sentient"×1
- `nemotron-3.5-iq4_nl+terms`: "Knock knock knock knock knock knock knock knock knock knock "×1; "Yeah, I think I'm gonna go- go ahead and do that. I'm gonna "×1; "Yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, yeah, "×1; "The gassho in Daido's zmm dot org. Thank you."×1; "Kansen an, namu, Kannon, Kansen an, namu, mondo. Kansen an, "×1; "Sentient beings are numberless, I vow to save them. Sentient"×1
- `parakeet-ft-v1`: "So that"×1; "Thank you."×1; "Sension be number I to say"×1
- `parakeet-ft-v1+vad90`: "Yeah"×2; "Thank you."×1; "Sent be"×1
- `parakeet-v3`: "So that"×1; "Okay."×1; "Just working on the"×1; "Sension be number two."×1
- `parakeet-v3+boost0.3f`: "So that"×1; "But then you know we do want to write a lot of"×1; "Thank you."×1; "Okay."×1; "Just a little bit."×1; "Sension be number two."×1
- `parakeet-v3+boost0.5`: "So that"×1; "Okay."×1; "Just working on the"×1; "Sension be number two."×1; "No, no, baby."×1
- `parakeet-v3+boost1`: "So that"×1; "Thank you."×1; "Okay."×1; "Just a little bit of a"×1; "Sension be number two."×1
- `qwen3-asr-1.7b`: "The."×24; "Oh."×12; "Okay."×8; "Oh, oh,"×3; "The first thing that you need to do is to get a good underst"×3; "Yeah."×2
- `qwen3-asr-1.7b+ctx`: "This is a dharma talk by John Daido Loori, Daido Roshi, at Z"×54; "This is a dharma talk by Geoffrey Shugen Arnold, Shugen Rosh"×4; "Yeah."×2; "This is a dharma talk by Mark Sando Mininberg at Zen Mountai"×2; "This is a dharma talk by Ron Hogen Green, Hogen Sensei, at Z"×2; "So that being."×1
- `qwen3-asr-1.7b+vad`: "Oh."×2; "Yeah."×2; "Thank you."×1; "Ah."×1; "Sentient beings are."×1
- `qwen3-asr-1.7b+vad+terms`: "Yeah."×2; "Oh."×1; "Thank you."×1; "Ango, Kannon, Shobogenzo, mondo."×1; "Hyakujo, thangka, oryoki, Kannon."×1; "Sanctian beings are."×1
- `vibevoice-asr`: "[Human Sounds] So. Did that be."×1; "[Music][Door] Thank you."×1; "[Music] [Lyric] Kandze ya na [Lyric] Kandze ya na [Lyric] Ka"×1; "[Silence] [Lyric] Saint-Jean-de-Luz en Bresse, à l'heure du "×1
- `vibevoice-asr+terms`: "[Breathing][Cough] So, did that be..."×1; "[Music] Thank you."×1; "[Environmental Sounds] [Lyric] Send your beams on our number"×1
- `whisper-large-v3`: "Thank you."×3; "Yeah."×2; "Yes."×1; "sentient beings are"×1
- `whisper-large-v3+ctx`: "Opening Talk."×2; "Thank you."×2; "Thank you for watching!"×1; "Shobogenzo."×1; "Sentient beings are..."×1
- `whisper-turbo`: "Amen."×2; "Thank you."×2; "Bye."×1; "Yeah."×1; "Sentient beings are"×1
- `whisper-turbo+ctx`: "Thank you."×4; "Amen."×1; "Shobogenzo."×1; "Sentient beings are..."×1
- `whisper-turbo+ctx+nsoff`: "Thank you."×4; "Amen."×1; "Shobogenzo."×1; "Sentient beings are..."×1
- `whisper-turbo+ctx+seq`: "Thank you."×2; "To Be Enlightened by the World"×1; "It's a dharma talk."×1; "Amen."×1; "We'll be talking about Shobogenzo."×1; "Sentient beings of..."×1
- `whisper-turbo+ctx+seq+novad`: "Thank you."×17; "This is a dharma talk."×3; ". . . Thank you."×3; "Thank you very much."×2; "We'll be right back."×2; "Avalokiteshvara."×2
- `whisper-turbo+ctx+seq+vadlo`: "Amen."×2; "Thank you."×2; "Shobogenzo."×2; "2019 Fall Ango Intensive, Part 2 – Versace Speaking ofaption"×1; "Avalokiteshvara.com"×1; "We'll be talking about Shobogenzo."×1
- `whisper-turbo+ctx+seq+vadlo+echo`: "Amen."×2; "Thank you."×2; "Shobogenzo."×2; "Music by T Union"×1; "Avalokiteshvara.com"×1; "Sentient beings are alive."×1
- `whisper-turbo+ctx+seq+vadlo+echo+hst`: "Thank you."×3; "Avalokiteshvara.com"×1; "Amen."×1; "Sentient beings are alive."×1; "Shobogenzo."×1
- `whisper-turbo+ctx+vadlo`: "Thank you."×4; "This is a dharma talk by Geoffrey Shugen Arnold."×1; "Avalokiteshva"×1; "Amen."×1; "Aaaaaaaaaa."×1; "Just..."×1
- `whisper-turbo+ctxlong`: "Thank you."×4; "Amen."×1; "Yeah."×1; "Sentient beings are"×1
- `whisper-turbo+ctxlong+seq+vadlo+echo`: "Amen."×2; "Thank you."×2; "Zazen."×1; "Doshinji, shikantaza, nirvana, nirvana, nirvana, nirvana, ni"×1; "Aaaaaaah"×1; "Just..."×1

## Side-by-side examples

Snippets around a glossary term, aligned to `whisper-large-v3+ctx`. Each starts a few words before the term. Listen to the clip (`data/goldset/clips/<clip>.wav`, at the given offset) to judge which is right.

**dharma** — `30766_s00180` at 1:03 · John Daido Loori · 1980s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called the precept of refraining from |
| `granite-5.0-2b` | third is the precept of refraining from |
| `granite-5.0-2b+terms` | the |
| `nemotron-3.5-iq4_nl` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called the precept of refraining from |
| `nemotron-3.5-iq4_nl+terms` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called the precept of refraining from |
| `parakeet-ft-v1` | nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-ft-v1+vad90` | nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost0.3f` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost0.5` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost1` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `qwen3-asr-1.7b` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `qwen3-asr-1.7b+ctx` | nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `qwen3-asr-1.7b+vad` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `qwen3-asr-1.7b+vad+terms` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `vibevoice-asr` | nature is clear and obvious in the sphere of the unstained Dharma. Not yielding to attachment is called the precept of refraining from |
| `vibevoice-asr+terms` | is clear and obvious in the sphere of the unstained Dharma. Not yielding to attachment is called the precept of refraining from |
| `whisper-large-v3` | -nature is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-large-v3+ctx` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo` | -nature is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctx` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctx+nsoff` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctx+seq` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called a precept of refraining from |
| `whisper-turbo+ctx+seq+novad` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `whisper-turbo+ctx+seq+vadlo` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `whisper-turbo+ctx+seq+vadlo+echo` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `whisper-turbo+ctx+vadlo` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctxlong` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | -nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |

**zendo** — `32995_s00180` at 2:36 · Konrad Ryushin Marchaj · 2010s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | our life. If we were to leave this within the Zenda, that question of what good does it really do, should be on |
| `granite-5.0-2b` | our life. For us to leave this within the zenda, that question of what good does it really do should be on |
| `granite-5.0-2b+terms` | our life for to leave this within the zenda that question of what good does it really do should be on |
| `nemotron-3.5-iq4_nl` | our life. If we were to leave this within the zendo, that question of what good does it really do should be on |
| `nemotron-3.5-iq4_nl+terms` | our life. If we were to leave this within the zendo, that question of what good does it really do should be on |
| `parakeet-ft-v1` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-ft-v1+vad90` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost0.3f` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost0.5` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost1` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `qwen3-asr-1.7b` | our life. For to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+ctx` | our life. For to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+vad` | our life. For us to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+vad+terms` | our life. For us to leave this within the zendo, that question of what good does it really do should be on |
| `vibevoice-asr` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `vibevoice-asr+terms` | our life. If we were to leave this within the zendo, that question of what good does it really do should be on |
| `whisper-large-v3` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-large-v3+ctx` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo` | our life. If we were to leave this within the Zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctx` | our life. If we were to leave this within the zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctx+nsoff` | our life. If we were to leave this within the zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctx+seq` | our life. If we were to leave this within the zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctx+seq+novad` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo+ctx+seq+vadlo` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo+ctx+seq+vadlo+echo` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo+ctx+vadlo` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo+ctxlong` | our life. If we were to leave this within the zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |

**Baizhang Huaihai** — `31268_s00240` at 0:59 · John Daido Loori · 1980s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | was Yakujo, as we talked about in the colon of Yakujo and the fox. And another was Nansen. Basso once said of his |
| `granite-5.0-2b` | was Yakujo, that we talked about in the koan of Yakujo and the fox, and another was Nansen. Basso once said of these |
| `granite-5.0-2b+terms` | was yakujo, that we talked about in the koan of yakujo and the fox, and another was nansen. baso once said of these |
| `nemotron-3.5-iq4_nl` | was Yakuj that we talked about in the Koan with Yakuj and the fox and another was Nansen Baso once said of these |
| `nemotron-3.5-iq4_nl+terms` | was Hyakujo that we talked about in the koan of Hyakujo and the fox and another was Nansen. Baso once said of these |
| `parakeet-ft-v1` | was Yakujo, as we talked about in the cone of Yakujo and the Fox, and another was nonsense. Baso once said of these |
| `parakeet-ft-v1+vad90` | was Yakujo, as we talked about in the cone of Yakujo and the Fox, and another was nonsense. Baso once said of these |
| `parakeet-v3` | was Yakujo, that we talked about in the column of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost0.3f` | was Yakujo, that we talked about in the column of Yakujo and the Fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost0.5` | was Yakujo, that we talked about in the column of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost1` | was Yakujo, that we talked about in the corner of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `qwen3-asr-1.7b` | was Yakujyo, that we talked about, the cone, Yakujyo, and the fox; and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+ctx` | was Hyakujo, that we talked about the cone, Hyakujo, and the fox, and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+vad` | was Yakujyo, that we talked about, the cone of Yakujyo and the fox, and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+vad+terms` | was Hyakujo, that we talked about, the cone of Hyakujo and the fox, and the other was Nansen. Baso once said of these |
| `vibevoice-asr` | was Yakuzo, as we talked about in the colon of Yakuzo and the fox, and another was Nansen. [Silence] Baso once said of these |
| `vibevoice-asr+terms` | was Yakuzo, as we talked about in the koan of Yakuzo and the fox, and another was Nansen. Baso once said of these |
| `whisper-large-v3` | was Yakujo, that we talked about in the calling of Yakujo and the fox. And another was Nansen. Basso once said of these |
| `whisper-large-v3+ctx` | was Hyakujo, that we talked about in the calling of Hyakujo and the fox, and another was Nansen. Basso once said of these |
| `whisper-turbo` | was Yakujo, that we talked about in the colon of Yakujo and the fox. And another was Nansen. Basso once said of these |
| `whisper-turbo+ctx` | was Hyakujo, that we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctx+nsoff` | was Hyakujo, that we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctx+seq` | was Hyakujo, as we talked about in the column of Hyakujo and the Fox, and another was Nansen. And Basa once said of these |
| `whisper-turbo+ctx+seq+novad` | was Hyakujo, as we talked about in the colon of Hyakujo and the fox, and another was Nansen. Mbasa once said of these |
| `whisper-turbo+ctx+seq+vadlo` | was Hyakujo, as we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctx+seq+vadlo+echo` | was Hyakujo, as we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | was Hyakujo, as we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctx+vadlo` | words, Hyakujo, that we talked about in the calling of Hyakujo and the fox. And another was Nansen. Vasa once said of these |
| `whisper-turbo+ctxlong` | was Hyakujo, that we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | was Hyakujo, as we talked about in the koan of Hyakujo and the fox, and another was Nansen. Baso once said of these |

**densho** — `33528_s01214` at 2:09 · John Daido Loori · 1990s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | is communication. It's what it is. You know, the bell rings, the dencho rings. It's time to go to the Buddha Hall for |
| `granite-5.0-2b` | It's communication. It's what it is. The bell rings, the dencho rings. It's time to go to the Buddha hall for |
| `granite-5.0-2b+terms` | it's communication. it's what it is. you know, the bell rings, the dencho rings. it's time to go to the buddha hall for |
| `nemotron-3.5-iq4_nl` | it's communication is what it is you know the bell rings the the densho rings it's time to go to the Buddha hall for |
| `nemotron-3.5-iq4_nl+terms` | it's communication is what it is you know the bell rings the the densho rings it's time to go to the buddha hall for |
| `parakeet-ft-v1` | it's communication is what it is you know the bell rings the dentro rings it's time to go to the Buddha hall for |
| `parakeet-ft-v1+vad90` | it's communication is what it is. You know the bell rings the dent show rings it's time to go to the Buddha hall for |
| `parakeet-v3` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost0.3f` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost0.5` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost1` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `qwen3-asr-1.7b` | It's communication. It's what it is. You know, the bell rings, the dento rings. It's time to go to the Buddha hall for |
| `qwen3-asr-1.7b+ctx` | It's communication. It's what it is. You know, the bell rings, the dento rings. It's time to go to the Buddha hall for |
| `qwen3-asr-1.7b+vad` | It's communication. It's what it is. You know, the bell rings. The bell rings. It's time to go to the Buddha Hall for |
| `qwen3-asr-1.7b+vad+terms` | It's communication. It's what it is. You know, the bell rings. The bell rings. It's time to go to the Buddha Hall for |
| `vibevoice-asr` | is communication, is what it is. You know, the bell rings, the denco rings, it's time to go to the Buddha hall for |
| `vibevoice-asr+terms` | it's communication, is what it is. You know, the bell rings, the dento rings, it's time to go to the Buddha hall for |
| `whisper-large-v3` | is communication, is what it is. You know, the bell rings, the denture rings, it's time to go to the Buddha Hall for |
| `whisper-large-v3+ctx` | It's communication, it's what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo` | is communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha hall for |
| `whisper-turbo+ctx` | is communication, is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+nsoff` | is communication, is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+seq` | It's communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+seq+novad` | is communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+seq+vadlo` | It's communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+seq+vadlo+echo` | It's communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | It's communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctx+vadlo` | is communication is what it is. You know, the bell rings, the dencho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctxlong` | is communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | it's communication is what it is, you know, the bell rings, the dencho rings, it's time to go to the Buddha Hall for |

**Zhaozhou Congshen** — `34803_s00570` at 4:05 · Geoffrey Shugen Arnold · 2020s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | What was her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could, from one perspective, say, is a great master. |
| `granite-5.0-2b` | What was her power? She was a tea woman offering refreshment to travelers. Jaojo, you could from one perspective say, is a great master. |
| `granite-5.0-2b+terms` | what was her power she was a tea woman offering refreshment to travelers zhaozhou, you could from one perspective say, is a great master, |
| `nemotron-3.5-iq4_nl` | what was her power? She's a tea woman offering refreshment to travelers. Zhaozhou you could from one perspective say is a great master |
| `nemotron-3.5-iq4_nl+terms` | what was her power. She's a tea woman offering refreshment to travelers. Zhaozhou you could from one perspective say is a great master |
| `parakeet-ft-v1` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master. |
| `parakeet-ft-v1+vad90` | What was her power? She's a T woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master. |
| `parakeet-v3+boost0.3f` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3+boost0.5` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3+boost1` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, |
| `qwen3-asr-1.7b` | What was her power? She's a tea woman offering refreshment to travelers. Zhao, you could, from one perspective, say, is a great master. |
| `qwen3-asr-1.7b+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master, |
| `qwen3-asr-1.7b+vad` | What was her power? She's a tea woman offering refreshment to travelers. Jangjo, you could, from one perspective, say is a great master, |
| `qwen3-asr-1.7b+vad+terms` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say is a great master, |
| `vibevoice-asr` | What was her power? She was a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `vibevoice-asr+terms` | What was her power? She's a tea woman, offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master. |
| `whisper-large-v3` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-large-v3+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-turbo` | What was her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could from one perspective say, is a great master. |
| `whisper-turbo+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-turbo+ctx+nsoff` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-turbo+ctx+seq` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, |
| `whisper-turbo+ctx+seq+novad` | What was her power? She's a tea woman, offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, |
| `whisper-turbo+ctx+seq+vadlo` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master. |
| `whisper-turbo+ctx+seq+vadlo+echo` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master. |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master. |
| `whisper-turbo+ctx+vadlo` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, |
| `whisper-turbo+ctxlong` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |

**Yantou Quanhuo** — `34004_s01972` at 1:08 · Other · 1990s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | shift together. You were sweeping under the pizza oven and you swept down a little critter and it was caught in flypaper and you ran over in a panic. I don't know if it's dead or alive. There's something in the flypaper. What's the constant principle of that? May your life go well. Attention. First, I want to let you know I've never done this before so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of matter. If you do not agree, then you're forever sunk in |
| `granite-5.0-2b` | I'm actually feeling kind of nervous. As far as the last line of the call, if you agree, then you're still attached to |
| `granite-5.0-2b+terms` | i'm actually feeling kind of nervous as far as the last line of the call if you agree then you're still attached to |
| `nemotron-3.5-iq4_nl` | together and you were sweeping under the pizza oven and you swept out a little critter that was caught in fly paper and you ran over in a panic. I don't know if it's dead or alive, there's there's something in the fly paper. What's the constant principle of that? May your life go well. Attention. First I want to let you know I've never done this before so I'm actually being kind of nervous. As far as the last line of the koan, if one if you agree then you are still attached to |
| `nemotron-3.5-iq4_nl+terms` | together and you were sweeping under the pizza oven and you swept out a little critter that was caught in fly paper and you ran over in a panic. I don't know if it's dead or alive, there's there's something in the fly paper. What's the constant principle of that? May your life go well. Attention. First I want to let you know I've never done this before so I'm actually being kind of nervous. As far as the last line of the koan, if one if you agree then you are still attached to |
| `parakeet-ft-v1` | together and you were sweeping under the pizza oven and you swept down a little critter that was caught in fly paper and you ran over in a panic uh |
| `parakeet-ft-v1+vad90` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was hot in fly paper and you ran over in a panic. Uh I don't know if it's dead or live. There's there's something in the fly paper. What's the constant principle for that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous about this. As far as the last line of the call on it, if you agree, then you're still attached to sense of matter. If you do not agree, then you're forever sunk in |
| `parakeet-v3` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran it over in a panic. |
| `parakeet-v3+boost0.3f` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, then you're still attached to |
| `parakeet-v3+boost0.5` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, then you're still attached to |
| `parakeet-v3+boost1` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. Uh I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the call on it, if you agree, then you're still attached to |
| `qwen3-asr-1.7b` | shift together, you were sweeping under the pizza oven and you swept out little critters. Caught in the flypaper, and you ran over a pan. I don't think there's a lot. There's there's something in the flypaper. What's the constant principle? That. May your life go well. Attention. So I want to let you know I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you agree, then you're still a |
| `qwen3-asr-1.7b+ctx` | shift together. You were sweeping under the pizza oven and you swept out little critters. Caught in the fly paper. You ran over a pan. I don't think there's a lot. There's there's something in the fly paper. What's the constant principle? That. May your life go well. Attention. Just so I let you know, I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you agree that you're still a |
| `qwen3-asr-1.7b+vad` | shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm nervous. As far as the last line |
| `qwen3-asr-1.7b+vad+terms` | shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm not nervous. As far as the last line |
| `vibevoice-asr` | shift together. We were sweeping under the pizza oven and you swept down a little critter that was caught in flypaper and you ran it over with a paddle. Uh, I don't know if it's dead or alive or |
| `vibevoice-asr+terms` | shift together. We were sweeping under the pizza oven, and you swept down a little critter that was caught in flypaper, and you ran it over with a paddle. I don't know if it's dead or alive or |
| `whisper-large-v3` | koan, if you agree, then you're still attached to the sense of matter. If you do not agree... Then you're forever sunk in |
| `whisper-large-v3+ctx` | John Daido Loori, Bernie Glassman, Tokusan, Zen Peacemaker Order, and Ganto. We'll be talking about John Daido Loori, Bernie Glassman, Tokusan, Zen Peacemaker |
| `whisper-turbo` | koan, if you agree, then you're still attached to the sense of manner. If you do not agree... Then you're forever sunk in |
| `whisper-turbo+ctx` | As far as the last line of the koan, if you agree, then you're still attached to the sentiment. If you do not |
| `whisper-turbo+ctx+nsoff` | As far as the last line of the koan, if you agree, then you're still attached to the sentiment. If you do not |
| `whisper-turbo+ctx+seq` | shift together. You were sweeping under the pizza oven, and you swept down a little critter that was caught in flypaper, and you ran over in a panic. I don't know if it's dead or alive, there's something in the flypaper. What's the constant principle of that? May your life go well. Attention. Chris, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of matter. If you do not agree, then you're forever sunk in |
| `whisper-turbo+ctx+seq+novad` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in flypaper, and you ran over in a panic. I don't know if it's dead or alive, there's something in the flypaper. What's the constant principle of that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attentive to the sense of manner. If you do not agree, then you're forever sunk in |
| `whisper-turbo+ctx+seq+vadlo` | you agree, then you are still attached to the sense of matter. If you do not agree, then you are forever sunk in |
| `whisper-turbo+ctx+seq+vadlo+echo` | you agree, then you are still attached to the sense of matter. If you do not agree, then you are forever sunk in |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | you agree, then you are still attached to the sense of matter. If you do not agree, then you are forever sunk in |
| `whisper-turbo+ctx+vadlo` | together and you were sweeping under the pizza oven and you swept down a little critter that was caught in flypaper and you ran over in a panic. |
| `whisper-turbo+ctxlong` | as the last line of the koan, if you agree, then you're still attached to the sense of manner. If you do not |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | koan, if you agree, then you're still attached to the sense of matter. If you do not agree, then you're forever sunk in |

**Shariputra** — `30671_b01435` at 4:12 · John Daido Loori · 1980s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | the brain works linearly and sequentially and we grasp things dualistically relatively our whole definition of the universe is based on that relativity everything is known in reference to something else it's one big reference system i remember when i began to realize that in science i mean i used to think of science for 17 years that was my field science it was my god and then i realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `granite-5.0-2b` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science for 17 years, that was my field, science, it was my god. And then I realized one day, the whole thing just back and forth referring to different reference systems. What's the absolute basis of |
| `granite-5.0-2b+terms` | the brain works linearly and sequentially and we grasp things dualistically relatively our whole definition of the universe is based on that relativity everything is known in reference to something else it's one big reference system i remember when i began to realize that in science i mean i used to think that science for 17 years that was my field science that was my god and then i realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `nemotron-3.5-iq4_nl` | the brain works linearly and sequentially. And we grasp things dualistically. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science, for seventeen years, that was my field, science, it was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `nemotron-3.5-iq4_nl+terms` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science, for seventeen years, that was my field, science, it was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `parakeet-ft-v1` | the brain works linearly and sequentially and we grasp things dualistically relatively our whole definition of the universe is based on that relativity everything is known in reference to something else it's one big reference system I remember when I began to realize that in science I mean I used to think of science for 17 years that was my field science it was my God and then I realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `parakeet-ft-v1+vad90` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean I used to think of science for 17 years that was my field science it was my God and then I realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `parakeet-v3` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost0.3f` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost0.5` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost1` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think it's science for seventeen years. That was my field, science. It was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+ctx` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think it's science for 17 years. That was my field, science. It was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+vad` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that science. I mean, I used to think that science, for 17 years, that was my field, science, that was my guide. And then I realized one day, the whole thing is just back and forth, referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+vad+terms` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science, for 17 years, that was my field, science, that was my guide. And then I realized one day, the whole thing is just back and forth, referring to different reference systems. What's the absolute basis of |
| `vibevoice-asr` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. [Silence] Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. [Silence] I remember when I began to realize that in science. I mean, I used to think that science, for seventeen years, that was my field, science. It was my god. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `vibevoice-asr+terms` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science, for seventeen years, that was my field, science. It was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `whisper-large-v3` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science for 17 years, that was my field, science. It was my God. And then I realized one day, the whole thing just... back and forth referring to different reference systems what's the absolute basis of |
| `whisper-large-v3+ctx` | the brain works linearly and sequentially. Avalokitesvara, jukai, Eno, and Shariputra. Back and forth, referring to different references. What's the absolute basis of |
| `whisper-turbo` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day the whole thing just... back and forth referring to different reference systems what's the absolute basis of |
| `whisper-turbo+ctx` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my god. And then I realized one day the whole thing just... Back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+nsoff` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my god. And then I realized one day the whole thing just... Back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+seq` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+seq+novad` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That It was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+seq+vadlo` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science. For 17 years, that was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+seq+vadlo+echo` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science. For 17 years, that was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science. For 17 years, that was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctx+vadlo` | the brain works linearly and sequentially. And we grasp things dualistically. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctxlong` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my god. And then I realized one day the whole thing just... Back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing, just back and forth, referring to different reference systems. What's the absolute basis of |

**Shakyamuni** — `36533_s00180` at 2:25 · John Daido Loori · 2000s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | Dogen says let us offer flowers of the distant mountains to the Tathagatha or share the treasures with all sentient beings and spiritual things as well as material things when the way is surrendered to the way you attain the way upon being awakened you necessarily let the way come through itself the self the self gives the self for the sake of giving the self the other gives the other for the sake of giving |
| `granite-5.0-2b` | Dogen says, let us offer flowers of the distant mountains to the Tathagata or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `granite-5.0-2b+terms` | dogan says, let us offer flowers of the distant mountains to the tathagata or share the treasures with all sentient beings, and spiritual things as well as material things. when the way is surrendered to the way, you attain the way. upon being awakened, you necessarily let the way come through itself. the self gives the self for the sake of giving the self. the other gives the other for the sake of giving |
| `nemotron-3.5-iq4_nl` | Dogen says, let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `nemotron-3.5-iq4_nl+terms` | Dogen says, let us offer flowers of the distant mountains to the tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-ft-v1` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-ft-v1+vad90` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost0.3f` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost0.5` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost1` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+ctx` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+vad` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+vad+terms` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `vibevoice-asr` | Dogen says let us offer flowers of the distant fountains to the Tathagata, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `vibevoice-asr+terms` | Dogen says, let us offer flowers of the distant mountains to the tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-large-v3` | Dogen says, let us offer flowers of the distant mountains to the Tathagata. or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-large-v3+ctx` | Dogen says, let us offer flowers of the distant mountains to the tathagata. The other gives the other for the sake of giving |
| `whisper-turbo` | Dogen says let us offer flowers of the distant mountains to the Tathagatha or share the treasures with all sentient beings in spiritual things as well as material things when the way is surrendered to the way you attain the way upon being awakened you necessarily let the way come through itself the self gives the self for the sake of giving the self the other gives the other for the sake of giving |
| `whisper-turbo+ctx` | Dogen says let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+nsoff` | Dogen says let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+seq` | Dogen says let us offer flowers of the distant mountains to the tathagata or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way you attain the way. Upon being awakened you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+seq+novad` | Dogen says, let us offer flowers of the distant mountains to the tathagata or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+seq+vadlo` | Dogen says, let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings. In spiritual things as well as material things. When the Way is surrendered to the Way, you attain the Way. Upon being awakened, you necessarily let the Way come through itself. The Self gives the Self for the sake of giving the Self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+seq+vadlo+echo` | Dogen says, let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings. In spiritual things as well as material things. When the Way is surrendered to the Way, you attain the Way. Upon being awakened, you necessarily let the Way come through itself. The Self gives the Self for the sake of giving the Self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | Dogen says, let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings. In spiritual things as well as material things. When the Way is surrendered to the Way, you attain the Way. Upon being awakened, you necessarily let the Way come through itself. The Self gives the Self for the sake of giving the Self. The other gives the other for the sake of giving |
| `whisper-turbo+ctx+vadlo` | Dogen says, let us offer flowers of the distant mountains to the tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the Way is surrendered to the Way, you attain the Way. Upon being awakened, you necessarily let the Way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctxlong` | Dogen says, let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | Dogen says let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings. In spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |

**gassho** — `35549_s00390` at 3:01 · Bonnie Myotai Treace · 1990s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | experience. Have you experienced that? Have you experienced acting on the world? Gatha not. Anybody? Ever entered a situation, a moment, a relationship? |
| `granite-5.0-2b` | experience. Have you experienced that? Have you experienced acting on the world, gasho not? Anybody? Ever entered a situation, a moment, a relationship? |
| `granite-5.0-2b+terms` | experience. have you experienced that? have you experienced acting on the world, gassho not? anybody ever entered a situation, a moment, a relationship? |
| `nemotron-3.5-iq4_nl` | experience have you experienced that Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship? |
| `nemotron-3.5-iq4_nl+terms` | experience. Have you experienced that? Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-ft-v1` | experience? Have you experienced that? Have you experienced acting on the world? Gasho not anybody ever entered a situation, a moment, a relationship? |
| `parakeet-ft-v1+vad90` | experience. Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-v3` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost0.3f` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost0.5` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost1` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `qwen3-asr-1.7b` | experience. Have you experienced that? Have you experienced acting on the world, ghasho not? Anybody ever enter a situation, a moment of relationship? |
| `qwen3-asr-1.7b+ctx` | experience. Have you experienced that? Have you experienced acting on the world gassho not? Anybody ever enter a situation, a moment, a relationship? |
| `qwen3-asr-1.7b+vad` | experience. Have you experienced that? Have you experienced acting on the world? Ghasho not. Anybody ever entered a situation, a moment, a relationship? |
| `qwen3-asr-1.7b+vad+terms` | experience. Have you experienced that? Have you experienced acting on the world? Gassho not. Anybody ever entered a situation, a moment, a relationship? |
| `vibevoice-asr` | experience. Have you experienced that? Have you experienced acting on the world? Gosh, no, not. Anybody ever entered a situation, a moment, a relationship? |
| `vibevoice-asr+terms` | experience. Have you experienced that? Have you experienced acting on the world? Gassho, not. Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-large-v3` | experience have you experienced that have you experienced acting on the world gassho not anybody Ever entered a situation, a moment, a relationship? |
| `whisper-large-v3+ctx` | experience. Have you experienced that? Have you experienced acting on the world? Gassho not. Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo` | experience have you experienced that have you experienced acting on the world gacho not anybody Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx` | experience. Have you experienced that? Have you experienced acting on the world, gassho, not? Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx+nsoff` | experience. Have you experienced that? Have you experienced acting on the world, gassho, not? Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx+seq` | Have you experienced that? Have you experienced acting on the world? Gassho not. Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx+seq+novad` | experience. Have you experienced that? Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx+seq+vadlo` | experience. Have you experienced that? Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship. |
| `whisper-turbo+ctx+seq+vadlo+echo` | experience. Have you experienced that? Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship. |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | experience. Have you experienced that? Have you experienced acting on the world, gassho not? Anybody? Ever entered a situation, a moment, a relationship. |
| `whisper-turbo+ctx+vadlo` | experience. Have you experienced that? Have you experienced acting on the world, gassho, not? Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctxlong` | experience. Have you experienced that? Have you experienced acting on the world, gassho, not? Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | experience. Have you experienced that? Have you experienced acting on the world? Gassho, not. Anybody? Ever entered a situation, a moment, a relationship? |

**sangha** — `34736_s02010` at 1:44 · Ron Hogen Green · 2020s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `granite-5.0-2b` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `granite-5.0-2b+terms` | buddha i take refuge in the dharma i take refuge in the sangha i take refuge in the buddha the incomparably honored one |
| `nemotron-3.5-iq4_nl` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `nemotron-3.5-iq4_nl+terms` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-ft-v1` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-ft-v1+vad90` | Buddha I take refuge in the Dharma I take refuge in the Sangha I take refuge in the Buddha the incomparably honored one |
| `parakeet-v3` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost0.3f` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost0.5` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost1` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b+ctx` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b+vad` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparable honored one. |
| `qwen3-asr-1.7b+vad+terms` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparable honored one. |
| `vibevoice-asr` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `vibevoice-asr+terms` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-large-v3` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. |
| `whisper-large-v3+ctx` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx` | Buddha. I take refuge in the Dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+nsoff` | Buddha. I take refuge in the Dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+seq` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+seq+novad` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+seq+vadlo` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+seq+vadlo+echo` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx+vadlo` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctxlong` | Buddha. I take refuge in the Dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |

**ango** — `34775_s01976` at 3:04 · Jody Hojin Kimmel · 2020s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | of all my fear and all of my you know like no way and so and I keep coming too I walk in the door for session I feel like I'm getting an infusion like I need an infusion and and so and every session you know I'll be sitting and I don't |
| `granite-5.0-2b` | need an infusion. And so and every session, you know, I'll be sitting and I don't sit well. It's not about my head. |
| `granite-5.0-2b+terms` | and i don't sit well and it's not about my head |
| `nemotron-3.5-iq4_nl` | of all my fear and all of my, you know, I like, no way. Um, and so, um, and, and I keep coming too, I, I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And, um, and so, and every session, you know, I'll be sitting and, and I don't |
| `nemotron-3.5-iq4_nl+terms` | of all my fear and all of my, you know, I like, no way. Um. And so, um, and, and I keep coming too, I, I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And, um, and so, and every session, you know, I'll be sitting and, and I don't |
| `parakeet-ft-v1` | of all my fear and all of my you know I like no way um and so um and and I keep coming too I I I walk in the door for session I feel like I'm getting an infusion like I need an infusion and um and so and every session you know I'll I'll be sitting and and I don't |
| `parakeet-ft-v1+vad90` | of all my fear and all of my you know I like no way um and so um and and I keep coming too I I I walk in the door for session I feel like I'm getting an infusion like I need an infusion and um and so and every session you know I'll I'll be sitting and and I don't |
| `parakeet-v3` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too, I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost0.3f` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too. I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost0.5` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too. I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost1` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too, I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `qwen3-asr-1.7b` | of all my fear and all of my, you know, like no way. And so, and and I keep coming too. I I walk in the door for session. I feel like I'm getting an infusion. Like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+ctx` | of all my fear and all of my, you know, like no way. And so, and and I keep coming too. I I walk in the door for session. I feel like I'm getting an infusion. Like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+vad` | of all my fear and all of my, you know, I like no way. And so, and and I keep coming to. I I walk in the door for session. I feel like I'm getting infusion, like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+vad+terms` | of all my fear and all of my, you know, I like no way. And so, and and I keep coming to. I I walk in the door for session. I feel like I'm getting infusion, like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `vibevoice-asr` | of all my fear and all of my, you know, I, like, no way. Um, and so, um, and, and I keep coming, too. I, I, I walk in the door for a session. I feel like I'm getting an infusion, like I need an infusion. And, um, and so, and every session, you know, I'll be sitting and, and I don't |
| `vibevoice-asr+terms` | of all my fear and all of my, you know, I, like, no way. Um, and so, um, and, and I keep coming, too. I, I, I walk in the door for a session. I feel like I'm getting an infusion, like I need an infusion. And, um, and so, and every session, you know, I'll be sitting and, and I don't |
| `whisper-large-v3` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for session. I feel like I'm getting an infusion, like I need an infusion. And so, and every session, you know, I'll be sitting, and I don't |
| `whisper-large-v3+ctx` | of all my fear and all of my We'll be talking about ango, Sozan, and zmm .org. We'll be talking about ango, Sozan, |
| `whisper-turbo` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for session. I feel like I'm getting an infusion, like I need an infusion. And so, and every session, you know, I'll be sitting, and I don't |
| `whisper-turbo+ctx` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And so, and every Sashen, you know, I'll be sitting and I don't |
| `whisper-turbo+ctx+nsoff` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And so, and every Sashen, you know, I'll be sitting and I don't |
| `whisper-turbo+ctx+seq` | of all my fear and all of my, you know, like, no way. And so, and I keep coming to, I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And so, and every Sashen, you know, I'll be sitting and I don't |
| `whisper-turbo+ctx+seq+novad` | of all my fear and all of my, you know, like, no way. And so, and I keep coming to, I walk in the door for Sashen, I feel like I'm getting an infusion, like I I need an infusion. |
| `whisper-turbo+ctx+seq+vadlo` | of all my fear and all of my, you know, like, no way. And I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And every Sashen, I'll be sitting, and I don't sit well, it's not |
| `whisper-turbo+ctx+seq+vadlo+echo` | of all my fear and all of my, you know, like, no way. And I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And every Sashen, I'll be sitting, and I don't sit well, it's not |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | of all my fear and all of my, you know, like, no way. And I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And every Sashen, I'll be sitting, and I don't sit well, it's not |
| `whisper-turbo+ctx+vadlo` | of all my fear and all of my, you know, like no way. And I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And every Sashen, I'll be sitting, and I don't sit well. It's not |
| `whisper-turbo+ctxlong` | of all my fear and all of my... You know, like, no way. And so, and I keep coming too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And so, and every Sashen, you know, I'll be sitting and I don't |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | of all my fear and all of my, you know, like no way. And I keep coming, too. I walk in the door for Sashen. I feel like I'm getting an infusion, like I need an infusion. And every Sashen, I'll be sitting, and I don't sit well. It's not |

**karma** — `33782_s02428` at 5:54 · Ron Hogen Green · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | to. Um, and that's our responsibility. And there's a karma from that. |
| `granite-5.0-2b` | to. And that's our responsibility. And there's a karma for that. And karma came out of all of those things. |
| `granite-5.0-2b+terms` | to. and that's our responsibility. and there's a karma for that. and karma came out of all of those things. |
| `nemotron-3.5-iq4_nl` | to. Um and that's our responsibility. And there's a karma from that. And a karma came out of all of those things. |
| `nemotron-3.5-iq4_nl+terms` | to um and that's our responsibility and there's a karma for that and a karma came out of all of those things |
| `parakeet-ft-v1` | to. Um And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-ft-v1+vad90` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3` | to. Um and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost0.3f` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost0.5` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost1` | to. Um and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `qwen3-asr-1.7b` | to, and that's our responsibility. And there's a karma for that, and a karma came out of all of those things. |
| `qwen3-asr-1.7b+ctx` | to, and that's our responsibility. And there's a karma for that, and a karma came out of all of those things. |
| `qwen3-asr-1.7b+vad` | to, and that's our responsibility. And there's a karma for that, and karma came out of all of those things. |
| `qwen3-asr-1.7b+vad+terms` | to, and that's our responsibility. And there's a karma for that, and karma came out of all of those things. |
| `vibevoice-asr` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `vibevoice-asr+terms` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-large-v3` | to. And that's our responsibility. And there's a karma from that. Karma came out of all of those things. |
| `whisper-large-v3+ctx` | to. And that's our responsibility. And there's a karma from that. Karma came out of all of those things. |
| `whisper-turbo` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |
| `whisper-turbo+ctx` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |
| `whisper-turbo+ctx+nsoff` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |
| `whisper-turbo+ctx+seq` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctx+seq+novad` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctx+seq+vadlo` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctx+seq+vadlo+echo` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctx+vadlo` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `whisper-turbo+ctxlong` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |

**Konrad Ryushin Marchaj** — `29973_s00810` at 4:32 · Konrad Ryushin Marchaj · 2010s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | through and expose the fallacy of all the laws of nature. As you can sense I was mentioning yesterday, every koan in a sense is |
| `granite-5.0-2b` | through and expose the fallacy of all the laws of nature. The Shugan sense I was mentioning yesterday, every kohan in a sense is |
| `granite-5.0-2b+terms` | through and expose the fallacy of all the laws of nature. the shugan sense i was mentioning yesterday, every kuan in a sense is |
| `nemotron-3.5-iq4_nl` | through and expose the fallacy of all the laws of nature. The Shubinsensei was mentioning yesterday every koan in a sense is |
| `nemotron-3.5-iq4_nl+terms` | through and expose the fallacy of all the laws of nature. The Shubinsensei was mentioning yesterday every koan in a sense is |
| `parakeet-ft-v1` | through and expose the fallacy of all the laws of nature. Mr. Vincenzo was mentioning yesterday, every koan in a sense is |
| `parakeet-ft-v1+vad90` | through and expose the fallacy of all the laws of nature. Mr. Vincenzo was mentioning yesterday, every koan in a sense is |
| `parakeet-v3` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost0.3f` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost0.5` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost1` | through and expose the fallacy of all the laws of nature. |
| `qwen3-asr-1.7b` | through and expose the fallacy of all the laws of nature. This reminds me, I was mentioning yesterday, every koan in a sense is |
| `qwen3-asr-1.7b+ctx` | through and expose the fallacy of all the laws of nature. The Shoben Sensei was mentioning yesterday. Every koan, in a sense, is |
| `qwen3-asr-1.7b+vad` | through and expose the falsity of all the laws of nature. The Sri Venanda was mentioning yesterday every koan in a sense is |
| `qwen3-asr-1.7b+vad+terms` | through and expose the falsity of all the laws of nature. The Shubhendra was mentioning yesterday every koan in a sense is |
| `vibevoice-asr` | through and expose the fallacy of all the laws of nature. As Shugen Senso was mentioning yesterday, every koan, in a sense, is |
| `vibevoice-asr+terms` | through and expose the fallacy of all the laws of nature. As Shugen-sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-large-v3` | through and expose the fallacy of all the laws of nature. As Ruben Sanza was mentioning yesterday, every koan, in a sense, is |
| `whisper-large-v3+ctx` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo` | through and expose the fallacy of all the laws of nature. As you can sense, I was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+nsoff` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+seq` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+seq+novad` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+seq+vadlo` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+seq+vadlo+echo` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx+vadlo` | through and expose. The fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctxlong` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |

**tathata** — `32903_s00720` at 0:06 · Vanessa Zuisei Goddard · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | we don't, we don't believe that we are a person of suchness as Dogen says. And because we don't believe it as a |
| `granite-5.0-2b` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `granite-5.0-2b+terms` | we don't. we don't believe that we are a person of suchness, as dogan says. and because we don't believe it, as a |
| `nemotron-3.5-iq4_nl` | we don't, we don't believe that we are a person of suchness as as Dogen says. And because we don't believe it, as a |
| `nemotron-3.5-iq4_nl+terms` | we don't, we don't believe that we are a person of suchness as as dokusan says. And because we don't believe it, as a |
| `parakeet-ft-v1` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `parakeet-ft-v1+vad90` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `parakeet-v3` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `parakeet-v3+boost0.3f` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `parakeet-v3+boost0.5` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `parakeet-v3+boost1` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `qwen3-asr-1.7b` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `qwen3-asr-1.7b+ctx` | we don't we don't believe that we are a person of suchness as Dogen says. And because we don't believe it, as a |
| `qwen3-asr-1.7b+vad` | we don't. We don't believe that we are a person of suchness as Dogen says. And because we don't believe it, as a |
| `qwen3-asr-1.7b+vad+terms` | we don't we don't believe that we are a person of suchness as Dogen says. And because we don't believe it, as a |
| `vibevoice-asr` | we don't, we don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `vibevoice-asr+terms` | we don't, we don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-large-v3` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-large-v3+ctx` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+nsoff` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+seq` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+seq+novad` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+seq+vadlo` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+seq+vadlo+echo` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctx+vadlo` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctxlong` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | we don't. We don't believe that we are a person of suchness, as Dogen says. And because we don't believe it, as a |

## Agreement between systems

Word error rate of each row's output measured against each column's output, on speech clips. Systems that agree closely are making the same choices, not necessarily the right ones.

| | `legacy-whisper-cli` | `granite-5.0-2b` | `granite-5.0-2b+terms` | `nemotron-3.5-iq4_nl` | `nemotron-3.5-iq4_nl+terms` | `parakeet-ft-v1` | `parakeet-ft-v1+vad90` | `parakeet-v3` | `parakeet-v3+boost0.3f` | `parakeet-v3+boost0.5` | `parakeet-v3+boost1` | `qwen3-asr-1.7b` | `qwen3-asr-1.7b+ctx` | `qwen3-asr-1.7b+vad` | `qwen3-asr-1.7b+vad+terms` | `vibevoice-asr` | `vibevoice-asr+terms` | `whisper-large-v3` | `whisper-large-v3+ctx` | `whisper-turbo` | `whisper-turbo+ctx` | `whisper-turbo+ctx+nsoff` | `whisper-turbo+ctx+seq` | `whisper-turbo+ctx+seq+novad` | `whisper-turbo+ctx+seq+vadlo` | `whisper-turbo+ctx+seq+vadlo+echo` | `whisper-turbo+ctx+seq+vadlo+echo+hst` | `whisper-turbo+ctx+vadlo` | `whisper-turbo+ctxlong` | `whisper-turbo+ctxlong+seq+vadlo+echo` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | · | 10% | 10% | 6% | 7% | 7% | 6% | 9% | 9% | 8% | 8% | 9% | 9% | 9% | 10% | 12% | 16% | 7% | 15% | 7% | 8% | 8% | 8% | 7% | 7% | 7% | 7% | 8% | 8% | 7% |
| `granite-5.0-2b` | 10% | · | 2% | 8% | 8% | 9% | 8% | 10% | 10% | 10% | 10% | 10% | 11% | 9% | 11% | 14% | 18% | 8% | 15% | 8% | 9% | 9% | 8% | 9% | 8% | 8% | 8% | 8% | 9% | 8% |
| `granite-5.0-2b+terms` | 10% | 2% | · | 8% | 8% | 9% | 8% | 10% | 10% | 10% | 10% | 10% | 11% | 10% | 11% | 14% | 18% | 8% | 15% | 8% | 9% | 9% | 9% | 9% | 8% | 8% | 8% | 8% | 9% | 8% |
| `nemotron-3.5-iq4_nl` | 6% | 9% | 9% | · | 1% | 5% | 4% | 7% | 7% | 6% | 6% | 6% | 6% | 6% | 7% | 10% | 14% | 6% | 14% | 7% | 8% | 8% | 7% | 6% | 6% | 6% | 6% | 7% | 7% | 6% |
| `nemotron-3.5-iq4_nl+terms` | 7% | 9% | 9% | 1% | · | 5% | 4% | 7% | 7% | 6% | 6% | 6% | 6% | 6% | 7% | 10% | 14% | 6% | 14% | 7% | 8% | 8% | 7% | 6% | 6% | 6% | 6% | 7% | 7% | 6% |
| `parakeet-ft-v1` | 7% | 9% | 9% | 5% | 5% | · | 2% | 4% | 4% | 4% | 4% | 7% | 7% | 6% | 7% | 10% | 15% | 7% | 14% | 7% | 8% | 8% | 7% | 7% | 6% | 6% | 6% | 7% | 7% | 6% |
| `parakeet-ft-v1+vad90` | 7% | 9% | 9% | 4% | 4% | 2% | · | 5% | 5% | 5% | 5% | 6% | 7% | 6% | 7% | 10% | 15% | 6% | 13% | 6% | 7% | 7% | 7% | 7% | 6% | 6% | 6% | 7% | 7% | 6% |
| `parakeet-v3` | 8% | 10% | 10% | 6% | 6% | 4% | 4% | · | 1% | 1% | 1% | 8% | 9% | 8% | 9% | 12% | 16% | 7% | 14% | 7% | 8% | 8% | 8% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `parakeet-v3+boost0.3f` | 8% | 10% | 10% | 6% | 6% | 4% | 4% | 1% | · | 1% | 1% | 8% | 9% | 8% | 9% | 12% | 16% | 7% | 14% | 7% | 8% | 8% | 8% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `parakeet-v3+boost0.5` | 8% | 10% | 10% | 6% | 6% | 4% | 4% | 1% | 1% | · | 1% | 8% | 9% | 7% | 9% | 12% | 16% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 7% | 7% | 7% |
| `parakeet-v3+boost1` | 8% | 10% | 10% | 6% | 6% | 4% | 4% | 1% | 1% | 1% | · | 8% | 8% | 7% | 9% | 12% | 16% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `qwen3-asr-1.7b` | 8% | 10% | 10% | 6% | 6% | 6% | 6% | 8% | 8% | 8% | 8% | · | 3% | 4% | 6% | 11% | 15% | 7% | 15% | 8% | 9% | 9% | 8% | 8% | 8% | 8% | 8% | 8% | 8% | 7% |
| `qwen3-asr-1.7b+ctx` | 9% | 11% | 11% | 6% | 6% | 7% | 7% | 9% | 9% | 9% | 9% | 3% | · | 5% | 6% | 12% | 16% | 8% | 15% | 8% | 9% | 9% | 9% | 9% | 8% | 8% | 8% | 9% | 9% | 8% |
| `qwen3-asr-1.7b+vad` | 8% | 10% | 10% | 6% | 6% | 6% | 6% | 8% | 8% | 7% | 7% | 4% | 5% | · | 2% | 11% | 15% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 7% | 8% | 7% |
| `qwen3-asr-1.7b+vad+terms` | 10% | 11% | 11% | 7% | 7% | 7% | 7% | 9% | 9% | 9% | 9% | 6% | 6% | 2% | · | 12% | 16% | 9% | 15% | 9% | 9% | 9% | 9% | 10% | 8% | 8% | 8% | 9% | 9% | 8% |
| `vibevoice-asr` | 12% | 15% | 15% | 10% | 10% | 11% | 5% | 13% | 13% | 13% | 13% | 12% | 13% | 12% | 13% | · | 12% | 6% | 20% | 13% | 14% | 14% | 13% | 13% | 13% | 13% | 13% | 13% | 13% | 12% |
| `vibevoice-asr+terms` | 17% | 20% | 20% | 15% | 15% | 16% | 5% | 18% | 18% | 18% | 18% | 17% | 18% | 17% | 18% | 13% | · | 6% | 25% | 18% | 19% | 19% | 18% | 17% | 17% | 17% | 17% | 18% | 18% | 17% |
| `whisper-large-v3` | 8% | 8% | 9% | 7% | 7% | 7% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 16% | · | 9% | 2% | 3% | 3% | 4% | 6% | 4% | 4% | 4% | 4% | 3% | 4% |
| `whisper-large-v3+ctx` | 13% | 14% | 14% | 12% | 12% | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 14% | 13% | 14% | 17% | 21% | 8% | · | 9% | 8% | 8% | 10% | 12% | 10% | 10% | 10% | 10% | 8% | 10% |
| `whisper-turbo` | 7% | 8% | 9% | 6% | 7% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 16% | 2% | 9% | · | 2% | 2% | 3% | 6% | 4% | 4% | 4% | 4% | 2% | 4% |
| `whisper-turbo+ctx` | 8% | 9% | 9% | 7% | 7% | 7% | 7% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 12% | 16% | 3% | 9% | 2% | · | 0% | 3% | 6% | 4% | 4% | 4% | 3% | 1% | 4% |
| `whisper-turbo+ctx+nsoff` | 8% | 9% | 9% | 7% | 7% | 7% | 7% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 12% | 16% | 3% | 9% | 2% | 0% | · | 3% | 6% | 4% | 4% | 4% | 3% | 1% | 4% |
| `whisper-turbo+ctx+seq` | 7% | 9% | 9% | 7% | 7% | 7% | 6% | 7% | 8% | 7% | 7% | 8% | 8% | 7% | 9% | 12% | 16% | 4% | 10% | 3% | 3% | 3% | · | 5% | 3% | 3% | 3% | 3% | 3% | 3% |
| `whisper-turbo+ctx+seq+novad` | 6% | 9% | 9% | 6% | 6% | 7% | 6% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 10% | 12% | 15% | 5% | 13% | 6% | 6% | 6% | 5% | · | 4% | 4% | 4% | 5% | 6% | 5% |
| `whisper-turbo+ctx+seq+vadlo` | 7% | 8% | 8% | 6% | 6% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 15% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | · | 0% | 0% | 3% | 4% | 2% |
| `whisper-turbo+ctx+seq+vadlo+echo` | 7% | 8% | 8% | 6% | 6% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 15% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 0% | · | 0% | 3% | 4% | 2% |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | 7% | 8% | 8% | 6% | 6% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 15% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 0% | 0% | · | 3% | 4% | 2% |
| `whisper-turbo+ctx+vadlo` | 7% | 8% | 9% | 7% | 7% | 7% | 6% | 8% | 8% | 7% | 7% | 8% | 8% | 7% | 8% | 12% | 16% | 4% | 10% | 4% | 3% | 3% | 3% | 5% | 3% | 3% | 3% | · | 3% | 3% |
| `whisper-turbo+ctxlong` | 8% | 9% | 9% | 7% | 7% | 7% | 6% | 8% | 8% | 7% | 7% | 8% | 9% | 7% | 9% | 12% | 16% | 3% | 9% | 2% | 1% | 1% | 3% | 6% | 4% | 4% | 4% | 3% | · | 4% |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | 6% | 8% | 8% | 6% | 6% | 6% | 6% | 7% | 7% | 7% | 7% | 7% | 8% | 7% | 8% | 11% | 15% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 2% | 2% | 2% | 3% | 4% | · |

## Clips with repetition loops

- `legacy-whisper-cli`: `30643_s01710`, `31043_s04042`, `36192_s02610`
- `nemotron-3.5-iq4_nl`: `36192_s02610`
- `nemotron-3.5-iq4_nl+terms`: `36192_s02610`
- `parakeet-ft-v1`: `36192_s02610`
- `parakeet-ft-v1+vad90`: `36192_s02610`
- `parakeet-v3`: `36192_s02610`
- `parakeet-v3+boost0.3f`: `36192_s02610`
- `parakeet-v3+boost0.5`: `36192_s02610`
- `parakeet-v3+boost1`: `36192_s02610`
- `qwen3-asr-1.7b+ctx`: `30643_s01710`
- `vibevoice-asr`: `30643_s01710`, `36192_s02610`
- `vibevoice-asr+terms`: `30643_s01710`, `36192_s02610`
- `whisper-large-v3`: `36192_s02610`
- `whisper-turbo+ctx+seq`: `36192_s02610`, `35549_s00390`
- `whisper-turbo+ctx+seq+novad`: `31043_s04042`, `36192_s02610`
- `whisper-turbo+ctx+seq+vadlo`: `30643_s01710`, `36192_s02610`
- `whisper-turbo+ctx+seq+vadlo+echo`: `30643_s01710`, `36192_s02610`
- `whisper-turbo+ctx+seq+vadlo+echo+hst`: `36192_s02610`
- `whisper-turbo+ctxlong+seq+vadlo+echo`: `36192_s02610`

## Not run here

- **Nemotron-3.5-Transcribe (30B)**: about 60 GB of weights, which is more than this machine's 60 GB of RAM. Run it on a cloud H100 and drop its outputs into `data/outputs/` to include it.
- **ElevenLabs Scribe v2 (hosted)**: needs an API key. Intended as an accuracy ceiling on the gold set only.

## Method notes

- Each excerpt is about 6 minutes, cut at pauses found by Silero VAD. All systems get the same 16 kHz audio.
- `+ctx` systems get the talk's prompt from `transcriber/build_context.py`. It is built from metadata and the talk's *old* transcript, as it would be in production.
- WER is computed after Whisper's English normalizer (lowercasing, punctuation and filler words removed, numbers spelled out).
- Legacy text is sliced from full-talk transcripts by segment midpoint, so a few words at clip edges may differ for reasons unrelated to accuracy.
- Drafts for correction come from the legacy transcripts, so the gold set isn't anchored to any new system.
- Excluded `29668_s01050` (To Be Enlightened by the World: 2016 Fall Ango Intensive, Part 2 – Sounds): no speech in this window: loud room/nature sound for a talk titled '... – Sounds' (VAD finds 0.7 s of speech; every system outputs only 'Oh'/'Ah' or nothing); legacy transcript is repeated 'Thank you'.
- Excluded `29856_s00180` (Dongshan Presents Offerings Before The Image): near-silent recording (whole talk ~-61 dB mean; VAD finds 3 s of speech even after loudness normalization); legacy transcript is 101x 'Thank you'.
- Left out of silver WER only `30643_s01710` (Opening Talk): mostly unintelligible: 62 reference words in 6 min, settled by ear as unclear; systems write unrelated text or loop here, which is reported under loops, not WER.
- Non-speech clips skew toward the 1980s tapes, where the old transcripts hallucinate most. They are VAD-confirmed but not yet confirmed by ear (`verified: false` in the manifest).
