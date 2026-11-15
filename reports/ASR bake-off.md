# ASR bake-off

_Generated 2026-11-14 20:23 by `eval/report.py`. Re-run after adding systems or references._

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

### Recommendation (provisional)

- **Production default:** faster-whisper **turbo + per-talk prompt + VAD**. It has the most precise context (about 95%), the best term spelling and the best speed.
- **Fix before production:** turbo's phrase drops (about 2.4% of words). Test VAD settings, then smaller batches. A second system can fill the gaps: parakeet-ft-v1 is fast and rarely drops a phrase.
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
| `parakeet-ft-v1+vad90` | freetranscribe/parakeet-ft-v1 | — | cuda | 189 | 3509 MB | 1.4 days |
| `parakeet-v3` | nvidia/parakeet-tdt-0.6b-v3 | — | cuda | 228 | 5003 MB | 1.2 days |
| `parakeet-v3+boost0.3f` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.3, hard terms (difficulty>=0.15, with evidence) | cuda | 194 | 5003 MB | 1.4 days |
| `parakeet-v3+boost0.5` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.5, top 40 talk terms | cuda | 193 | 5003 MB | 1.4 days |
| `parakeet-v3+boost1` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=1.0, top 40 talk terms | cuda | 194 | 5003 MB | 1.4 days |
| `qwen3-asr-1.7b` | Qwen/Qwen3-ASR-1.7B | — | cuda | 22 | 5160 MB | 12.4 days |
| `qwen3-asr-1.7b+ctx` | Qwen/Qwen3-ASR-1.7B | system prompt = talk prompt | cuda | 21 | 5649 MB | 12.7 days |
| `qwen3-asr-1.7b+vad` | Qwen/Qwen3-ASR-1.7B | — | cuda | 21 | 5396 MB | 12.7 days |
| `qwen3-asr-1.7b+vad+terms` | Qwen/Qwen3-ASR-1.7B | system prompt = hard-term list | cuda | 21 | 5310 MB | 12.7 days |
| `whisper-large-v3` | faster-whisper large-v3 | — | cuda | 61 | 4501 MB | 4.4 days |
| `whisper-large-v3+ctx` | faster-whisper large-v3 | hotwords=talk prompt | cuda | 58 | 4995 MB | 4.7 days |
| `whisper-turbo` | faster-whisper large-v3-turbo | — | cuda | 150 | 3320 MB | 1.8 days |
| `whisper-turbo+ctx` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 151 | 3336 MB | 1.8 days |

\* 6,500 h of audio at the measured speed on short clips (includes per-clip overhead, so full talks run somewhat faster). `legacy-whisper-cli` = the existing transcripts (Whisper CLI turbo, no VAD, no prompt, `condition_on_previous_text=True`).

## Summary

| System | Non-speech clips with invented text | Glossary terms misheard | Prompt echo | Loops | Words/min | Punct./100 words |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | 76/76 (100%) | 11.3% (48 of 425) | — | 3 | 112 | 13.7 |
| `parakeet-ft-v1+vad90` | 4/76 (5%) | 16.6% (61 of 367) | — | 1 | 111 | 12.4 |
| `parakeet-v3` | 4/76 (5%) | 14.2% (51 of 360) | — | 1 | 109 | 15.5 |
| `parakeet-v3+boost0.3f` | 7/76 (9%) | 13.6% (49 of 359) | 0 clips | 1 | 109 | 15.5 |
| `parakeet-v3+boost0.5` | 5/76 (7%) | 10.9% (41 of 375) | 0 clips | 1 | 109 | 15.5 |
| `parakeet-v3+boost1` | 5/76 (7%) | 10.8% (42 of 388) | 0 clips | 1 | 109 | 15.4 |
| `qwen3-asr-1.7b` | 74/76 (97%) | 2.3% (8 of 354) | — | 0 | 110 | 16.7 |
| `qwen3-asr-1.7b+ctx` | 74/76 (97%) | 2.1% (10 of 476) | 6 clips (1.4% of audio) | 1 | 110 | 16.6 |
| `qwen3-asr-1.7b+vad` | 7/76 (9%) | 2.9% (11 of 374) | — | 0 | 109 | 16.6 |
| `qwen3-asr-1.7b+vad+terms` | 7/76 (9%) | 1.9% (8 of 415) | 0 clips | 0 | 110 | 16.5 |
| `whisper-large-v3` | 7/76 (9%) | 8.0% (33 of 411) | — | 1 | 106 | 15.9 |
| `whisper-large-v3+ctx` | 7/76 (9%) | 2.5% (12 of 475) | 13 clips (2.0% of audio) | 0 | 100 | 16.9 |
| `whisper-turbo` | 7/76 (9%) | 13.1% (55 of 421) | — | 0 | 107 | 16.0 |
| `whisper-turbo+ctx` | 7/76 (9%) | 3.9% (17 of 440) | 0 clips | 0 | 106 | 16.6 |

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
| `whisper-turbo` | 5.8% | 1.4% / 4.0% / 0.5% | 5.9% | 5.4% | 2.0 |
| `whisper-large-v3` | 5.9% | 1.3% / 4.2% / 0.4% | 6.1% | 5.0% | 2.0 |
| `parakeet-ft-v1+vad90` | 6.3% | 1.7% / 0.6% / 4.0% | 6.5% | 5.4% | 2.0 |
| `whisper-turbo+ctx` | 6.5% | 1.2% / 4.8% / 0.5% | 6.8% | 5.5% | 2.0 |
| `legacy-whisper-cli` | 6.8% | 1.8% / 1.9% / 3.1% | 7.1% | 5.6% | 2.0 |
| `parakeet-v3+boost0.5` | 7.1% | 2.0% / 1.8% / 3.3% | 7.3% | 6.5% | 2.0 |
| `qwen3-asr-1.7b+vad` | 7.2% | 2.6% / 1.3% / 3.3% | 7.2% | 7.3% | 2.0 |
| `parakeet-v3+boost1` | 7.2% | 2.0% / 1.9% / 3.4% | 7.4% | 6.8% | 2.0 |
| `parakeet-v3` | 7.5% | 2.0% / 2.0% / 3.4% | 7.7% | 7.0% | 2.0 |
| `parakeet-v3+boost0.3f` | 7.5% | 2.0% / 2.1% / 3.4% | 7.6% | 7.4% | 2.0 |
| `qwen3-asr-1.7b` | 7.8% | 2.8% / 1.2% / 3.8% | 7.8% | 7.7% | 2.0 |
| `qwen3-asr-1.7b+ctx` | 8.4% | 2.7% / 1.3% / 4.4% | 8.5% | 7.9% | 2.0 |
| `qwen3-asr-1.7b+vad+terms` | 8.6% | 2.6% / 1.4% / 4.6% | 9.0% | 7.1% | 2.0 |
| `whisper-large-v3+ctx` | 11.7% | 1.7% / 9.6% / 0.5% | 12.2% | 9.9% | 2.0 |

