# ASR bake-off

_Generated 2026-11-10 06:19 by `eval/report.py`. Re-run after adding systems or references._

**Gold set:** 38 speech excerpts (3.8 h, one per talk, stratified by era / speaker / content / audio difficulty) and 76 non-speech clips (38 min of bells, silence and room noise where VAD finds <10% speech). **Corrected references: 0/38.**

## Findings

_Hand-written interpretation (`eval/findings.md`, last edited 2026-11-10). The tables below are regenerated each run; re-check this section when they change._

These notes are based on 13 systems, 38 speech excerpts (3.8 h) and 76 non-speech clips. **No references have been corrected yet, so no system has an accuracy number.** Everything below comes from metrics that don't need a reference, plus listening to the side-by-side examples. Treat the ranking as provisional until WER is in.

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

### Recommendation (provisional)

- **Production default:** faster-whisper **turbo + per-talk prompt + VAD**. It's fast, safe, and gives most of the term gains.
- **Upgrade if WER supports it:** **Qwen3-ASR + VAD + term list**, for difficult talks or a full cloud run.
- **Not recommended as configured:** large-v3 with a prompt, unless the echo is detected and retried, and Parakeet with boosting until references show the boost helps more than it hurts.
- **Before deciding,** correct about 15–20 references (see `eval/CONVENTIONS.md`) and re-run `eval/report.py`. That adds WER, term recall and false insertions with confidence intervals.

> **Accuracy (WER) is not measured yet.** No corrected references exist, so this report shows only what can be measured without them: speed, hallucination on non-speech, how each system spells glossary terms, repetition loops, and agreement between systems. Correct the drafts in `eval/goldset/drafts/` into `eval/goldset/refs/` (see `eval/CONVENTIONS.md`) and re-run to add WER, term recall and per-stratum results.

## Systems

| System | Model | Context | Device | Speed (× real time) | GPU peak | Archive time on this PC* |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | openai-whisper CLI turbo (existing transcripts) | — | unknown | — | — | — |
| `parakeet-v3` | nvidia/parakeet-tdt-0.6b-v3 | — | cuda | 224 | 5045 MB | 1.2 days |
| `parakeet-v3+boost0.3f` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.3, hard terms (difficulty>=0.15, with evidence) | cuda | 192 | 5024 MB | 1.4 days |
| `parakeet-v3+boost0.5` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=0.5, top 40 talk terms | cuda | 193 | 5023 MB | 1.4 days |
| `parakeet-v3+boost1` | nvidia/parakeet-tdt-0.6b-v3 | phrase boosting alpha=1.0, top 40 talk terms | cuda | 193 | 5023 MB | 1.4 days |
| `qwen3-asr-1.7b` | Qwen/Qwen3-ASR-1.7B | — | cuda | 17 | 5180 MB | 15.6 days |
| `qwen3-asr-1.7b+ctx` | Qwen/Qwen3-ASR-1.7B | system prompt = talk prompt | cuda | 18 | 5220 MB | 15.0 days |
| `qwen3-asr-1.7b+vad` | Qwen/Qwen3-ASR-1.7B | — | cuda | 22 | 5016 MB | 12.4 days |
| `qwen3-asr-1.7b+vad+terms` | Qwen/Qwen3-ASR-1.7B | system prompt = hard-term list | cuda | 22 | 5218 MB | 12.4 days |
| `whisper-large-v3` | faster-whisper large-v3 | — | cuda | 64 | 4441 MB | 4.2 days |
| `whisper-large-v3+ctx` | faster-whisper large-v3 | hotwords=talk prompt | cuda | 60 | 4762 MB | 4.6 days |
| `whisper-turbo` | faster-whisper large-v3-turbo | — | cuda | 153 | 3337 MB | 1.8 days |
| `whisper-turbo+ctx` | faster-whisper large-v3-turbo | hotwords=talk prompt | cuda | 152 | 3325 MB | 1.8 days |

\* 6,500 h of audio at the measured speed on short clips (includes per-clip overhead, so full talks run somewhat faster). `legacy-whisper-cli` = the existing transcripts (Whisper CLI turbo, no VAD, no prompt, `condition_on_previous_text=True`).

## Summary

