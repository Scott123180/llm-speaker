This is a simple script to transform a csv into a json that can be read by my dharma library project.

| Stage                   | Meaning                                       |
| ----------------------- | --------------------------------------------- |
| `audio_original`        | Source audio, untouched                       |
| `transcript_raw`        | Direct ASR output (verbatim, noisy)           |
| `transcript_structured` | Text segmented into paragraphs / blocks       |
| `transcript_cleaned`    | Errors corrected, wording fixed               |
| `transcript_curated`    | Domain-aware refinement (names, dharma terms) |
| `transcript_published`  | Final, user-facing canonical text             |
