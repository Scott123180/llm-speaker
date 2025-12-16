# How to run

1. Download ollama
`curl -fsSL https://ollama.com/install.sh | sh`

2. Choose a model

Basic, but runs on cpu:
`ollama run mistral`

Trying to run on GPU:
https://ollama.com/library/llama3.1

# Install big model

Saw this was using around 42GB of memory.

`cd temp`

`ollama pull llama3.1:70b`

`ollama create llama70-cleanup -f Modelfile-llama70-cleanup`

``` bash
  cat ./30594.txt | ollama run llama70-cleanup > 30594_cleaned_and_corrected.txt
```

This is the older one that might not be good since we're adding extra instructions on it.
``` bash
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ./30594.txt)" \
  | ollama run llama70-cleanup > 30594_cleaned_cor.txt
```