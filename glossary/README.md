# Glossary

`glossary.csv` lists the names and terms used in ZMM dharma talks. It feeds
ASR context (Whisper prompts, NeMo phrase boosting) and, later, glossary-constrained
correction. Spelling style: plain romanization, no macrons (Dogen, koan, Shobogenzo).

| Column | Meaning |
|---|---|
| `term` | Canonical spelling. Always detected in transcripts, even if it is an English word. |
| `category` | `lineage-*`, `ancestor-*`, `teacher-zmm`, `teacher-modern`, `teacher-guest`, `sangha-zmm`, `figure`, `text`, `liturgy`, `practice`, `title`, `doctrine`, `place` |
| `lang` | `ja` `zh` `sa` `pi` `bo` `ko` `en` … |
| `same_as` | Other **correct** spoken forms, `;`-separated (Joshu;Zhaozhou;Chao-chou). Never "corrected" into each other. Plain-English aliases ("Washing", "Being Time") only match in metadata, not in transcripts. |
| `misheard` | Whisper errors seen in the archive, `;`-separated. Use `wrong>right` to pin the target spelling (`Matsu>Mazu`); otherwise the closest `same_as` form is chosen. |
| `notes` | Free text. Flag ambiguities here (e.g. "Shishin" = sesshin or Gerry Shishin Wick). |

Rules of thumb:
- A word that is a real name or term elsewhere in the file must not appear in another row's `misheard` (e.g. Sankai, Koen, hosan).
- The ZMM lineage switched from Japanese readings to Sanskrit/Chinese pronunciations in April 2023, so keep both forms.

## Per-talk context

`transcriber/build_context.py` combines this glossary with talk metadata and each talk's
existing Whisper transcript (where misheard forms reveal which terms were spoken) to write
`transcriber/context/{id}.json`: a short `prompt` for Whisper and a ranked `terms` list.

```bash
python3 transcriber/build_context.py \
  --metadata ~/Downloads/metadata_export__20261109-20_16.csv \
  --transcripts ~/Documents/talks/all            # ~45 s for the whole archive
```
