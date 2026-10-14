# prepare_hackerone.py
# Run from the SubFluxGPT project root.
#
# Install the dataset package first:
#   python -m pip install datasets
#
# Then run:
#   python training_pipeline/prepare_hackerone.py
#
# For llama2.c with a custom tokenizer:
#   python training_pipeline/prepare_hackerone.py --vocab_size 2048
#
# For nanoGPT/GPT-2 (uses GPT-2 tokenizer):
#   python training_pipeline/prepare_hackerone.py --tokenizer=gpt2

import argparse
import os
import random
import re

import numpy as np
from datasets import load_dataset

DATASET_ID = "Hacker0x01/hackerone_disclosed_reports"
OUTPUT_DIR_LLAMA2C = "data/hackerone_tokens"
OUTPUT_DIR_GPT2 = "data/hackerone_gpt2_tokens"

# Adjust this list after inspecting the reports that match.
RELEVANT = re.compile(
    r"\b(subdomain|sub-domain|dns|dangling|cname|takeover|"
    r"zone transfer|subdomain takeover)\b",
    re.IGNORECASE,
)


def text_value(value):
    """Convert common dataset field values to readable text."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(text_value(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_value(v) for v in value)
    return str(value)


def get_field(row, name):
    return text_value(row.get(name, "")).strip()


def report_text(row):
    title = get_field(row, "title")
    body = get_field(row, "vulnerability_information")
    weakness = get_field(row, "weakness")

    # Include just the report content needed for language-model training.
    return (
        f"Report title: {title}\n"
        f"Weakness: {weakness}\n"
        f"Report details: {body}\n"
    ).strip()


def prepare_llama2c(reports, vocab_size=0, seed=42, train_split=0.9):
    """Prepare data for llama2.c using SentencePiece tokenizer."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        from tokenizer import Tokenizer
    except ImportError:
        # Try llama2.c directory
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'llama2.c'))
            from tokenizer import Tokenizer
        except ImportError:
            print("Error: llama2.c tokenizer not found. Make sure llama2.c is in the project.")
            return None
    
    # Initialize tokenizer
    if vocab_size == 0:
        tokenizer_model = None
    else:
        tokenizer_model = os.path.join("data", f"tok{vocab_size}.model")
        if not os.path.exists(tokenizer_model):
            raise FileNotFoundError(
                f"Custom tokenizer not found: {tokenizer_model}"
            )
    
    tokenizer = Tokenizer(tokenizer_model)
    os.makedirs(OUTPUT_DIR_LLAMA2C, exist_ok=True)
    
    # Split at the report level so one report cannot leak into both splits.
    random.Random(seed).shuffle(reports)
    split_index = max(1, min(int(len(reports) * train_split), len(reports) - 1))
    splits = {
        "train": reports[:split_index],
        "val": reports[split_index:],
    }
    
    for split_name, split_reports in splits.items():
        tokens = []
        for text in split_reports:
            # Match tinystories.py: BOS at the start of each report.
            tokens.extend(tokenizer.encode(text, bos=True, eos=False))
        
        if not tokens:
            raise RuntimeError(f"No tokens produced for {split_name} split.")
        
        # llama2.c's pasted loader reads uint16 token IDs.
        token_array = np.asarray(tokens, dtype=np.uint16)
        output_path = os.path.join(OUTPUT_DIR_LLAMA2C, f"{split_name}.bin")
        token_array.tofile(output_path)
        
        print(
            f"llama2.c {split_name}: {len(split_reports)} reports, "
            f"{len(token_array)} tokens -> {output_path}"
        )
    
    return OUTPUT_DIR_LLAMA2C


def prepare_gpt2(reports, seed=42, train_split=0.9):
    """Prepare data for nanoGPT/GPT-2 using tiktoken."""
    try:
        import tiktoken
    except ImportError:
        print("Error: tiktoken not found. Install with: pip install tiktoken")
        return None
    
    # GPT-2 tokenizer, matching nanoGPT's pretrained GPT-2 checkpoints.
    enc = tiktoken.get_encoding("gpt2")
    eot = enc.eot_token
    
    os.makedirs(OUTPUT_DIR_GPT2, exist_ok=True)
    
    # Split at the report level
    random.Random(seed).shuffle(reports)
    split_index = max(1, min(int(len(reports) * train_split), len(reports) - 1))
    splits = {
        "train": reports[:split_index],
        "val": reports[split_index:],
    }
    
    for name, docs in splits.items():
        token_ids = []
        for doc in docs:
            token_ids.extend(enc.encode_ordinary(doc))
            token_ids.append(eot)
        
        tokens = np.asarray(token_ids, dtype=np.uint16)
        path = os.path.join(OUTPUT_DIR_GPT2, f"{name}.bin")
        tokens.tofile(path)
        print(f"GPT-2 {name}: {len(docs)} reports, {len(tokens)} tokens -> {path}")
    
    return OUTPUT_DIR_GPT2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tokenizer",
        type=str,
        default="llama2c",
        choices=["llama2c", "gpt2", "both"],
        help="Which tokenizer to use (llama2c, gpt2, or both)"
    )
    parser.add_argument(
        "--vocab_size",
        type=int,
        default=0,
        help="Use 0 for the Llama 2 tokenizer; otherwise use your custom "
             "SentencePiece vocab size, such as 2048. Only for llama2c."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--train_split",
        type=float,
        default=0.9,
        help="Fraction of data to use for training (rest for validation)"
    )
    args = parser.parse_args()

    print(f"Loading {DATASET_ID}...")
    dataset = load_dataset(DATASET_ID, split="train")

    reports = []
    for row in dataset:
        text = report_text(row)
        if text and RELEVANT.search(text):
            reports.append(text)

    if len(reports) < 2:
        raise RuntimeError(
            f"Only found {len(reports)} matching reports. "
            "Check the dataset fields or broaden the keyword filter."
        )

    print(f"Found {len(reports)} relevant reports (subdomain/DNS/takeover)")

    if args.tokenizer in ["llama2c", "both"]:
        print("\nPreparing data for llama2.c...")
        prepare_llama2c(reports, args.vocab_size, args.seed, args.train_split)
    
    if args.tokenizer in ["gpt2", "both"]:
        print("\nPreparing data for GPT-2/nanoGPT...")
        prepare_gpt2(reports, args.seed, args.train_split)
    
    print("\nDone. These files are ready for the dataset loader.")
    print("\nFor llama2.c training:")
    print("  - Update PretokDataset to load from data/hackerone_tokens")
    print("\nFor nanoGPT/GPT-2 training:")
    print("  - Set dataset = 'hackerone' in config")
    print("  - Create data/hackerone/prepare.py (or use data/hackerone_gpt2_tokens)")


if __name__ == "__main__":
    main()
