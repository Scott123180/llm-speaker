import os
import requests
from transformers import AutoTokenizer

# --- Settings ---
MODEL_NAME = "llama3.1"  # Your Ollama model name
TOKENIZER_MODEL = "meta-llama/Llama-2-7b-hf"  # Tokenizer close to your model
MAX_TOKENS = 2000
FOLDER_PATH = "./transcripts"
OUTPUT_SUFFIX = ".cleaned.txt"
HEADERS = {"Content-Type": "application/json"}

# --- Load Tokenizer ---
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)

# --- Ollama prompt instruction ---
SYSTEM_PROMPT = (
    "You are a careful transcription editor. This is a transcript of a talk given by a Zen teacher. "
    "Your task is to preserve the original meaning while fixing grammar and transcription mistakes. "
    "Do not rewrite for engagement or clarity. Remove repeated thank-you sections or long name blocks at the end. "
    "If Zen terms like 'zazen', 'kensho', 'mu', or 'dokusan' appear to be mistranscribed, correct them."
)

def query_ollama(chunk_text):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chunk_text}
        ]
    }
    response = requests.post("http://localhost:11434/api/chat", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["message"]["content"]

def chunk_text_by_tokens(text, max_tokens=MAX_TOKENS):
    tokens = tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        token_chunk = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(token_chunk)
        chunks.append(chunk_text)

    return chunks

def process_file(filepath):
    print(f"🔍 Processing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        original_text = f.read()

    chunks = chunk_text_by_tokens(original_text)
    cleaned_chunks = []

    for idx, chunk in enumerate(chunks):
        print(f"  → Cleaning chunk {idx+1}/{len(chunks)}...")
        cleaned = query_ollama(chunk)
        cleaned_chunks.append(cleaned)

    output_path = filepath.replace(".txt", OUTPUT_SUFFIX)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(cleaned_chunks))

    print(f"✅ Saved cleaned file to {output_path}")

def main():
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".txt") and not filename.endswith(OUTPUT_SUFFIX):
            process_file(os.path.join(FOLDER_PATH, filename))

if __name__ == "__main__":
    main()
