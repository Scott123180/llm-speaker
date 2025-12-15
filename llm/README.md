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
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ./24798.txt)" \
  | ollama run llama70-cleanup > 24798_cleaned.txt
```

# Install small model
cd temp

`ollama pull llama3:8b`

`ollama create llama8-cleanup -f Modelfile-llama8-cleanup`

``` bash
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ../transcripts/24526_short.txt)" \
  | ollama run llama8-cleanup
```

# 8B q5
`ollama pull llama3:8b-instruct-q5_K_M`


`ollama create llama8-Q5-instruct -f Modelfile-llama8-Q5-instruct-cleanup`


``` bash
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ../transcripts/24526_short.txt)" \
  | ollama run llama8-Q5-instruct
```

# 3.1 fp16
`ollama pull llama3.1:8b-instruct-fp16`

`ollama create llama8-31-fp16 -f Modelfile-llama8-31-instruct-fp16`

``` bash
printf "Clean this transcript according to your rules. Do NOT summarize.\n\n%s" \
  "$(cat ../transcripts/24526_short.txt)" \
  | ollama run llama8-31-fp16
```