## Effect of per-talk context

| Base → variant | Misheard terms: base → variant | Non-speech output: base → variant | Disagreement between the two |
|---|---|---|---|
| `parakeet-v3` → `parakeet-v3+boost0.3f` | 14.2% → 13.6% | 4 → 7 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost0.5` | 14.2% → 10.9% | 4 → 5 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost1` | 14.2% → 10.8% | 4 → 5 clips | 1.1% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+ctx` | 2.3% → 2.1% | 74 → 74 clips | 2.6% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+vad` | 2.3% → 2.9% | 74 → 7 clips | 4.0% of words |
| `qwen3-asr-1.7b+vad` → `qwen3-asr-1.7b+vad+terms` | 2.9% → 1.9% | 7 → 7 clips | 2.3% of words |
| `whisper-large-v3` → `whisper-large-v3+ctx` | 8.0% → 2.5% | 7 → 7 clips | 8.1% of words |
| `whisper-turbo` → `whisper-turbo+ctx` | 13.1% → 3.9% | 7 → 7 clips | 2.0% of words |

Disagreement is the word error rate between the two outputs: how much of the text the context changed.

## Most frequent misheard glossary terms

| System | Top known misspellings in its output |
|---|---|
| `legacy-whisper-cli` | Zhao, Yakujo, Shapa, Maizumi, doksan, Daito, Ingo, Huiko, Ongan, Setsho, Zazengi, Wutsu |
| `parakeet-ft-v1+vad90` | dogan, gasho, Yakujo, Secho, Mizumi, Mayakaya Shapa, Shapa, kohan, Orioki, Zhao, Ingo, Huiko |
| `parakeet-v3` | gasho, Yakujo, Secho, Mizumi, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, seshin, Orioki |
| `parakeet-v3+boost0.3f` | gasho, Secho, Mizumi, Yakujo, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, Orioki, seshin |
| `parakeet-v3+boost0.5` | gasho, Yakujo, Mizumi, Secho, Mayakaya Shapa, Shapa, doksan, Orioki, Ingo, seshin, Ongo, Zazengi |
| `parakeet-v3+boost1` | gasho, Yakujo, Mizumi, Secho, Mayakaya Shapa, Shapa, doksan, Orioki, Ingo, seshin, Ongo, Zazengi |
| `qwen3-asr-1.7b` | Mazumi, Ongo, seshin, doksan, Zhao, Uman |
| `qwen3-asr-1.7b+ctx` | Shapa, Mazumi, Ongo, doksan, Genjo |
| `qwen3-asr-1.7b+vad` | Shapa, doksan, Uman, Ongo, Doxan, Tikkadhan, Genjo |
| `qwen3-asr-1.7b+vad+terms` | doksan, Dogon, Tikkadhan, Genjo |
| `whisper-large-v3` | Yakujo, Shapa, Maizumi, doksan, Setsho, Huiko, Daito, Ingo, Mayakaya Shapa, Mizumi, Yunmin, Ongo |
| `whisper-large-v3+ctx` | Shapa, Mayakaya Shapa, Setsho, Zenda, Dogon |
| `whisper-turbo` | doksan, Yakujo, Shapa, gasho, Maizumi, Gashow, Setsho, Mayakaya Shapa, Huiko, Daito, Zhao, Ingo |
| `whisper-turbo+ctx` | Shapa, Setsho, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda, Sazen |

