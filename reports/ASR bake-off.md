# ASR bake-off

_Generated 2026-11-15 00:15 by `eval/report.py`. Re-run after adding systems or references._

**Gold set:** 50 speech excerpts (5.0 h, one per talk, stratified by era / speaker / content / audio difficulty) and 76 non-speech clips (38 min of bells, silence and room noise where VAD finds <10% speech). **Corrected references: 0/50.**

## Findings

_Hand-written interpretation (`eval/findings.md`, last edited 2026-11-14). The tables below are regenerated each run; re-check this section when they change._

These notes are based on 14 systems, 38 stratified speech excerpts plus 12 book excerpts, and 76 non-speech clips. **No human-corrected references exist yet;** sections 8–14 use automatic silver references and the edited book text. Everything below comes from metrics that don't need a reference, plus listening to the side-by-side examples. Treat the ranking as provisional until WER is in.

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

### Recommendation (provisional)

- **Production default:** faster-whisper **turbo + per-talk prompt, sequential decoding, VAD 0.35 with 800 ms padding, prompt-echo filter, hallucination_silence 2 s** (item 17). It has the best silver WER of any system tested (5.6%), the best term spelling of the Whisper setups and the most precise context (about 95%). It's about 80× real time, about 3.4 days for the archive on this PC.
  ```
  uv run python asr/run_whisper.py --model large-v3-turbo --context --batch-size 0 \
      --vad-threshold 0.35 --vad-pad-ms 800 --drop-prompt-echo --hallucination-silence 2
  ```
- **Upgrade if WER supports it:** **Qwen3-ASR + VAD + term list**, for difficult talks or a full cloud run. Its term list is less precise (about 68%).
- **Not recommended as configured:**
  - large-v3 with a prompt, which is mostly insertions
  - Qwen with a prose prompt, which echoes and inserts
  - Parakeet's gentle boost, which does almost nothing
- **Before deciding,** correct about 15–20 references (see `eval/CONVENTIONS.md`) and re-run `eval/report.py`. That adds WER, term recall and false insertions with confidence intervals. The A10 run adds three more voter families to the silver references.

> **Accuracy (WER) is not measured yet.** No corrected references exist, so this report shows only what can be measured without them: speed, hallucination on non-speech, how each system spells glossary terms, repetition loops, and agreement between systems. Correct the drafts in `eval/goldset/drafts/` into `eval/goldset/refs/` (see `eval/CONVENTIONS.md`) and re-run to add WER, term recall and per-stratum results.

## Systems

| System | Model | Context | Device | Speed (× real time) | GPU peak | Archive time on this PC* |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | openai-whisper CLI turbo (existing transcripts) | — | unknown | — | — | — |
| `granite-5.0-2b` | ibm-granite/granite-speech-5.0-2b | — | cuda | 19 | 5497 MB | 14.1 days |
| `granite-5.0-2b+terms` | ibm-granite/granite-speech-5.0-2b | keyword list (hard terms, max 20) | cuda | 20 | 5499 MB | 13.3 days |
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
| `vibevoice-asr` | ? | — | ? | — | — | — |
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
| `vibevoice-asr` | 1/6 (17%) | 5.2% (9 of 172) | — | 0 | 121 | 17.5 |
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

