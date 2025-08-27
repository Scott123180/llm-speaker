import os
import json
import requests
import re

# -------- Settings --------
MODEL_NAME = "llama3.1:8b-instruct-q5_K_M"
#MODEL_NAME = "mistral:7b-instruct-q4_K_M"
FOLDER_PATH = "./transcripts"
OUTPUT_SUFFIX = ".cleaned.txt"
HEADERS = {"Content-Type": "application/json"}

# chunking / sampling
CHARS_PER_TOKEN = 4.0          # heuristic for LLaMA-like models
TEMPERATURE = 0
TOP_P = 1.0
EVALUATION_WINDOW_CHARACTERS = 1200
CONTEXT_WINDOW_TOKENS = 1000

def query_first_paragraph(chunk_text: str) -> str:
    """
    Ask the model to return the FIRST paragraph as an exact substring of chunk_text.
    Returns '' if it can't decide.
    """
    system_prompt = (
        "You are a strict tool. Output ONLY VALID JSON.\n"
        "Task: Split the user text (delimited by <text>...</text>) into logical paragraphs.\n"
        "Rules:\n"
        "- Paragraphs should end at natural boundaries (usually after '.', '!' or '?').\n"
        "- Output exactly the FIRST paragraph only, as it appears verbatim from the input.\n"
        "- Format: {\"paragraph\": \"<p>substring</p><p>substring</p>\"}\n"
        "- The substring MUST be copied byte-for-byte from the input. Do not rewrite or alter words.\n"
        "- If no sentence-ending punctuation exists, cut a reasonable early segment (~800–1200 characters).\n"
        "- If the text is too short to form a paragraph, return {\"paragraph\": \"\"}."
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"<text>\n{chunk_text}\n</text>"},
        ],
        "stream": False,
        "keep_alive": "30m",
        "format": "json",
        "options": {"temperature": TEMPERATURE, "top_p": TOP_P, "num_ctx": CONTEXT_WINDOW_TOKENS}
    }
    r = requests.post("http://localhost:11434/api/chat", headers=HEADERS, json=payload)
    r.raise_for_status()
    print(r.json())
    content = r.json()["message"]["content"]
    data = json.loads(content)  # JSON mode -> parse string into dict
    para = data.get("paragraph", "")
    return para if isinstance(para, str) else ""

# -------- Utilities --------
def approx_token_count(text: str, chars_per_token: float = CHARS_PER_TOKEN) -> int:
    return int(len(text) / chars_per_token)

# -------- Process flow (plugged in) --------
def process_file(filepath):
    print(f"🔍 Processing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        original_text = flatten_text(f.read())

    print(f"Approximate tokens: {approx_token_count(original_text)} "
          f"(chars={len(original_text)})")
    

    working_text = original_text 
    loops = 0 # safety measure

    while(len(working_text) > 0 and loops < 200):
        substring = working_text[0:EVALUATION_WINDOW_CHARACTERS]
        print(f'Substring: {substring}')
        llm_paragraph = query_first_paragraph(substring)


        cleaned = clean_paragraph(llm_paragraph)
        working_text = working_text[len(cleaned):]

        print(f'CLEANED: {cleaned}')
        print("===========================")

        loops += 1

    # # 3) Save
    # output_path = filepath.replace(".txt", OUTPUT_SUFFIX)
    # with open(output_path, "w", encoding="utf-8") as f:
    #     f.write(paragraphized)

    # print(f"✅ Saved cleaned file to {output_path}")

def clean_paragraph(para: str) -> str:
    """
    Clean up model output:
    - Remove <p>...</p> wrappers
    - Strip surrounding whitespace
    - Remove escape backslashes (e.g. don\'t -> don't)
    """
    # remove <p> and </p>
    para = re.sub(r'^<p>|</p>$', '', para.strip())
    # unescape common backslash escapes
    para = para.replace("\\'", "'").replace('\\"', '"').replace("\\n", " ")
    # collapse multiple spaces
    # para = re.sub(r"\s+", " ", para)
    return para.strip()

def flatten_text(text: str) -> str:
    """
    Flatten text into a single line:
    - Replace all newlines with spaces
    - Collapse multiple spaces into one
    - Strip leading/trailing whitespace
    """
    # Replace line breaks and tabs with spaces
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    # Collapse multiple spaces
    # text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".txt") and not filename.endswith(OUTPUT_SUFFIX):
            process_file(os.path.join(FOLDER_PATH, filename))

if __name__ == "__main__":
    main()