## What systems output on non-speech

- `legacy-whisper-cli`: "Thank you."×73; "thank you"×3
- `parakeet-ft-v1+vad90`: "Yeah"×2; "Thank you."×1; "Sent be"×1
- `parakeet-v3`: "So that"×1; "Okay."×1; "Just working on the"×1; "Sension be number two."×1
- `parakeet-v3+boost0.3f`: "So that"×1; "But then you know we do want to write a lot of"×1; "Thank you."×1; "Okay."×1; "Just a little bit."×1; "Sension be number two."×1
- `parakeet-v3+boost0.5`: "So that"×1; "Okay."×1; "Just working on the"×1; "Sension be number two."×1; "No, no, baby."×1
- `parakeet-v3+boost1`: "So that"×1; "Thank you."×1; "Okay."×1; "Just a little bit of a"×1; "Sension be number two."×1
- `qwen3-asr-1.7b`: "The."×24; "Oh."×12; "Okay."×8; "Oh, oh,"×3; "The first thing that you need to do is to get a good underst"×3; "Yeah."×2
- `qwen3-asr-1.7b+ctx`: "This is a dharma talk by John Daido Loori, Daido Roshi, at Z"×54; "This is a dharma talk by Geoffrey Shugen Arnold, Shugen Rosh"×4; "Yeah."×2; "This is a dharma talk by Mark Sando Mininberg at Zen Mountai"×2; "This is a dharma talk by Ron Hogen Green, Hogen Sensei, at Z"×2; "So that being."×1
- `qwen3-asr-1.7b+vad`: "Oh."×2; "Yeah."×2; "Thank you."×1; "Ah."×1; "Sentient beings are."×1
- `qwen3-asr-1.7b+vad+terms`: "Yeah."×2; "Oh."×1; "Thank you."×1; "Ango, Kannon, Shobogenzo, mondo."×1; "Hyakujo, thangka, oryoki, Kannon."×1; "Sanctian beings are."×1
- `whisper-large-v3`: "Thank you."×3; "Yeah."×2; "Yes."×1; "sentient beings are"×1
- `whisper-large-v3+ctx`: "Opening Talk."×2; "Thank you."×2; "Thank you for watching!"×1; "Shobogenzo."×1; "Sentient beings are..."×1
- `whisper-turbo`: "Amen."×2; "Thank you."×2; "Bye."×1; "Yeah."×1; "Sentient beings are"×1
- `whisper-turbo+ctx`: "Thank you."×4; "Amen."×1; "Shobogenzo."×1; "Sentient beings are..."×1

## Side-by-side examples

Snippets around a glossary term, aligned to `whisper-large-v3+ctx`. Each starts a few words before the term. Listen to the clip (`data/goldset/clips/<clip>.wav`, at the given offset) to judge which is right.

**dharma** — `30766_s00180` at 1:03 · John Daido Loori · 1980s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called the precept of refraining from |
| `parakeet-ft-v1+vad90` | nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost0.3f` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost0.5` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `parakeet-v3+boost1` | is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `qwen3-asr-1.7b` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `qwen3-asr-1.7b+ctx` | nature is clear and obvious in the sphere of the unstained dharma. Not yielding to attachment is called the precept of refraining from |
| `qwen3-asr-1.7b+vad` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `qwen3-asr-1.7b+vad+terms` | nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment, is called the precept of refraining from |
| `whisper-large-v3` | -nature is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-large-v3+ctx` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo` | -nature is clear and obvious. In the sphere of the unstained Dharma, not yielding to attachment is called a precept of refraining from |
| `whisper-turbo+ctx` | -nature is clear and obvious. In the sphere of the unstained dharma, not yielding to attachment is called a precept of refraining from |