| System | Silver WER (all) | substitutions / deletions / insertions | Stratified set | Book set | Voters |
|---|---|---|---|---|---|
| `vibevoice-asr` | 3.8% | 1.6% / 0.4% / 1.7% | 3.8% | — | 4.0 |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | 4.9% | 1.5% / 2.6% / 0.9% | 5.2% | 4.1% | 3.4 |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | 5.2% | 1.5% / 2.9% / 0.8% | 5.5% | 3.8% | 3.4 |
| `whisper-turbo+ctx+seq+vadlo+echo` | 5.2% | 1.4% / 2.9% / 0.9% | 5.5% | 3.9% | 3.4 |
| `parakeet-ft-v1+vad90` | 5.2% | 1.7% / 0.8% / 2.7% | 5.5% | 4.0% | 3.3 |
| `whisper-turbo+ctx+seq+vadlo` | 5.2% | 1.4% / 2.9% / 0.9% | 5.5% | 4.0% | 3.4 |
| `whisper-turbo` | 5.4% | 1.3% / 3.6% / 0.5% | 5.3% | 5.5% | 3.4 |
| `whisper-large-v3` | 5.4% | 1.1% / 3.8% / 0.4% | 5.5% | 5.0% | 3.4 |
| `parakeet-ft-v1` | 5.5% | 2.0% / 0.9% / 2.7% | 5.7% | 4.9% | 3.3 |
| `whisper-turbo+ctx+vadlo` | 5.6% | 1.3% / 3.8% / 0.6% | 5.9% | 4.5% | 3.4 |
| `whisper-turbo+ctx+seq` | 5.7% | 1.4% / 3.5% / 0.9% | 5.7% | 5.5% | 3.4 |
| `qwen3-asr-1.7b+vad` | 5.7% | 2.5% / 1.7% / 1.5% | 5.7% | 5.6% | 3.3 |
| `whisper-turbo+ctxlong` | 5.7% | 1.1% / 4.1% / 0.5% | 5.8% | 5.6% | 3.4 |
| `whisper-turbo+ctx+seq+novad` | 5.9% | 1.6% / 2.3% / 2.0% | 6.4% | 4.2% | 3.4 |
| `whisper-turbo+ctx` | 6.0% | 1.1% / 4.5% / 0.5% | 6.1% | 5.6% | 3.4 |
| `whisper-turbo+ctx+nsoff` | 6.0% | 1.1% / 4.5% / 0.5% | 6.1% | 5.6% | 3.4 |
| `qwen3-asr-1.7b` | 6.2% | 2.8% / 1.5% / 1.9% | 6.3% | 5.8% | 3.3 |
| `parakeet-v3+boost0.5` | 6.3% | 2.0% / 2.2% / 2.1% | 6.2% | 6.4% | 3.3 |
| `legacy-whisper-cli` | 6.3% | 1.7% / 1.5% / 3.1% | 6.7% | 4.7% | 3.4 |
| `parakeet-v3+boost1` | 6.3% | 1.9% / 2.2% / 2.2% | 6.2% | 6.7% | 3.3 |
| `parakeet-v3` | 6.5% | 2.0% / 2.3% / 2.2% | 6.3% | 6.9% | 3.3 |
| `parakeet-v3+boost0.3f` | 6.5% | 2.0% / 2.3% / 2.2% | 6.4% | 7.0% | 3.3 |
| `qwen3-asr-1.7b+ctx` | 6.9% | 2.7% / 1.7% / 2.6% | 7.1% | 6.1% | 3.3 |
| `qwen3-asr-1.7b+vad+terms` | 7.1% | 2.6% / 1.7% / 2.8% | 7.5% | 5.5% | 3.3 |
| `granite-5.0-2b+terms` | 7.7% | 1.9% / 4.6% / 1.2% | 8.5% | 4.6% | 3.3 |
| `granite-5.0-2b` | 7.8% | 2.1% / 4.5% / 1.1% | 8.6% | 4.4% | 3.3 |
| `whisper-large-v3+ctx` | 11.3% | 1.7% / 9.2% / 0.4% | 11.6% | 9.9% | 3.4 |

## Effect of per-talk context

| Base → variant | Misheard terms: base → variant | Non-speech output: base → variant | Disagreement between the two |
|---|---|---|---|
| `granite-5.0-2b` → `granite-5.0-2b+terms` | 13.0% → 10.3% | 7 → 7 clips | 2.3% of words |
| `parakeet-ft-v1` → `parakeet-ft-v1+vad90` | 16.3% → 16.6% | 3 → 4 clips | 2.3% of words |
| `parakeet-v3` → `parakeet-v3+boost0.3f` | 14.2% → 13.6% | 4 → 7 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost0.5` | 14.2% → 10.9% | 4 → 5 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost1` | 14.2% → 10.8% | 4 → 5 clips | 1.1% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+ctx` | 2.3% → 2.1% | 74 → 74 clips | 2.6% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+vad` | 2.3% → 2.9% | 74 → 7 clips | 4.0% of words |
| `qwen3-asr-1.7b+vad` → `qwen3-asr-1.7b+vad+terms` | 2.9% → 1.9% | 7 → 7 clips | 2.3% of words |
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
| `vibevoice-asr` | doksan, Shapa, Huiko, Sashin, Ongo |
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
- `vibevoice-asr`: "[Human Sounds] So. Did that be."×1
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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
| `vibevoice-asr` | _(nothing)_ |
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

**zazen** — `35726_s01200` at 0:15 · Geoffrey Shugen Arnold · 2000s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `granite-5.0-2b` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `granite-5.0-2b+terms` | has no interest in demystifying what he calls the essential art of zazen on the contrary it is precisely the unthinkable mystery of |
| `parakeet-ft-v1` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `parakeet-ft-v1+vad90` | has no interest in demystifying what he calls the essential art of Zazin. On the contrary, it is precisely the unthinkable mystery of |
| `parakeet-v3` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `parakeet-v3+boost0.3f` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `parakeet-v3+boost0.5` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `parakeet-v3+boost1` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `qwen3-asr-1.7b` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `qwen3-asr-1.7b+ctx` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `qwen3-asr-1.7b+vad` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `qwen3-asr-1.7b+vad+terms` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `vibevoice-asr` | _(nothing)_ |
| `whisper-large-v3` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-large-v3+ctx` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+nsoff` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+seq` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+seq+novad` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+seq+vadlo` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+seq+vadlo+echo` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctx+vadlo` | has no interest in demystifying what he calls the essential art of Zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctxlong` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | has no interest in demystifying what he calls the essential art of zazen. On the contrary, it is precisely the unthinkable mystery of |

