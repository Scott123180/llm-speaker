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