**zendo** — `32995_s00180` at 2:36 · Konrad Ryushin Marchaj · 2010s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | our life. If we were to leave this within the Zenda, that question of what good does it really do, should be on |
| `parakeet-ft-v1+vad90` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost0.3f` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost0.5` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `parakeet-v3+boost1` | our life. If we were to leave this within the Zenda, that question of what good does it really do should be on |
| `qwen3-asr-1.7b` | our life. For to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+ctx` | our life. For to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+vad` | our life. For us to leave this within the zendo, that question of what good does it really do should be on |
| `qwen3-asr-1.7b+vad+terms` | our life. For us to leave this within the zendo, that question of what good does it really do should be on |
| `whisper-large-v3` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-large-v3+ctx` | our life. If we were to leave this within the zenda, that question of what good does it really do should be on |
| `whisper-turbo` | our life. If we were to leave this within the Zenda, that question of what good does it really do, should be on |
| `whisper-turbo+ctx` | our life. If we were to leave this within the zenda, that question of what good does it really do, should be on |

**Baizhang Huaihai** — `31268_s00240` at 0:59 · John Daido Loori · 1980s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | was Yakujo, as we talked about in the colon of Yakujo and the fox. And another was Nansen. Basso once said of his |
| `parakeet-ft-v1+vad90` | was Yakujo, as we talked about in the cone of Yakujo and the Fox, and another was nonsense. Baso once said of these |
| `parakeet-v3` | was Yakujo, that we talked about in the column of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost0.3f` | was Yakujo, that we talked about in the column of Yakujo and the Fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost0.5` | was Yakujo, that we talked about in the column of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `parakeet-v3+boost1` | was Yakujo, that we talked about in the corner of Yakujo and the fox. And another was nonsense. Baso once said of these |
| `qwen3-asr-1.7b` | was Yakujyo, that we talked about, the cone, Yakujyo, and the fox; and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+ctx` | was Hyakujo, that we talked about the cone, Hyakujo, and the fox, and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+vad` | was Yakujyo, that we talked about, the cone of Yakujyo and the fox, and the other was Nansen. Baso once said of these |
| `qwen3-asr-1.7b+vad+terms` | was Hyakujo, that we talked about, the cone of Hyakujo and the fox, and the other was Nansen. Baso once said of these |
| `whisper-large-v3` | was Yakujo, that we talked about in the calling of Yakujo and the fox. And another was Nansen. Basso once said of these |
| `whisper-large-v3+ctx` | was Hyakujo, that we talked about in the calling of Hyakujo and the fox, and another was Nansen. Basso once said of these |
| `whisper-turbo` | was Yakujo, that we talked about in the colon of Yakujo and the fox. And another was Nansen. Basso once said of these |
| `whisper-turbo+ctx` | was Hyakujo, that we talked about in the colon of Hyakujo and the fox, and another was Nansen. Baso once said of these |

**densho** — `33528_s01214` at 2:09 · John Daido Loori · 1990s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | is communication. It's what it is. You know, the bell rings, the dencho rings. It's time to go to the Buddha Hall for |
| `parakeet-ft-v1+vad90` | it's communication is what it is. You know the bell rings the dent show rings it's time to go to the Buddha hall for |
| `parakeet-v3` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost0.3f` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost0.5` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `parakeet-v3+boost1` | is communication, is what it is. You know, the bell rings, the dentro rings, it's time to go to the Buddha Hall for |
| `qwen3-asr-1.7b` | It's communication. It's what it is. You know, the bell rings, the dento rings. It's time to go to the Buddha hall for |
| `qwen3-asr-1.7b+ctx` | It's communication. It's what it is. You know, the bell rings, the dento rings. It's time to go to the Buddha hall for |
| `qwen3-asr-1.7b+vad` | It's communication. It's what it is. You know, the bell rings. The bell rings. It's time to go to the Buddha Hall for |
| `qwen3-asr-1.7b+vad+terms` | It's communication. It's what it is. You know, the bell rings. The bell rings. It's time to go to the Buddha Hall for |
| `whisper-large-v3` | is communication, is what it is. You know, the bell rings, the denture rings, it's time to go to the Buddha Hall for |
| `whisper-large-v3+ctx` | It's communication, it's what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |
| `whisper-turbo` | is communication is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha hall for |
| `whisper-turbo+ctx` | is communication, is what it is. You know, the bell rings, the densho rings, it's time to go to the Buddha Hall for |

**Zhaozhou Congshen** — `34803_s00570` at 4:05 · Geoffrey Shugen Arnold · 2020s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | What was her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could, from one perspective, say, is a great master. |
| `parakeet-ft-v1+vad90` | What was her power? She's a T woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master. |
| `parakeet-v3+boost0.3f` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3+boost0.5` | What was her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, |
| `parakeet-v3+boost1` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, |
| `qwen3-asr-1.7b` | What was her power? She's a tea woman offering refreshment to travelers. Zhao, you could, from one perspective, say, is a great master. |
| `qwen3-asr-1.7b+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master, |
| `qwen3-asr-1.7b+vad` | What was her power? She's a tea woman offering refreshment to travelers. Jangjo, you could, from one perspective, say is a great master, |
| `qwen3-asr-1.7b+vad+terms` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say is a great master, |
| `whisper-large-v3` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-large-v3+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |
| `whisper-turbo` | What was her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could from one perspective say, is a great master. |
| `whisper-turbo+ctx` | What was her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. |

**Yantou Quanhuo** — `34004_s01972` at 1:08 · Other · 1990s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | shift together. You were sweeping under the pizza oven and you swept down a little critter and it was caught in flypaper and you ran over in a panic. I don't know if it's dead or alive. There's something in the flypaper. What's the constant principle of that? May your life go well. Attention. First, I want to let you know I've never done this before so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of matter. If you do not agree, then you're forever sunk in |
| `parakeet-ft-v1+vad90` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was hot in fly paper and you ran over in a panic. Uh I don't know if it's dead or live. There's there's something in the fly paper. What's the constant principle for that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous about this. As far as the last line of the call on it, if you agree, then you're still attached to sense of matter. If you do not agree, then you're forever sunk in |
| `parakeet-v3` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran it over in a panic. |
| `parakeet-v3+boost0.3f` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, then you're still attached to |
| `parakeet-v3+boost0.5` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, then you're still attached to |
| `parakeet-v3+boost1` | together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. Uh I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the call on it, if you agree, then you're still attached to |
| `qwen3-asr-1.7b` | shift together, you were sweeping under the pizza oven and you swept out little critters. Caught in the flypaper, and you ran over a pan. I don't think there's a lot. There's there's something in the flypaper. What's the constant principle? That. May your life go well. Attention. So I want to let you know I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you agree, then you're still a |
| `qwen3-asr-1.7b+ctx` | shift together. You were sweeping under the pizza oven and you swept out little critters. Caught in the fly paper. You ran over a pan. I don't think there's a lot. There's there's something in the fly paper. What's the constant principle? That. May your life go well. Attention. Just so I let you know, I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you agree that you're still a |
| `qwen3-asr-1.7b+vad` | shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm nervous. As far as the last line |
| `qwen3-asr-1.7b+vad+terms` | shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm not nervous. As far as the last line |
| `whisper-large-v3` | koan, if you agree, then you're still attached to the sense of matter. If you do not agree... Then you're forever sunk in |
| `whisper-large-v3+ctx` | John Daido Loori, Bernie Glassman, Tokusan, Zen Peacemaker Order, and Ganto. We'll be talking about John Daido Loori, Bernie Glassman, Tokusan, Zen Peacemaker |
| `whisper-turbo` | koan, if you agree, then you're still attached to the sense of manner. If you do not agree... Then you're forever sunk in |
| `whisper-turbo+ctx` | As far as the last line of the koan, if you agree, then you're still attached to the sentiment. If you do not |

**Shariputra** — `30671_b01435` at 4:12 · John Daido Loori · 1980s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | the brain works linearly and sequentially and we grasp things dualistically relatively our whole definition of the universe is based on that relativity everything is known in reference to something else it's one big reference system i remember when i began to realize that in science i mean i used to think of science for 17 years that was my field science it was my god and then i realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `parakeet-ft-v1+vad90` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean I used to think of science for 17 years that was my field science it was my God and then I realized one day the whole thing just back and forth referring to different reference systems what's the absolute basis of |
| `parakeet-v3` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost0.3f` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost0.5` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `parakeet-v3+boost1` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day, the whole thing. Just back and forth, referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think it's science for seventeen years. That was my field, science. It was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+ctx` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think it's science for 17 years. That was my field, science. It was my god. And then I realized one day, the whole thing is just back and forth referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+vad` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that science. I mean, I used to think that science, for 17 years, that was my field, science, that was my guide. And then I realized one day, the whole thing is just back and forth, referring to different reference systems. What's the absolute basis of |
| `qwen3-asr-1.7b+vad+terms` | the brain works linearly and sequentially, and we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science, for 17 years, that was my field, science, that was my guide. And then I realized one day, the whole thing is just back and forth, referring to different reference systems. What's the absolute basis of |
| `whisper-large-v3` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think that science for 17 years, that was my field, science. It was my God. And then I realized one day, the whole thing just... back and forth referring to different reference systems what's the absolute basis of |
| `whisper-large-v3+ctx` | the brain works linearly and sequentially. Avalokitesvara, jukai, Eno, and Shariputra. Back and forth, referring to different references. What's the absolute basis of |
| `whisper-turbo` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my God. And then I realized one day the whole thing just... back and forth referring to different reference systems what's the absolute basis of |
| `whisper-turbo+ctx` | the brain works linearly and sequentially. And we grasp things dualistically, relatively. Our whole definition of the universe is based on that relativity. Everything is known in reference to something else. It's one big reference system. I remember when I began to realize that in science. I mean, I used to think of science for 17 years. That was my field, science. It was my god. And then I realized one day the whole thing just... Back and forth, referring to different reference systems. What's the absolute basis of |

