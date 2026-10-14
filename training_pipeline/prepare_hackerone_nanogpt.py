# data/hackerone/prepare.py
# For nanoGPT training on HackerOne reports
# Run from the SubFluxGPT project root:
#   python training_pipeline/prepare_hackerone_nanogpt.py

import os
import random
import re

import numpy as np
import tiktoken
from datasets import load_dataset

OUT_DIR = "data/hackerone"
KEYWORDS = re.compile(
    r"\b(subdomain|sub-domain|dns|dangling|cname|takeover|zone transfer)\b",
    re.IGNORECASE,
)


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(as_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(as_text(v) for v in value)
    return str(value)


def main():
    ds = load_dataset(
        "Hacker0x01/hackerone_disclosed_reports",
        split="train",
    )

    reports = []
    for row in ds:
        title = as_text(row.get("title")).strip()
        weakness = as_text(row.get("weakness")).strip()
        details = as_text(row.get("vulnerability_information")).strip()

        text = (
            f"Report title: {title}\n"
            f"Weakness: {weakness}\n"
            f"Report details: {details}\n"
        )
        if details and KEYWORDS.search(text):
            reports.append(text)

    if len(reports) < 2:
        raise RuntimeError(
            f"Only found {len(reports)} matching reports; "
            "check the dataset fields or broaden the keyword filter."
        )

    random.Random(42).shuffle(reports)
    split_at = max(1, min(int(len(reports) * 0.9), len(reports) - 1))
    splits = {
        "train": reports[:split_at],
        "val": reports[split_at:],
    }

    # GPT-2 tokenizer, matching nanoGPT's pretrained GPT-2 checkpoints.
    enc = tiktoken.get_encoding("gpt2")
    eot = enc.eot_token

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, docs in splits.items():
        token_ids = []
        for doc in docs:
            token_ids.extend(enc.encode_ordinary(doc))
            token_ids.append(eot)

        tokens = np.asarray(token_ids, dtype=np.uint16)
        path = os.path.join(OUT_DIR, f"{name}.bin")
        tokens.tofile(path)
        print(f"{name}: {len(docs)} reports, {len(tokens)} tokens -> {path}")

if __name__ == "__main__":
    main()
