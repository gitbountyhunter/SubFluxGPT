"""
Prepare bug bounty data for llama2.c training.
This replaces tinystories.py for cybersecurity domain training.
"""

import argparse
import os
import random
import re
from typing import List
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import numpy as np
from tokenizer import Tokenizer
from data_collector.database_manager import DatabaseManager
import yaml

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

DATA_CACHE_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_CACHE_DIR, "bugbounty_tokens")


def report_text(report: dict) -> str:
    """
    Format a report for training data.
    
    Args:
        report: Report dictionary from database
        
    Returns:
        Formatted text string
    """
    program_name = report.get('program_name', 'Unknown')
    title = report.get('title', '')
    weakness = report.get('weakness', '')
    raw_content = report.get('raw_content', '')
    
    # Format for language model training
    text = (
        f"Program: {program_name}\n"
        f"Report title: {title}\n"
        f"Weakness: {weakness}\n"
        f"Report details: {raw_content}\n"
    ).strip()
    
    return text


def process_reports(reports: List[dict], tokenizer: Tokenizer, split_name: str, vocab_size: int) -> str:
    """
    Process reports into tokenized .bin file.
    
    Args:
        reports: List of report dictionaries
        tokenizer: Tokenizer instance
        split_name: Name of split (train/val)
        vocab_size: Vocabulary size
        
    Returns:
        Path to output .bin file
    """
    tokens = []
    
    for report in reports:
        text = report_text(report)
        if text:
            # BOS at the start of each report
            tokens.extend(tokenizer.encode(text, bos=True, eos=False))
    
    if not tokens:
        raise RuntimeError(f"No tokens produced for {split_name} split.")
    
    # Convert to uint16 array
    token_array = np.asarray(tokens, dtype=np.uint16)
    output_path = os.path.join(OUTPUT_DIR, f"{split_name}.bin")
    token_array.tofile(output_path)
    
    print(
        f"{split_name}: {len(reports)} reports, "
        f"{len(token_array)} tokens -> {output_path}"
    )
    
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vocab_size",
        type=int,
        default=0,
        help="Use 0 for the Llama 2 tokenizer; otherwise use your custom "
             "SentencePiece vocab size, such as 2048.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--train_split",
        type=float,
        default=0.9,
        help="Fraction of data to use for training (rest for validation)"
    )
    args = parser.parse_args()

    # Initialize database
    db_url = config['database']['url']
    db_manager = DatabaseManager(db_url)
    
    # Get all reports from database
    print("Loading reports from database...")
    reports = db_manager.get_reports_for_training()
    
    if len(reports) < 2:
        raise RuntimeError(
            f"Only found {len(reports)} reports in database. "
            "Run data collection first."
        )
    
    print(f"Loaded {len(reports)} reports from database")
    
    # Shuffle reports
    random.Random(args.seed).shuffle(reports)
    
    # Split into train/val
    split_index = max(1, int(len(reports) * args.train_split))
    split_index = min(split_index, len(reports) - 1)
    splits = {
        "train": reports[:split_index],
        "val": reports[split_index:],
    }
    
    # Initialize tokenizer
    if args.vocab_size == 0:
        tokenizer_model = None
    else:
        tokenizer_model = os.path.join(
            DATA_CACHE_DIR, f"tok{args.vocab_size}.model"
        )
        if not os.path.exists(tokenizer_model):
            raise FileNotFoundError(
                f"Custom tokenizer not found: {tokenizer_model}"
            )
    
    tokenizer = Tokenizer(tokenizer_model)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Process each split
    for split_name, split_reports in splits.items():
        process_reports(split_reports, tokenizer, split_name, args.vocab_size)
    
    print("Done. These files are ready for the dataset loader.")


if __name__ == "__main__":
    main()