**Shakyamuni** — `36533_s00180` at 2:25 · John Daido Loori · 2000s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | Dogen says let us offer flowers of the distant mountains to the Tathagatha or share the treasures with all sentient beings and spiritual things as well as material things when the way is surrendered to the way you attain the way upon being awakened you necessarily let the way come through itself the self the self gives the self for the sake of giving the self the other gives the other for the sake of giving |
| `parakeet-ft-v1+vad90` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost0.3f` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost0.5` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `parakeet-v3+boost1` | Dogan says, let us offer flowers of the distant mountains to the Tathagatha, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+ctx` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+vad` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `qwen3-asr-1.7b+vad+terms` | Dogen says, "Let us offer flowers of the distant mountains to the Tathagata, or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-large-v3` | Dogen says, let us offer flowers of the distant mountains to the Tathagata. or share the treasures with all sentient beings in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |
| `whisper-large-v3+ctx` | Dogen says, let us offer flowers of the distant mountains to the tathagata. The other gives the other for the sake of giving |
| `whisper-turbo` | Dogen says let us offer flowers of the distant mountains to the Tathagatha or share the treasures with all sentient beings in spiritual things as well as material things when the way is surrendered to the way you attain the way upon being awakened you necessarily let the way come through itself the self gives the self for the sake of giving the self the other gives the other for the sake of giving |
| `whisper-turbo+ctx` | Dogen says let us offer flowers of the distant mountains to the tathagata. Or share the treasures with all sentient beings, in spiritual things as well as material things. When the way is surrendered to the way, you attain the way. Upon being awakened, you necessarily let the way come through itself. The self gives the self for the sake of giving the self. The other gives the other for the sake of giving |

