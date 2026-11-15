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