| System | Non-speech clips with invented text | Glossary terms misheard | Prompt echo | Loops | Words/min | Punct./100 words |
|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | 76/76 (100%) | 11.2% (41 of 367) | — | 3 | 117 | 15.1 |
| `parakeet-v3` | 4/76 (5%) | 13.7% (42 of 306) | — | 1 | 114 | 15.5 |
| `parakeet-v3+boost0.3f` | 7/76 (9%) | 13.0% (40 of 307) | 0 clips | 1 | 114 | 15.5 |
| `parakeet-v3+boost0.5` | 5/76 (7%) | 11.0% (35 of 318) | 0 clips | 1 | 114 | 15.6 |
| `parakeet-v3+boost1` | 5/76 (7%) | 11.0% (36 of 328) | 0 clips | 1 | 114 | 15.5 |
| `qwen3-asr-1.7b` | 74/76 (97%) | 2.3% (7 of 304) | — | 0 | 114 | 16.7 |
| `qwen3-asr-1.7b+ctx` | 74/76 (97%) | 1.9% (8 of 417) | 5 clips (1.8% of audio) | 1 | 115 | 16.6 |
| `qwen3-asr-1.7b+vad` | 7/76 (9%) | 2.2% (7 of 318) | — | 0 | 113 | 16.7 |
| `qwen3-asr-1.7b+vad+terms` | 7/76 (9%) | 1.7% (6 of 356) | 0 clips | 0 | 115 | 16.5 |
| `whisper-large-v3` | 7/76 (9%) | 7.4% (26 of 351) | — | 1 | 110 | 16.1 |
| `whisper-large-v3+ctx` | 7/76 (9%) | 1.9% (8 of 411) | 12 clips (2.3% of audio) | 0 | 104 | 17.0 |
| `whisper-turbo` | 7/76 (9%) | 13.0% (47 of 361) | — | 0 | 111 | 16.2 |
| `whisper-turbo+ctx` | 7/76 (9%) | 3.2% (12 of 378) | 0 clips | 0 | 110 | 16.7 |

How to read this:
- **Non-speech clips with invented text**: any words output on a clip with no speech. All of them are errors, so lower is better. Most of these clips were *chosen* at spots where the legacy transcripts invented text, so legacy's score there is near 100% by construction. Compare the new systems with each other.
- **Glossary terms misheard**: share of glossary hits that use a known *wrong* spelling ("Yakujo" for Hyakujo, "doksan" for dokusan). Lower is better. This only counts misspellings already listed in the glossary, and a prompt can push the share down by inserting terms that weren't said, so check it against the false-insertion column once references exist.
- **Prompt echo**: speech clips where a stretch of output repeats the context prompt instead of what was said (the speech there is lost), and the share of speech audio replaced that way. Only systems given a prompt or term list can do this; any non-zero value is serious.
- **Loops**: speech clips where the output repeats a phrase over and over (a classic Whisper failure).
- **Words/min**: big differences from the other systems suggest dropped audio or invented text.

## Effect of per-talk context