**gassho** — `35549_s00390` at 3:01 · Bonnie Myotai Treace · 1990s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | experience. Have you experienced that? Have you experienced acting on the world? Gatha not. Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-ft-v1+vad90` | experience. Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-v3` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody? Ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost0.3f` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost0.5` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `parakeet-v3+boost1` | experience? Have you experienced that? Have you experienced acting on the world? Gasho, not. Anybody ever entered a situation, a moment, a relationship? |
| `qwen3-asr-1.7b` | experience. Have you experienced that? Have you experienced acting on the world, ghasho not? Anybody ever enter a situation, a moment of relationship? |
| `qwen3-asr-1.7b+ctx` | experience. Have you experienced that? Have you experienced acting on the world gassho not? Anybody ever enter a situation, a moment, a relationship? |
| `qwen3-asr-1.7b+vad` | experience. Have you experienced that? Have you experienced acting on the world? Ghasho not. Anybody ever entered a situation, a moment, a relationship? |
| `qwen3-asr-1.7b+vad+terms` | experience. Have you experienced that? Have you experienced acting on the world? Gassho not. Anybody ever entered a situation, a moment, a relationship? |
| `whisper-large-v3` | experience have you experienced that have you experienced acting on the world gassho not anybody Ever entered a situation, a moment, a relationship? |
| `whisper-large-v3+ctx` | experience. Have you experienced that? Have you experienced acting on the world? Gassho not. Anybody? Ever entered a situation, a moment, a relationship? |
| `whisper-turbo` | experience have you experienced that have you experienced acting on the world gacho not anybody Ever entered a situation, a moment, a relationship? |
| `whisper-turbo+ctx` | experience. Have you experienced that? Have you experienced acting on the world, gassho, not? Anybody? Ever entered a situation, a moment, a relationship? |

**sangha** — `34736_s02010` at 1:44 · Ron Hogen Green · 2020s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-ft-v1+vad90` | Buddha I take refuge in the Dharma I take refuge in the Sangha I take refuge in the Buddha the incomparably honored one |
| `parakeet-v3` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost0.3f` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost0.5` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `parakeet-v3+boost1` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b+ctx` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `qwen3-asr-1.7b+vad` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparable honored one. |
| `qwen3-asr-1.7b+vad+terms` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparable honored one. |
| `whisper-large-v3` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. |
| `whisper-large-v3+ctx` | Buddha. I take refuge in the dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo` | Buddha. I take refuge in the Dharma. I take refuge in the Sangha. I take refuge in the Buddha, the incomparably honored one. |
| `whisper-turbo+ctx` | Buddha. I take refuge in the Dharma. I take refuge in the sangha. I take refuge in the Buddha, the incomparably honored one. |

**ango** — `34775_s01976` at 3:04 · Jody Hojin Kimmel · 2020s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | of all my fear and all of my you know like no way and so and I keep coming too I walk in the door for session I feel like I'm getting an infusion like I need an infusion and and so and every session you know I'll be sitting and I don't |
| `parakeet-ft-v1+vad90` | of all my fear and all of my you know I like no way um and so um and and I keep coming too I I I walk in the door for session I feel like I'm getting an infusion like I need an infusion and um and so and every session you know I'll I'll be sitting and and I don't |
| `parakeet-v3` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too, I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost0.3f` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too. I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost0.5` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too. I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `parakeet-v3+boost1` | of all my fear and all of my, you know, I like no way. Um and so um and and I keep coming too, I I I walk in the door for session, I feel like I'm getting an infusion, like I need an infusion. And um and so and every session, you know, I'll I'll be sitting and and I don't |
| `qwen3-asr-1.7b` | of all my fear and all of my, you know, like no way. And so, and and I keep coming too. I I walk in the door for session. I feel like I'm getting an infusion. Like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+ctx` | of all my fear and all of my, you know, like no way. And so, and and I keep coming too. I I walk in the door for session. I feel like I'm getting an infusion. Like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+vad` | of all my fear and all of my, you know, I like no way. And so, and and I keep coming to. I I walk in the door for session. I feel like I'm getting infusion, like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `qwen3-asr-1.7b+vad+terms` | of all my fear and all of my, you know, I like no way. And so, and and I keep coming to. I I walk in the door for session. I feel like I'm getting infusion, like I need an infusion, and and so and every session, you know, I'll be sitting and and I don't |
| `whisper-large-v3` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for session. I feel like I'm getting an infusion, like I need an infusion. And so, and every session, you know, I'll be sitting, and I don't |
| `whisper-large-v3+ctx` | of all my fear and all of my We'll be talking about ango, Sozan, and zmm .org. We'll be talking about ango, Sozan, |
| `whisper-turbo` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for session. I feel like I'm getting an infusion, like I need an infusion. And so, and every session, you know, I'll be sitting, and I don't |
| `whisper-turbo+ctx` | of all my fear and all of my... You know, like, no way. And so, and I keep coming, too. I walk in the door for Sashen, I feel like I'm getting an infusion, like I need an infusion. And so, and every Sashen, you know, I'll be sitting and I don't |

