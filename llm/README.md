# How to run

1. Download ollama
`curl -fsSL https://ollama.com/install.sh | sh`

2. Choose a model

Basic, but runs on cpu:
`ollama run mistral`

Trying to run on GPU:
https://ollama.com/library/llama3.1

# Install model
cd temp

`ollama create llama70-cleanup -f Modelfile-llama70-cleanup`

``` bash
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ../transcripts/24526.txt)" \
  | ollama run llama70-cleanup
```