| Base → variant | Misheard terms: base → variant | Non-speech output: base → variant | Disagreement between the two |
|---|---|---|---|
| `parakeet-v3` → `parakeet-v3+boost0.3f` | 13.7% → 13.0% | 4 → 7 clips | 1.0% of words |
| `parakeet-v3` → `parakeet-v3+boost0.5` | 13.7% → 11.0% | 4 → 5 clips | 1.1% of words |
| `parakeet-v3` → `parakeet-v3+boost1` | 13.7% → 11.0% | 4 → 5 clips | 1.1% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+ctx` | 2.3% → 1.9% | 74 → 74 clips | 2.8% of words |
| `qwen3-asr-1.7b` → `qwen3-asr-1.7b+vad` | 2.3% → 2.2% | 74 → 7 clips | 3.8% of words |
| `qwen3-asr-1.7b+vad` → `qwen3-asr-1.7b+vad+terms` | 2.2% → 1.7% | 7 → 7 clips | 2.8% of words |
| `whisper-large-v3` → `whisper-large-v3+ctx` | 7.4% → 1.9% | 7 → 7 clips | 8.6% of words |
| `whisper-turbo` → `whisper-turbo+ctx` | 13.0% → 3.2% | 7 → 7 clips | 2.2% of words |

Disagreement is the word error rate between the two outputs: how much of the text the context changed.

## Most frequent misheard glossary terms

| System | Top known misspellings in its output |
|---|---|
| `legacy-whisper-cli` | Zhao, Yakujo, Maizumi, doksan, Shapa, Daito, Ingo, Huiko, Ongan, Setsho, Zazengi, Wutsu |
| `parakeet-v3` | gasho, Yakujo, Mizumi, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, Orioki, Secho, seshin |
| `parakeet-v3+boost0.3f` | gasho, Mizumi, Yakujo, dogan, Ingo, Mayakaya Shapa, Shapa, kohan, doksan, Orioki, Secho, seshin |
| `parakeet-v3+boost0.5` | gasho, Yakujo, Mizumi, Mayakaya Shapa, Shapa, doksan, Orioki, Secho, Ingo, seshin, Ongo, Zazengi |
| `parakeet-v3+boost1` | gasho, Yakujo, Mizumi, Mayakaya Shapa, Shapa, doksan, Orioki, Secho, Ingo, seshin, Ongo, Zazengi |
| `qwen3-asr-1.7b` | Mazumi, Ongo, seshin, doksan, Zhao |
| `qwen3-asr-1.7b+ctx` | Shapa, Mazumi, Ongo, doksan |
| `qwen3-asr-1.7b+vad` | Shapa, doksan, Ongo, Doxan |
| `qwen3-asr-1.7b+vad+terms` | doksan, Dogon |
| `whisper-large-v3` | Yakujo, Maizumi, doksan, Shapa, Huiko, Daito, Setsho, Ingo, Mayakaya Shapa, Mizumi, Yunmin, Ongo |
| `whisper-large-v3+ctx` | Shapa, Mayakaya Shapa, Zenda |
| `whisper-turbo` | doksan, Yakujo, gasho, Shapa, Maizumi, Gashow, Mayakaya Shapa, Huiko, Daito, Zhao, Ingo, Setsho |
| `whisper-turbo+ctx` | Shapa, Yakujo, Mayakaya Shapa, Sashen, seshin, Zenda |

## What systems output on non-speech

- `legacy-whisper-cli`: "Thank you."×73; "thank you"×3
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

**Muge Daido** — `37196_s01410` at 5:29 · Konrad Ryushin Marchaj · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | of the teachings now of Zen, of Tantra, of Mahayana, of Tibet, that's where it opens up. You know, this is your oyster. |
| `parakeet-v3` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your obstructions. |
| `parakeet-v3+boost0.3f` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your obstructions. |
| `parakeet-v3+boost0.5` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your obstructions. |
| `parakeet-v3+boost1` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your obstructions. |
| `qwen3-asr-1.7b` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your abstractions. |
| `qwen3-asr-1.7b+ctx` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your abstractions. |
| `qwen3-asr-1.7b+vad` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your abstractions. |
| `qwen3-asr-1.7b+vad+terms` | specific containers. If you understand what's going on, every aspect of your life is going to be useful. You're going to be able to use your relationships, your abstractions. |
| `whisper-large-v3` | of the teachings now of Zen, of Tantra, of Mahayana, of Tibet, that's where it opens up. You know, this is your oyster. |
| `whisper-large-v3+ctx` | Daido, and Mazu. Attention! -1. We'll be talking about Fukanzazengi, Daido, and Mazu. Attention! -1. We'll be talking about Fukanzazengi, Daido, and Mazu. |
| `whisper-turbo` | of the teachings now of Zen, of Tantra, of Mahayana, of Tibet, that's where it opens up. You know, this is your oyster. |
| `whisper-turbo+ctx` | of the teachings now of Zen, of Tantra, of Mahayana, of Tibet, that's where it opens up. You know, this is your oyster. |

**koan** — `31311_s00180` at 1:36 · John Daido Loori · 1980s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | these things are meant to eliminate the point of the koan, the point that's being made in the koan. And in this pointer, |
| `parakeet-v3` | these things are meant to illuminate the point of the Koan, the point that's being made in the Koan. And in this pointer |
| `parakeet-v3+boost0.3f` | these things are meant to illuminate the point of the Koan, the point that's being made in the Koan. And in this pointer |
| `parakeet-v3+boost0.5` | these things are meant to illuminate the point of the Koan, the point that's being made in the koan. And in this pointer |
| `parakeet-v3+boost1` | these things are meant to illuminate the point of the Khan, the point that's being made in the koan. And in this pointer |
| `qwen3-asr-1.7b` | these things are meant to illuminate the point of the koan, the point that's being made in the koan. And in this pointer, |
| `qwen3-asr-1.7b+ctx` | these things are meant to illuminate the point of the koan, the point that's being made in the koan. And in this pointer, |
| `qwen3-asr-1.7b+vad` | these things are meant to illuminate the point of the koan, the point that's being made in the koan. And in this pointer, |
| `qwen3-asr-1.7b+vad+terms` | these things are meant to illuminate the point of the koan, the point that's being made in the koan. And in this pointer, |
| `whisper-large-v3` | these things are meant to illuminate the point of the koan. the point that's being made in the koan. And in this pointer, |
| `whisper-large-v3+ctx` | these things are meant to illuminate the point of the koan. The point that's being made in the koan. And in this pointer, |
| `whisper-turbo` | these things are meant to illuminate the point of the koan. The point that's being made in the koan. And in this pointer, |
| `whisper-turbo+ctx` | these things are meant to illuminate the point of the koan. The point that's being made in the koan. And in this pointer, |

**Deshan Xuanjian** — `34004_s01972` at 1:05 · Other · 1990s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | well. Attention. Shuso, you and I had a meal shift together. You were sweeping under the pizza oven and you swept down a little critter and it was caught in flypaper and you ran over in a panic. I don't know if it's dead or alive. There's something in the flypaper. What's the constant principle of that? May your life go well. Attention. First, I want to let you know I've never done this before so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of matter. If you do not agree, |
| `parakeet-v3` | well. Attention. Justo, you and I had a meal shift together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran |
| `parakeet-v3+boost0.3f` | well. Attention. Justo, you and I had a meal shift together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, |
| `parakeet-v3+boost0.5` | well. Attention. Justo, you and I had a meal shift together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. As far as the last line of the call on it, if you agree, |
| `parakeet-v3+boost1` | well. Attention. Justo, you and I had a meal shift together, and you were sweeping under the pizza oven, and you swept down a little critter that was caught in fly paper, and you ran it over in a panic. Uh I don't know if it's dead or alive. There's something in the fly paper. What's the constant principle for that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the call on it, if you agree, |
| `qwen3-asr-1.7b` | well. Attention. Just so you and I had a meal shift together, you were sweeping under the pizza oven and you swept out little critters. Caught in the flypaper, and you ran over a pan. I don't think there's a lot. There's there's something in the flypaper. What's the constant principle? That. May your life go well. Attention. So I want to let you know I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you |
| `qwen3-asr-1.7b+ctx` | well. Attention. Just so you and I had a meal shift together. You were sweeping under the pizza oven and you swept out little critters. Caught in the fly paper. You ran over a pan. I don't think there's a lot. There's there's something in the fly paper. What's the constant principle? That. May your life go well. Attention. Just so I let you know, I've never done this before, so I'm actually in kinder. As far as the last line of the poem, if you |
| `qwen3-asr-1.7b+vad` | well. Attention, Queso. You and I had a meal shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm nervous. As |
| `qwen3-asr-1.7b+vad+terms` | well. Attention, Quito. You and I had a meal shift together. You were sweeping up a pizza oven, and you swept down a little critter that was caught in the flypaper. You ran over, panicked. I don't think there's a lie. There's something in the flypaper. What's the constant principle? May your life go well. Attention. I just want to let you know I've never done this before. So naturally, I'm not nervous. As |
| `whisper-large-v3` | well. caught in flypaper and ran over in a panic. I don't know if it's dead or alive. There's something in the flypaper. What's the constant principle of that? May your life go well. Attention. Chris, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of matter. If you do not agree... |
| `whisper-large-v3+ctx` | well. We'll be talking about John Daido Loori, Bernie Glassman, Tokusan, Zen Peacemaker Order, and Ganto. We'll be talking about John Daido Loori, |
| `whisper-turbo` | well. caught in flypaper and ran over in a panic. I don't know if it's dead or alive. There's something in the flypaper. What's the constant principle of that? May your life go well. Attention. First, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the sense of manner. If you do not agree... |
| `whisper-turbo+ctx` | well. May your life go well. Attention. Chris, I want to let you know I've never done this before, so I'm actually being kind of nervous. As far as the last line of the koan, if you agree, then you're still attached to the |

**Huangbo Xiyun** — `35351_s00900` at 2:10 · Geoffrey Shugen Arnold · 1990s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | mind? That Vasa was pointing to. A monk asked Master Obaku, From earliest times, all the masters say mind is Buddha. I wonder |
| `parakeet-v3` | mind that Basava is pointing to? Monk asks Master Obaku, from earliest times all the masters say mind is Buddha. I wonder |
| `parakeet-v3+boost0.3f` | mind that Basava is pointing to? Monk asks Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |
| `parakeet-v3+boost0.5` | mind? Monk asks Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |
| `parakeet-v3+boost1` | mind that Basava is pointing to? Monk asks Master Obaku, from earliest times all the masters say mind is Buddha. I wonder |
| `qwen3-asr-1.7b` | mind? The master was pointing to. A monk asked Master Obaku, "From earliest times, all the masters say mind is Buddha. I wonder |
| `qwen3-asr-1.7b+ctx` | mind? The boss was pointing to. A monk asked Master Obaku, "From earliest times, all the masters say mind is Buddha. I wonder |
| `qwen3-asr-1.7b+vad` | mind? The bossa was pointing to. A monk asked Master Obaku, "From earliest times, all the masters say mind is Buddha. I wonder |
| `qwen3-asr-1.7b+vad+terms` | mind? The bossa was pointing to. A monk asked Master Obaku, "From earliest times, all the masters say mind is Buddha. I wonder |
| `whisper-large-v3` | mind that Basava is pointing to? A monk asked Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |
| `whisper-large-v3+ctx` | mind that Mazu was pointing to? A monk asked Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |
| `whisper-turbo` | mind that Bhasa was pointing to? A monk asked Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |
| `whisper-turbo+ctx` | mind? Mazu was pointing to. A monk asked Master Obaku, from earliest times, all the masters say mind is Buddha. I wonder |

**dokusan** — `35934_s02640` at 5:04 · John Daido Loori · 2000s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | they don't even come to doksan because they don't do doksan in soto school the way we do it in the inside school and |
| `parakeet-v3` | there don't even come to Dokesan because they don't do Doksan in uh Soto school the way we do it in Rinsei School. And |
| `parakeet-v3+boost0.3f` | there don't even come to Dokesan because they don't do Doksan in uh soto school the way we do it in the Rinsei School. And |
| `parakeet-v3+boost0.5` | there don't even come to Dokesan because they don't do Doksan in uh Soto school the way we do it in the Rinzai School. And |
| `parakeet-v3+boost1` | there don't even come to Dokesan because they don't do Doksan in uh Soto school the way we do it in the Rinzai School. And |
| `qwen3-asr-1.7b` | they don't even come to dokusan because they don't do dokusan in Soto school. We do it in Rinzai school. And |
| `qwen3-asr-1.7b+ctx` | they don't even come to dokusan because they don't do dokusan in Soto school. We do it in Rinzai school, and |
| `qwen3-asr-1.7b+vad` | don't even come to Dogen because they don't do Dogen in Soto school the way we do it in Rinzai school. And |
| `qwen3-asr-1.7b+vad+terms` | don't even come to doksan because they don't do doksan in Soto school the way we do it in Rinzai school. And |
| `whisper-large-v3` | there don't even come to Doksang, because they don't do Doksang in Soto school the way we do it in Rinzai school. And |
| `whisper-large-v3+ctx` | there don't even come to dokusan, because they don't do dokusan in Soto school the way we do it in Rinzai school. And |
| `whisper-turbo` | there don't even come to doksan, because they don't do doksan in Soto school the way we do it in Rinzai school. And |
| `whisper-turbo+ctx` | there don't even come to dokusan, because they don't do dokusan in Soto school the way we do it in Rinzai school. And |

**sangha** — `34736_s02010` at 2:15 · Ron Hogen Green · 2020s · hard audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `parakeet-v3` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `parakeet-v3+boost0.3f` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `parakeet-v3+boost0.5` | taken refuge in the Dharma. I |
| `parakeet-v3+boost1` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `qwen3-asr-1.7b` | taken refuge in the Dharma. I have taken refuge in the Sangha. Take refuge in the Buddha. I have taken refuge |
| `qwen3-asr-1.7b+ctx` | taken refuge in the Dharma. I have taken refuge in the Sangha. Take refuge in the Buddha. I have taken refuge |
| `qwen3-asr-1.7b+vad` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `qwen3-asr-1.7b+vad+terms` | taken refuge in the Dharma. I have taken refuge in the Sangha. Take refuge in the Buddha. I have taken refuge |
| `whisper-large-v3` | Dharma I |
| `whisper-large-v3+ctx` | taken refuge in the Dharma. I have taken refuge in the Sangha. I have taken refuge in the Buddha. I have taken refuge |
| `whisper-turbo` | taken refuge in the Dharma. I have taken refuge in the Sangha. I take refuge in the Buddha. I have taken refuge |
| `whisper-turbo+ctx` | taken refuge in the dharma. I have taken refuge in the sangha. Refuge in the Buddha. I have taken refuge |

**Mahakashyapa** — `29973_s00810` at 2:48 · Konrad Ryushin Marchaj · 2010s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | predicated and harking to that, this moment. And so Mahakaya Shapa sees the form of the flower and smiles. seeing the form he |
| `parakeet-v3` | predicated. And harking to that, this moment. And so Mahakayashapa sees the form of the flower and smiles. Seeing the form, he |
| `parakeet-v3+boost0.3f` | predicated and harking to that, this moment. And so Mahakayashapa sees the form of the flower and smiles. Seeing the form, he |
| `parakeet-v3+boost0.5` | predicated. And harking to that, this moment. And so Mahakayashapa sees the form of the flower and smiles. Seeing the form, he |
| `parakeet-v3+boost1` | predicated and harking to that, this moment. And so Mahakayashapa sees the form of the flower and smiles. Seeing the form, he |
| `qwen3-asr-1.7b` | predicated and harking to that this moment. And so Mahakaya Shabha sees the form of the flower and smiles, seeing the form. He |
| `qwen3-asr-1.7b+ctx` | predicated. And harking to that, this moment. And so Mahakasyapa sees the form of the flower and smiles. Seeing the form, he |
| `qwen3-asr-1.7b+vad` | predicated and harking to that this moment. And so Mahakaya Shabas sees the form of the flower and smiles. Seeing the form, he |
| `qwen3-asr-1.7b+vad+terms` | predicated and harking to that this moment. And so Mahakasyapa sees the form of the flower and smiles. Seeing the form, he |
| `whisper-large-v3` | predicated and harking to that, this moment. And so Mahakaya Shapa sees the form of the flower and smiles. Seeing the form, he |
| `whisper-large-v3+ctx` | predicated and harking to that, this moment. And so Mahakaya Shapa sees the form of the flower and smiles. Seeing the form, he |
| `whisper-turbo` | predicated and harking to that, this moment. And so Mahakaya Shapa sees the form of the flower in smiles. Seeing the form, he |
| `whisper-turbo+ctx` | predicated and harking to that, this moment. And so Mahakaya Shapa sees the form of the flower in smiles. Seeing the form, he |

**zendo** — `35687_s00990` at 0:43 · Bonnie Myotai Treace · 1990s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | raised fist in the hut, this raised blind in the zendo? Akin says, Ultimately, Feiyan is not saying merely that gain is gain, |
| `parakeet-v3` | raised fist in the hut, this raised blind in the Zendo? Aiken says, ultimately Fayin is not saying merely that gain is gain, |
| `parakeet-v3+boost0.3f` | raised fist in the hut, this raised blind in the Zendo? Aiken says, ultimately Fayin is not saying merely that gain is gain, |
| `parakeet-v3+boost0.5` | raised fist in the hut, this raised blind in the Zendo? Aiken says ultimately Fayin is not saying merely that gain is gain, |
| `parakeet-v3+boost1` | raised fist in the hut, this raised blind in the zendo? Aiken says, ultimately Fayin is not saying merely that gain is gain, |
| `qwen3-asr-1.7b` | raised fist in the hut, this raised blind in the zendo? Aiken says, ultimately, Fayen is not saying merely that gain is gain, |
| `qwen3-asr-1.7b+ctx` | raised fist in the hut, this raised blind in the zendo? Akin says, ultimately Fayan is not saying merely that gain is gain, |
| `qwen3-asr-1.7b+vad` | raised fist in the hut, this raised blind in the zendo? Aiken says, ultimately, Fayen is not saying merely that gain is gain, |
| `qwen3-asr-1.7b+vad+terms` | raised fist in the hut, this raised blind in the zendo? Aiken says, ultimately, Fayen is not saying merely that gain is gain, |
| `whisper-large-v3` | raised fist in the hut, this raised blind in the zendo? Akin says, Ultimately, Fayan is not saying merely that gain is gain, |
| `whisper-large-v3+ctx` | raised fist in the hut, this raised blind in the zendo. Akin says, Ultimately, Feiyan is not saying merely that gain is gain, |
| `whisper-turbo` | raised fist in the hut, this raised blind in the zendo? Aiken says, Ultimately, Feyen is not saying merely that gain is gain, |
| `whisper-turbo+ctx` | raised fist in the hut, this raised blind in the zendo? Aiken says, Ultimately, Fayin is not saying merely that gain is gain, |

**gassho** — `35549_s00390` at 4:41 · Bonnie Myotai Treace · 1990s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | of gatha not. And how is that not requesting, not gatha? Because it presents that, first of all, the person who's trying to be happy doesn't have the ability to be at themselves, and they don't need to meet you. But there's a, there's a point at which you haven't requested entry into the reality |
| `parakeet-v3` | of gosho not. And how is that not requesting? Not gosha. Okay. But there's a there's a point at which you haven't requested entry into the reality |
| `parakeet-v3+boost0.3f` | of gosh o not. And how is that not requesting? Not Gosho. Okay. But there's a there's a point at which you haven't requested entry into the reality |
| `parakeet-v3+boost0.5` | of gosh o not. And how is that not requesting? Not Gosho. Okay. But there's a there's a point at which you haven't requested entry into the reality |
| `parakeet-v3+boost1` | of gosho not. And how is that not requesting? Not Gosho. Okay. But there's a there's a point at which you haven't requested entry into the reality |
| `qwen3-asr-1.7b` | of gasha not. And how is that not requesting, not gasha? But there's a there's a point at which you haven't requested entry into the reality |
| `qwen3-asr-1.7b+ctx` | of gassho, not. And how is that not requesting, not gassho? But there's a there's a point at which you haven't requested entry into the reality |
| `qwen3-asr-1.7b+vad` | of gasha. Not. And how is that not requesting? Not gasha. But there's a there's a point at which you haven't requested entry into the reality |
| `qwen3-asr-1.7b+vad+terms` | of gassho, not. And how is that not requesting, not gassho? But there's a there's a point at which you haven't requested entry into the reality |
| `whisper-large-v3` | of gassho not. And how is that not requesting? Not gassho. There's a point at which you haven't requested entry into the reality |
| `whisper-large-v3+ctx` | of gassho not. And how is that not requesting? Not gassho. There's a point at which you haven't requested entry into the reality |
| `whisper-turbo` | of gasho not. And how is that not requesting? Not gasho. There's a point at which you haven't requested entry into the reality |
| `whisper-turbo+ctx` | of gassho not. And how is that not requesting? Not gassho. But there's a point at which you haven't requested entry into the reality |

**dharma** — `31268_s00240` at 3:11 · John Daido Loori · 1980s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | with Nansen, deepening his understanding. Taifu was a student of this Dharma Master Joe, a scholar in the 5th century in China. And |
| `parakeet-v3` | with Nansen, deepening his understanding. Taifu was a student of this Dhamma Master Zhou, a scholar of the fifth century in China. During the walk with his deep. |
| `parakeet-v3+boost0.3f` | with Nansen, deepening his understanding. Typho was a student of this Dhamma Master Zhou, a scholar of the fifth century in China. |
| `parakeet-v3+boost0.5` | with Nansen, deepening his understanding. Typhoo was a student of this Dhamma Master Zhou, a scholar of the fifth century in China. |
| `parakeet-v3+boost1` | with Nansen, deepening his understanding. Typhoo was a student of this Dhamma Master Zhou, a scholar of the fifth century in China. |
| `qwen3-asr-1.7b` | with Nansen, deepening his understanding. Taifu was a student of the Dharma Master Joe, a scholar in the fifth century China. And |
| `qwen3-asr-1.7b+ctx` | with Nansen, deepening his understanding. Taifu was a student of the Dharma Master Joe, a scholar in the fifth century China. And |
| `qwen3-asr-1.7b+vad` | with Nansen, deepening his understanding. Taifu was a student of the Dharma Master Joe, a scholar of the fifth century China. And |
| `qwen3-asr-1.7b+vad+terms` | with Nansen, deepening his understanding. Taifu was a student of the Dharma Master Joe, a scholar of the fifth century China. And |
| `whisper-large-v3` | with Nansen, deepening his understanding. And Taifu was a student of this Dharma Master Joe, a scholar in the 5th century in China. And |
| `whisper-large-v3+ctx` | with Nansen, deepening his understanding. Taifu was a student of this Dharma Master Joe, a scholar in the 5th century in China. And |
| `whisper-turbo` | with Nansen, deepening his understanding. And Tai Fu was a student of this Dharma Master Joe, a scholar of the fifth century in China. And |
| `whisper-turbo+ctx` | with Nansen, deepening his understanding. And Tai Fu was a student of this dharma master Joe, a scholar of the 5th century in China. And |

**zmm.org** — `31587_s01620` at 4:25 · Vanessa Zuisei Goddard · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, you know, I'm really thinking of taking the train because every time I go into the city my car gets broken into. And she said, oh, don't be ridiculous. Just take the car. It'll be easier. So he did. He took his car. They go to |
| `parakeet-v3` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, Oh, don't be ridiculous. Just take the car, it'll be easier. So he did. He took his car. They go to |
| `parakeet-v3+boost0.3f` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, Oh, don't be ridiculous. Just take the car, it'll be easier. So he did. He took his car. They go to |
| `parakeet-v3+boost0.5` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, Oh, don't be ridiculous. Just take the car, it'll be easier. So he did. He took his car. They go to |
| `parakeet-v3+boost1` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, Oh, don't be ridiculous. Just take the car, it'll be easier. So he did. He took his car. They go to |
| `qwen3-asr-1.7b` | teach. So I think she was here one time, and he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, "You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into." And she said, "Oh, don't be ridiculous. Just take the take the car. It'll be easier." So he did. He took his car to go to |
| `qwen3-asr-1.7b+ctx` | teach. So I think she was here one time, and he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, "You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into." And she said, "Oh, don't be ridiculous. Just take the take the car. It'll be easier." So he did. He took his car to go to |
| `qwen3-asr-1.7b+vad` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, "You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into." And she said, "Oh, don't be ridiculous! Just take the take the car; it'll be easier." So he did. He took his car to go to |
| `qwen3-asr-1.7b+vad+terms` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, "You know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into." And she said, "Oh, don't be ridiculous. Just take the take the car. It'll be easier." So he did. He took his car to go to |
| `whisper-large-v3` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, you know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, oh, don't be ridiculous. Just take the car. It'll be easier. So he did. He took his car. They go to |
| `whisper-large-v3+ctx` | be talking about Blue Cliff Record, Deshan, Shugen, Wuzu, and zmm .mro .org. So he did. He took his car. They go to |
| `whisper-turbo` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, you know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, oh, don't be ridiculous. Just take the car. It'll be easier. So he did. He took his car. They go to |
| `whisper-turbo+ctx` | teach. So I think she was here one time. And he was telling her he was going to a wedding in New York City. I'm not sure where he was, somewhere outside of it. And he said to her, you know, I'm really thinking of taking the train because every time I go into the city, my car gets broken into. And she said, oh, don't be ridiculous. Just take the car. It'll be easier. So he did. He took his car. They go to |

**Eihei Dogen** — `36533_s00180` at 4:44 · John Daido Loori · 2000s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | words completely devoid of any violent or spiteful language and Dogen says as you take the light in affectionate words they will gradually flourish |
| `parakeet-v3` | words, completely devoid of any violent or spiteful language. And Dogan says, as you take delight in affectionate words, they will gradually flourish, |
| `parakeet-v3+boost0.3f` | words, completely devoid of any violent or spiteful language. And Dogan says, as you take delight in affectionate words, they will gradually flourish, |
| `parakeet-v3+boost0.5` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take delight in affectionate words, they will gradually flourish, |
| `parakeet-v3+boost1` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take delight in affectionate words, they will gradually flourish, |
| `qwen3-asr-1.7b` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take the light in affectionate words, they will gradually flourish, |
| `qwen3-asr-1.7b+ctx` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take the light in affectionate words, they will gradually flourish, |
| `qwen3-asr-1.7b+vad` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take delight in affectionate words, they will gradually flourish, |
| `qwen3-asr-1.7b+vad+terms` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take delight in affectionate words, they will gradually flourish, |
| `whisper-large-v3` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take the light in affectionate words, they will gradually flourish. |
| `whisper-large-v3+ctx` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take delight in affectionate words, they will gradually flourish. |
| `whisper-turbo` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take the light in affectionate words, they will gradually flourish, |
| `whisper-turbo+ctx` | words, completely devoid of any violent or spiteful language. And Dogen says, as you take the light in affectionate words, they will gradually flourish, |

**Geoffrey Shugen Arnold** — `32903_s00720` at 3:33 · Vanessa Zuisei Goddard · 2010s · easy audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | least we know, and then we can proceed. At least, as Ryushin Sensei said, we have our position, it's fixed, and we can |
| `parakeet-v3` | least we know. And then we can proceed. At least, as Rishan Sensei said, we have our position, it's fixed, and we can |
| `parakeet-v3+boost0.3f` | least we know. And then we can proceed. At least, as Rishan Sensei said, we're we have our position, it's fixed, and we can |
| `parakeet-v3+boost0.5` | least we know. And then we can proceed. At least, as Rishan Sensei said, we're we have our position, it's fixed, and we can |
| `parakeet-v3+boost1` | least we know. And then we can proceed. At least, as Rishan Sensei said, we have our position, it's fixed, and we can |
| `qwen3-asr-1.7b` | least we know, and then we can proceed. At least, as Rishin Sensei said, we have our position; it's fixed, and we can |
| `qwen3-asr-1.7b+ctx` | least we know, and then we can proceed. At least, as Shugen Sensei said, we have our position; it's fixed, and we can |
| `qwen3-asr-1.7b+vad` | least we know, and then we can proceed. At least, as Rieschenssen said, we have our position; it's fixed, and we can |
| `qwen3-asr-1.7b+vad+terms` | least we know, and then we can proceed. At least, as Rishin Sensei said, we have our position; it's fixed, and we can |
| `whisper-large-v3` | least we know, and then we can proceed. At least, as Rishon Sensei said, we have our position. It's fixed, and we can |
| `whisper-large-v3+ctx` | least we know, and then we can proceed. At least, as Shugen Sensei said, we have our position. It's fixed, and we can |
| `whisper-turbo` | least we know, and then we can proceed. At least, as Rishun Sensei said, we have our position. It's fixed, and we can |
| `whisper-turbo+ctx` | least we know, and then we can proceed. At least, as Rishun Sensei said, we have our position. It's fixed, and we can |

**Zhaozhou Congshen** — `34803_s00570` at 4:09 · Geoffrey Shugen Arnold · 2020s · medium audio

| System | Text |
|---|---|
| `legacy-whisper-cli` | her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could, from one perspective, say, is a great master. He's an |
| `parakeet-v3` | her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master. He's an |
| `parakeet-v3+boost0.3f` | her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, he's an |
| `parakeet-v3+boost0.5` | her power? She's a tea woman offering refreshment to travelers. Zha Zhou, you could from one perspective say, is a great master, he's an |
| `parakeet-v3+boost1` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master, he's an |
| `qwen3-asr-1.7b` | her power? She's a tea woman offering refreshment to travelers. Zhao, you could, from one perspective, say, is a great master. He's an |
| `qwen3-asr-1.7b+ctx` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say, is a great master, is an |
| `qwen3-asr-1.7b+vad` | her power? She's a tea woman offering refreshment to travelers. Jangjo, you could, from one perspective, say is a great master, is an |
| `qwen3-asr-1.7b+vad+terms` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could, from one perspective, say is a great master, is an |
| `whisper-large-v3` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. He's an |
| `whisper-large-v3+ctx` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. He's an |
| `whisper-turbo` | her power? She's a tea woman offering refreshment to travelers. Zhao Zhao, you could from one perspective say, is a great master. He's an |
| `whisper-turbo+ctx` | her power? She's a tea woman offering refreshment to travelers. Zhaozhou, you could from one perspective say, is a great master. He's an |

## Agreement between systems

Word error rate of each row's output measured against each column's output, on speech clips. Systems that agree closely are making the same choices, not necessarily the right ones.

| | `legacy-whisper-cli` | `parakeet-v3` | `parakeet-v3+boost0.3f` | `parakeet-v3+boost0.5` | `parakeet-v3+boost1` | `qwen3-asr-1.7b` | `qwen3-asr-1.7b+ctx` | `qwen3-asr-1.7b+vad` | `qwen3-asr-1.7b+vad+terms` | `whisper-large-v3` | `whisper-large-v3+ctx` | `whisper-turbo` | `whisper-turbo+ctx` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `legacy-whisper-cli` | · | 9% | 9% | 9% | 8% | 9% | 9% | 9% | 11% | 7% | 15% | 7% | 9% |
| `parakeet-v3` | 8% | · | 1% | 1% | 1% | 8% | 8% | 7% | 9% | 7% | 15% | 7% | 8% |
| `parakeet-v3+boost0.3f` | 8% | 1% | · | 1% | 1% | 8% | 8% | 7% | 9% | 7% | 15% | 7% | 8% |
| `parakeet-v3+boost0.5` | 8% | 1% | 1% | · | 1% | 8% | 8% | 7% | 9% | 7% | 15% | 7% | 8% |
| `parakeet-v3+boost1` | 8% | 1% | 1% | 1% | · | 7% | 8% | 7% | 9% | 7% | 15% | 7% | 8% |
| `qwen3-asr-1.7b` | 9% | 8% | 8% | 8% | 8% | · | 3% | 4% | 6% | 7% | 15% | 8% | 9% |
| `qwen3-asr-1.7b+ctx` | 9% | 9% | 9% | 9% | 8% | 3% | · | 5% | 6% | 8% | 16% | 9% | 9% |
| `qwen3-asr-1.7b+vad` | 9% | 7% | 7% | 7% | 7% | 4% | 5% | · | 3% | 7% | 14% | 7% | 8% |
| `qwen3-asr-1.7b+vad+terms` | 11% | 9% | 9% | 9% | 9% | 6% | 6% | 3% | · | 9% | 16% | 9% | 10% |
| `whisper-large-v3` | 8% | 7% | 7% | 7% | 7% | 8% | 8% | 7% | 9% | · | 9% | 2% | 3% |
| `whisper-large-v3+ctx` | 14% | 14% | 14% | 14% | 14% | 14% | 14% | 13% | 14% | 9% | · | 9% | 9% |
| `whisper-turbo` | 7% | 7% | 7% | 7% | 7% | 7% | 8% | 7% | 9% | 2% | 10% | · | 2% |
| `whisper-turbo+ctx` | 8% | 8% | 8% | 8% | 8% | 8% | 9% | 8% | 9% | 3% | 9% | 2% | · |

## Clips with repetition loops

- `legacy-whisper-cli`: `30643_s01710`, `31043_s04042`, `36192_s02610`
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