**karma** — `33782_s02428` at 5:54 · Ron Hogen Green · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | to. Um, and that's our responsibility. And there's a karma from that. |
| `parakeet-ft-v1+vad90` | to. And that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3` | to. Um and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost0.3f` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost0.5` | to. Um, and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `parakeet-v3+boost1` | to. Um and that's our responsibility. And there's a karma for that. And a karma came out of all of those things. |
| `qwen3-asr-1.7b` | to, and that's our responsibility. And there's a karma for that, and a karma came out of all of those things. |
| `qwen3-asr-1.7b+ctx` | to, and that's our responsibility. And there's a karma for that, and a karma came out of all of those things. |
| `qwen3-asr-1.7b+vad` | to, and that's our responsibility. And there's a karma for that, and karma came out of all of those things. |
| `qwen3-asr-1.7b+vad+terms` | to, and that's our responsibility. And there's a karma for that, and karma came out of all of those things. |
| `whisper-large-v3` | to. And that's our responsibility. And there's a karma from that. Karma came out of all of those things. |
| `whisper-large-v3+ctx` | to. And that's our responsibility. And there's a karma from that. Karma came out of all of those things. |
| `whisper-turbo` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |
| `whisper-turbo+ctx` | to. And that's our responsibility. And there's a karma for that. Karma came out of all of those things. |

**Konrad Ryushin Marchaj** — `29973_s00810` at 4:32 · Konrad Ryushin Marchaj · 2010s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | through and expose the fallacy of all the laws of nature. As you can sense I was mentioning yesterday, every koan in a sense is |
| `parakeet-ft-v1+vad90` | through and expose the fallacy of all the laws of nature. Mr. Vincenzo was mentioning yesterday, every koan in a sense is |
| `parakeet-v3` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost0.3f` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost0.5` | through and expose the fallacy of all the laws of nature. |
| `parakeet-v3+boost1` | through and expose the fallacy of all the laws of nature. |
| `qwen3-asr-1.7b` | through and expose the fallacy of all the laws of nature. This reminds me, I was mentioning yesterday, every koan in a sense is |
| `qwen3-asr-1.7b+ctx` | through and expose the fallacy of all the laws of nature. The Shoben Sensei was mentioning yesterday. Every koan, in a sense, is |
| `qwen3-asr-1.7b+vad` | through and expose the falsity of all the laws of nature. The Sri Venanda was mentioning yesterday every koan in a sense is |
| `qwen3-asr-1.7b+vad+terms` | through and expose the falsity of all the laws of nature. The Shubhendra was mentioning yesterday every koan in a sense is |
| `whisper-large-v3` | through and expose the fallacy of all the laws of nature. As Ruben Sanza was mentioning yesterday, every koan, in a sense, is |
| `whisper-large-v3+ctx` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo` | through and expose the fallacy of all the laws of nature. As you can sense, I was mentioning yesterday, every koan, in a sense, is |
| `whisper-turbo+ctx` | through and expose the fallacy of all the laws of nature. As Ryushin Sensei was mentioning yesterday, every koan, in a sense, is |

