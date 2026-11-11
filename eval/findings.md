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

14. **Changes to the silver-reference pipeline suggested by this:**
    - In ties, prefer dictionary words and glossary terms ("oxherding" over "oxerting"), and on content words prefer the family that's most often right.
    - Strip possessives before glossary lookups, so "Yunmin's" becomes "Yunmen's".
    - Treat "book differs" as information only.
    - Adopt the book's spelling when it is close to the reference word ("sequential").
    - Add new misheard forms: Unman → Ummon, Tiknad Han → Thich Nhat Hanh.

### Recommendation (provisional)

- **Production default:** faster-whisper **turbo + per-talk prompt + VAD**. It has the most precise context (about 95%), the best term spelling and the best speed.
- **Fix before production:** turbo's phrase drops (about 2.4% of words). Test VAD settings, then smaller batches. A second system can fill the gaps: parakeet-ft-v1 is fast and rarely drops a phrase.
- **Upgrade if WER supports it:** **Qwen3-ASR + VAD + term list**, for difficult talks or a full cloud run. Its term list is less precise (about 68%).
- **Not recommended as configured:**
  - large-v3 with a prompt, which is mostly insertions
  - Qwen with a prose prompt, which echoes and inserts
  - Parakeet's gentle boost, which does almost nothing
- **Before deciding,** correct about 15–20 references (see `eval/CONVENTIONS.md`) and re-run `eval/report.py`. That adds WER, term recall and false insertions with confidence intervals. The A10 run adds three more voter families to the silver references.
