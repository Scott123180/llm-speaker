# How to run

1. Download ollama
`curl -fsSL https://ollama.com/install.sh | sh`

2. Choose a model

Basic, but runs on cpu:
`ollama run mistral`

Trying to run on GPU:
https://ollama.com/library/llama3.1

`ollama run llama3.1:8b-instruct-q5_K_M`


## Prompt
``` txt
Instruction Please clean up the following transcript of a talk given by a Zen teacher. Correct grammatical errors and fix any obvious transcription mistakes.

Do not rewrite or rephrase for engagement or style—keep the original tone and structure as intact as possible.

If there are repeated "thank you" sections or long blocks of names at the end, feel free to remove them.

This is a Zen Buddhist talk, so if any Zen-specific terms (e.g., zazen, dokusan, mu, kensho, bodhisattva) appear to be incorrectly transcribed, please correct them based on context.

[Insert transcript here]

```