**Bodhidharma** — `31369_b00637` at 2:00 · John Daido Loori · 1980s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | it possible to listen to the buddhadharma the master replied the buddhadharma cannot be attained by following others that is one has to |
| `parakeet-ft-v1+vad90` | it possible to listen to the Buddha Dharma? The master replied, the Buddha Dharma cannot be attained by following others. That is, one has to |
| `parakeet-v3` | it possible to listen to the Buddha Dharma? The master replied, The Buddha Dharma cannot be attained by following others. That is, one has to |
| `parakeet-v3+boost0.3f` | it possible to listen to the Buddha Dharma? The master replied, The Buddha Dharma cannot be attained by following others. That is, one has to |
| `parakeet-v3+boost0.5` | it possible to listen to the Buddha Dharma? The master replied, The Buddha Dharma cannot be attained by following others. That is, one has to |
| `parakeet-v3+boost1` | it possible to listen to the Buddha Dharma? The master replied, The Buddha Dharma cannot be attained by following others. That is, one has to |
| `qwen3-asr-1.7b` | it possible to listen to the Buddha Dharma?" The master replied, "The Buddha Dharma cannot be attained by following others. That is, one has to |
| `qwen3-asr-1.7b+ctx` | it possible to listen to the Buddha Dharma?" The master replied, "The Buddha Dharma cannot be attained by following others. That is, one has to |
| `qwen3-asr-1.7b+vad` | it possible to listen to the Buddha Dharma?" The master replied, "The Buddha Dharma cannot be attained by following others. That is, one has to |
| `qwen3-asr-1.7b+vad+terms` | it possible to listen to the Buddha Dharma?" The master replied, "The Buddha Dharma cannot be attained by following others. That is, one has to |
| `whisper-large-v3` | it possible to listen to the Buddha Dharma? The master replied, The Buddha Dharma cannot be attained by following others. That is, one has to |
| `whisper-large-v3+ctx` | it possible to listen to the Bodhidharma? The master replied, The Bodhidharma cannot be attained by following others. That is, one has to |
| `whisper-turbo` | it possible to listen to the Buddha Dharma? The master replied, the Buddha Dharma cannot be attained by following others. That is, one has to |
| `whisper-turbo+ctx` | it possible to listen to the Buddhadharma? The master replied, the Buddhadharma cannot be attained by following others. That is, one has to |

## Agreement between systems

Word error rate of each row's output measured against each column's output, on speech clips. Systems that agree closely are making the same choices, not necessarily the right ones.

| | `legacy-whisper-cli` | `parakeet-ft-v1+vad90` | `parakeet-v3` | `parakeet-v3+boost0.3f` | `parakeet-v3+boost0.5` | `parakeet-v3+boost1` | `qwen3-asr-1.7b` | `qwen3-asr-1.7b+ctx` | `qwen3-asr-1.7b+vad` | `qwen3-asr-1.7b+vad+terms` | `whisper-large-v3` | `whisper-large-v3+ctx` | `whisper-turbo` | `whisper-turbo+ctx` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | · | 6% | 9% | 9% | 8% | 8% | 9% | 9% | 9% | 10% | 7% | 15% | 7% | 8% |
| `parakeet-ft-v1+vad90` | 7% | · | 5% | 5% | 5% | 5% | 6% | 7% | 6% | 7% | 6% | 13% | 6% | 7% |
| `parakeet-v3` | 8% | 4% | · | 1% | 1% | 1% | 8% | 9% | 8% | 9% | 7% | 14% | 7% | 8% |
| `parakeet-v3+boost0.3f` | 8% | 4% | 1% | · | 1% | 1% | 8% | 9% | 8% | 9% | 7% | 14% | 7% | 8% |
| `parakeet-v3+boost0.5` | 8% | 4% | 1% | 1% | · | 1% | 8% | 9% | 7% | 9% | 7% | 14% | 7% | 8% |
| `parakeet-v3+boost1` | 8% | 4% | 1% | 1% | 1% | · | 8% | 8% | 7% | 9% | 7% | 14% | 7% | 8% |
| `qwen3-asr-1.7b` | 8% | 6% | 8% | 8% | 8% | 8% | · | 3% | 4% | 6% | 7% | 15% | 8% | 9% |
| `qwen3-asr-1.7b+ctx` | 9% | 7% | 9% | 9% | 9% | 9% | 3% | · | 5% | 6% | 8% | 15% | 8% | 9% |
| `qwen3-asr-1.7b+vad` | 8% | 6% | 8% | 8% | 7% | 7% | 4% | 5% | · | 2% | 7% | 14% | 7% | 8% |
| `qwen3-asr-1.7b+vad+terms` | 10% | 7% | 9% | 9% | 9% | 9% | 6% | 6% | 2% | · | 9% | 15% | 9% | 9% |
| `whisper-large-v3` | 8% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | · | 9% | 2% | 3% |
| `whisper-large-v3+ctx` | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 14% | 13% | 14% | 8% | · | 9% | 8% |
| `whisper-turbo` | 7% | 6% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 8% | 2% | 9% | · | 2% |
| `whisper-turbo+ctx` | 8% | 7% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 3% | 9% | 2% | · |

## Clips with repetition loops

- `legacy-whisper-cli`: `30643_s01710`, `31043_s04042`, `36192_s02610`
- `parakeet-ft-v1+vad90`: `36192_s02610`
- `parakeet-v3`: `36192_s02610`
- `parakeet-v3+boost0.3f`: `36192_s02610`
- `parakeet-v3+boost0.5`: `36192_s02610`
- `parakeet-v3+boost1`: `36192_s02610`
- `qwen3-asr-1.7b+ctx`: `30643_s01710`
- `whisper-large-v3`: `36192_s02610`

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
