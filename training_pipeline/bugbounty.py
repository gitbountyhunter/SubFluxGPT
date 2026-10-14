"""
Bug bounty dataset loader for llama2.c training.
Modified from tinystories.py to load cybersecurity data.
Supports both database reports and HuggingFace HackerOne dataset.
"""

import argparse
import glob
import os
import random
from typing import List
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import numpy as np
import torch
import torch.distributed as dist
from tqdm import tqdm

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tokenizer import Tokenizer
except ImportError:
    # Tokenizer might be in llama2.c directory
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'llama2.c'))
        from tokenizer import Tokenizer
    except ImportError:
        Tokenizer = None

DATA_CACHE_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_CACHE_DIR, "bugbounty_tokens")
# Alternative output for direct HuggingFace HackerOne data
HACKERONE_DIR = os.path.join(DATA_CACHE_DIR, "hackerone_tokens")


class PretokDataset(torch.utils.data.IterableDataset):
    """Loads pre-tokenized bug bounty reports from disk and yields them as PyTorch tensors."""

    def __init__(self, split, max_seq_len, vocab_size, vocab_source, data_source="database"):
        super().__init__()
        self.split = split
        self.max_seq_len = max_seq_len
        self.vocab_size = vocab_size
        self.vocab_source = vocab_source
        self.data_source = data_source  # "database" or "hackerone"

        # Validate Tokenizer is available if needed
        if vocab_source == "custom" and Tokenizer is None:
            raise ImportError(
                "Tokenizer module not found. Please ensure llama2.c is properly installed "
                "or use vocab_source='llama2' for the default tokenizer."
            )

    def __iter__(self):
        # Get worker info within a DataLoader
        worker_info = torch.utils.data.get_worker_info()
        worker_id = worker_info.id if worker_info else 0
        # Get DDP rank info
        rank = dist.get_rank() if dist.is_initialized() else 0
        # Combine the worker_id and worker_rank to create a unique seed for rng
        seed = 42 + worker_id + 1337 * rank
        rng = random.Random(seed)
        print(f"Created a PretokDataset with rng seed {seed}, data_source={self.data_source}")
        
        # Load the bug bounty tokenized files
        if self.data_source == "hackerone":
            bin_file = os.path.join(HACKERONE_DIR, f"{self.split}.bin")
        else:
            bin_file = os.path.join(OUTPUT_DIR, f"{self.split}.bin")
        
        if not os.path.exists(bin_file):
            raise FileNotFoundError(
                f"Tokenized file not found: {bin_file}. "
                f"Run prepare_bugbounty.py (for database) or prepare_hackerone.py (for HuggingFace) first."
            )
        
        # Open the dataset for reading but keep it on disk with memmap
        m = np.memmap(bin_file, dtype=np.uint16, mode="r")
        num_batches = len(m) // self.max_seq_len
        num_batches -= 1  # drop the last partial batch
        assert num_batches > 0, "The dataset is way too small? investigate."
        
        ixs = list(range(num_batches))
        rng.shuffle(ixs)
        
        for ix in ixs:
            start = ix * self.max_seq_len
            end = start + self.max_seq_len + 1
            # Calling .astype will copy the data into a new numpy array, now in RAM
            chunk = torch.from_numpy((m[start:end]).astype(np.int64))
            x = chunk[:-1]
            y = chunk[1:]
            yield x, y


def get_tokenizer_model_path(vocab_size):
    """
    Returns path to the sentencepiece tokenizer model for a given vocab size
    vocab_size = 0 designates the default Llama 2 tokenizer, in that case
    None is returned.
    """
    if vocab_size == 0:
        return None
    else:
        return os.path.join(DATA_CACHE_DIR, f"tok{vocab_size}.model")


class Task:
    """Task class for data loading."""

    @staticmethod
    def iter_batches(batch_size, device, num_workers=0, **dataset_kwargs):
        ds = PretokDataset(**dataset_kwargs)
        dl = torch.utils.data.DataLoader(
            ds, batch_size=batch_size, pin_memory=True, num_workers=num_workers
        )
        for x, y in dl:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            yield x, y


if __name__ == "__main__":
    """
    CLI for testing the dataset loader.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab_size", type=int, default=0)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--max_seq_len", type=int, default=256)
    parser.add_argument("--data_source", type=str, default="database", choices=["database", "hackerone"])
    args = parser.parse_args()

    # Test loading a batch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    iter_batches = partial(
        Task.iter_batches,
        batch_size=args.batch_size,
        max_seq_len=args.max_seq_len,
        vocab_size=args.vocab_size,
        vocab_source="custom" if args.vocab_size > 0 else "llama2",
        data_source=args.data_source,
        device=device,
        num_workers=0,
    )

    # Load a batch from train split
    train_iter = iter_batches(split="train")
    x, y = next(train_iter)
    
    print(f"Loaded batch from train split (data_source={args.data_source}):")
    print(f"  Shape: {x.shape}")
    print(f"  Device: {x.device}")
    print(f"  Sample tokens: {x[0][:10].tolist()}")