## Agreement between systems

Word error rate of each row's output measured against each column's output, on speech clips. Systems that agree closely are making the same choices, not necessarily the right ones.

| | `legacy-whisper-cli` | `granite-5.0-2b` | `granite-5.0-2b+terms` | `parakeet-ft-v1` | `parakeet-ft-v1+vad90` | `parakeet-v3` | `parakeet-v3+boost0.3f` | `parakeet-v3+boost0.5` | `parakeet-v3+boost1` | `qwen3-asr-1.7b` | `qwen3-asr-1.7b+ctx` | `qwen3-asr-1.7b+vad` | `qwen3-asr-1.7b+vad+terms` | `vibevoice-asr` | `whisper-large-v3` | `whisper-large-v3+ctx` | `whisper-turbo` | `whisper-turbo+ctx` | `whisper-turbo+ctx+nsoff` | `whisper-turbo+ctx+seq` | `whisper-turbo+ctx+seq+novad` | `whisper-turbo+ctx+seq+vadlo` | `whisper-turbo+ctx+seq+vadlo+echo` | `whisper-turbo+ctx+seq+vadlo+echo+hst` | `whisper-turbo+ctx+vadlo` | `whisper-turbo+ctxlong` | `whisper-turbo+ctxlong+seq+vadlo+echo` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | · | 10% | 10% | 7% | 6% | 9% | 9% | 8% | 8% | 9% | 9% | 9% | 10% | 6% | 7% | 15% | 7% | 8% | 8% | 8% | 7% | 7% | 7% | 7% | 8% | 8% | 7% |
| `granite-5.0-2b` | 10% | · | 2% | 9% | 8% | 10% | 10% | 10% | 10% | 10% | 11% | 9% | 11% | 8% | 8% | 15% | 8% | 9% | 9% | 8% | 9% | 8% | 8% | 8% | 8% | 9% | 8% |
| `granite-5.0-2b+terms` | 10% | 2% | · | 9% | 8% | 10% | 10% | 10% | 10% | 10% | 11% | 10% | 11% | 8% | 8% | 15% | 8% | 9% | 9% | 9% | 9% | 8% | 8% | 8% | 8% | 9% | 8% |
| `parakeet-ft-v1` | 7% | 9% | 9% | · | 2% | 4% | 4% | 4% | 4% | 7% | 7% | 6% | 7% | 4% | 7% | 14% | 7% | 8% | 8% | 7% | 7% | 6% | 6% | 6% | 7% | 7% | 6% |
| `parakeet-ft-v1+vad90` | 7% | 9% | 9% | 2% | · | 5% | 5% | 5% | 5% | 6% | 7% | 6% | 7% | 4% | 6% | 13% | 6% | 7% | 7% | 7% | 7% | 6% | 6% | 6% | 7% | 7% | 6% |
| `parakeet-v3` | 8% | 10% | 10% | 4% | 4% | · | 1% | 1% | 1% | 8% | 9% | 8% | 9% | 6% | 7% | 14% | 7% | 8% | 8% | 8% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `parakeet-v3+boost0.3f` | 8% | 10% | 10% | 4% | 4% | 1% | · | 1% | 1% | 8% | 9% | 8% | 9% | 6% | 7% | 14% | 7% | 8% | 8% | 8% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `parakeet-v3+boost0.5` | 8% | 10% | 10% | 4% | 4% | 1% | 1% | · | 1% | 8% | 9% | 7% | 9% | 6% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 7% | 7% | 7% |
| `parakeet-v3+boost1` | 8% | 10% | 10% | 4% | 4% | 1% | 1% | 1% | · | 8% | 8% | 7% | 9% | 6% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 8% | 8% | 7% |
| `qwen3-asr-1.7b` | 8% | 10% | 10% | 6% | 6% | 8% | 8% | 8% | 8% | · | 3% | 4% | 6% | 5% | 7% | 15% | 8% | 9% | 9% | 8% | 8% | 8% | 8% | 8% | 8% | 8% | 7% |
| `qwen3-asr-1.7b+ctx` | 9% | 11% | 11% | 7% | 7% | 9% | 9% | 9% | 9% | 3% | · | 5% | 6% | 6% | 8% | 15% | 8% | 9% | 9% | 9% | 9% | 8% | 8% | 8% | 9% | 9% | 8% |
| `qwen3-asr-1.7b+vad` | 8% | 10% | 10% | 6% | 6% | 8% | 8% | 7% | 7% | 4% | 5% | · | 2% | 5% | 7% | 14% | 7% | 8% | 8% | 7% | 8% | 7% | 7% | 7% | 7% | 8% | 7% |
| `qwen3-asr-1.7b+vad+terms` | 10% | 11% | 11% | 7% | 7% | 9% | 9% | 9% | 9% | 6% | 6% | 2% | · | 9% | 9% | 15% | 9% | 9% | 9% | 9% | 10% | 8% | 8% | 8% | 9% | 9% | 8% |
| `vibevoice-asr` | 6% | 8% | 8% | 4% | 4% | 6% | 6% | 6% | 6% | 5% | 6% | 5% | 9% | · | 6% | 11% | 5% | 6% | 6% | 6% | 6% | 5% | 5% | 5% | 5% | 5% | 5% |
| `whisper-large-v3` | 8% | 8% | 9% | 7% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 6% | · | 9% | 2% | 3% | 3% | 4% | 6% | 4% | 4% | 4% | 4% | 3% | 4% |
| `whisper-large-v3+ctx` | 13% | 14% | 14% | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 14% | 13% | 14% | 10% | 8% | · | 9% | 8% | 8% | 10% | 12% | 10% | 10% | 10% | 10% | 8% | 10% |
| `whisper-turbo` | 7% | 8% | 9% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 5% | 2% | 9% | · | 2% | 2% | 3% | 6% | 4% | 4% | 4% | 4% | 2% | 4% |
| `whisper-turbo+ctx` | 8% | 9% | 9% | 7% | 7% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 6% | 3% | 9% | 2% | · | 0% | 3% | 6% | 4% | 4% | 4% | 3% | 1% | 4% |
| `whisper-turbo+ctx+nsoff` | 8% | 9% | 9% | 7% | 7% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 6% | 3% | 9% | 2% | 0% | · | 3% | 6% | 4% | 4% | 4% | 3% | 1% | 4% |
| `whisper-turbo+ctx+seq` | 7% | 9% | 9% | 7% | 6% | 7% | 8% | 7% | 7% | 8% | 8% | 7% | 9% | 5% | 4% | 10% | 3% | 3% | 3% | · | 5% | 3% | 3% | 3% | 3% | 3% | 3% |
| `whisper-turbo+ctx+seq+novad` | 6% | 9% | 9% | 7% | 6% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 10% | 6% | 5% | 13% | 6% | 6% | 6% | 5% | · | 4% | 4% | 4% | 5% | 6% | 5% |
| `whisper-turbo+ctx+seq+vadlo` | 7% | 8% | 8% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 5% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | · | 0% | 0% | 3% | 4% | 2% |
| `whisper-turbo+ctx+seq+vadlo+echo` | 7% | 8% | 8% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 5% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 0% | · | 0% | 3% | 4% | 2% |
| `whisper-turbo+ctx+seq+vadlo+echo+hst` | 7% | 8% | 8% | 6% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 5% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 0% | 0% | · | 3% | 4% | 2% |
| `whisper-turbo+ctx+vadlo` | 7% | 8% | 9% | 7% | 6% | 8% | 8% | 7% | 7% | 8% | 8% | 7% | 8% | 5% | 4% | 10% | 4% | 3% | 3% | 3% | 5% | 3% | 3% | 3% | · | 3% | 3% |
| `whisper-turbo+ctxlong` | 8% | 9% | 9% | 7% | 6% | 8% | 8% | 7% | 7% | 8% | 9% | 7% | 9% | 5% | 3% | 9% | 2% | 1% | 1% | 3% | 6% | 4% | 4% | 4% | 3% | · | 4% |
| `whisper-turbo+ctxlong+seq+vadlo+echo` | 6% | 8% | 8% | 6% | 6% | 7% | 7% | 7% | 7% | 7% | 8% | 7% | 8% | 5% | 4% | 11% | 4% | 4% | 4% | 3% | 4% | 2% | 2% | 2% | 3% | 4% | · |

## Clips with repetition loops

- `legacy-whisper-cli`: `30643_s01710`, `31043_s04042`, `36192_s02610`
- `parakeet-ft-v1`: `36192_s02610`
- `parakeet-ft-v1+vad90`: `36192_s02610`
- `parakeet-v3`: `36192_s02610`
- `parakeet-v3+boost0.3f`: `36192_s02610`
- `parakeet-v3+boost0.5`: `36192_s02610`
- `parakeet-v3+boost1`: `36192_s02610`
- `qwen3-asr-1.7b+ctx`: `30643_s01710`
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
- Non-speech clips skew toward the 1980s tapes, where the old transcripts hallucinate most. They are VAD-confirmed but not yet confirmed by ear (`verified: false` in the manifest).
