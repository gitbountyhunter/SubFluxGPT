# HackerOne Dataset Integration Guide

This guide explains how to use the HackerOne disclosed reports dataset (`Hacker0x01/hackerone_disclosed_reports`) for training your models in SubFluxGPT.

## Overview

The HackerOne dataset contains real bug bounty reports, including subdomain takeover, DNS misconfigurations, and other vulnerabilities. The data preparation scripts filter for reports relevant to subdomain/DNS/takeover topics.

## Quick Start

### Option 1: Direct HuggingFace (Recommended for Quick Testing)

This bypasses the database and downloads directly from HuggingFace:

```bash
# For llama2.c training
python training_pipeline/prepare_hackerone.py --tokenizer=llama2c

# For GPT-2/nanoGPT training
python training_pipeline/prepare_hackerone.py --tokenizer=gpt2

# For both
python training_pipeline/prepare_hackerone.py --tokenizer=both
```

### Option 2: Database (For Continuous Collection)

This uses the SubFluxGPT database after running data collection:

```bash
# Run data collection first
python -m data_collector.main

# Then prepare from database
python training_pipeline/prepare_bugbounty.py --vocab_size 4096
```

## Files Created

### For llama2.c (SentencePiece tokenizer)
- `data/hackerone_tokens/train.bin` - Training data
- `data/hackerone_tokens/val.bin` - Validation data

### For GPT-2/nanoGPT (tiktoken)
- `data/hackerone_gpt2_tokens/train.bin` - Training data
- `data/hackerone_gpt2_tokens/val.bin` - Validation data
- `data/hackerone/train.bin` - For nanoGPT (alternative location)
- `data/hackerone/val.bin` - For nanoGPT (alternative location)

## Training with HackerOne Data

### llama2.c Training

Update your training script to use the HackerOne data:

```python
# In your training loop
from training_pipeline.bugbounty import PretokDataset, Task

dataset = PretokDataset(
    split="train",
    max_seq_len=256,
    vocab_size=4096,
    vocab_source="custom",
    data_source="hackerone"  # Use "hackerone" for HuggingFace data
)
```

Or use the CLI test:
```bash
python training_pipeline/bugbounty.py --data_source=hackerone --vocab_size=4096
```

### nanoGPT/GPT-2 Training

1. Prepare the data:
```bash
python training_pipeline/prepare_hackerone_nanogpt.py
```

2. Create a config file or use the provided one:
```bash
python train.py config/finetune_hackerone.py
```

The config `config/finetune_hackerone.py` is already set up for:
- Dataset: `hackerone`
- Init from: `gpt2` (pretrained GPT-2)
- Learning rate: `1e-5` (fine-tuning rate)
- Max iters: `500`
- Block size: `1024`

### GPT-2 (HuggingFace Transformers) Training

The GPT-2 trainer in SubFluxGPT already supports this:

```bash
python training_pipeline/train_gpt2.py --model_size 124M --output_dir ./models/gpt2
```

Or via the scheduler:
```bash
python training_pipeline/scheduler.py
```

## Keyword Filter

The scripts filter reports using these keywords:
- subdomain
- sub-domain
- dns
- dangling
- cname
- takeover
- zone transfer
- subdomain takeover

You can modify the `RELEVANT` regex in the preparation scripts to add/remove keywords.

## Report Format

Each report is formatted as:
```
Report title: [title]
Weakness: [weakness category]
Report details: [vulnerability information]
```

This format teaches the model the structure of bug bounty reports.

## Important Notes

### Dataset Terms
The HackerOne dataset is available under HackerOne's Terms of Service. Review these terms before:
- Training on the data
- Distributing a model trained on it
- Using outputs commercially

### Filter Quality
The keyword filter is a **first pass only**. It may:
- Miss relevant reports
- Include irrelevant reports

**Always inspect the exported set** before training to ensure quality.

### Data Splitting
The scripts split by **report**, not by random token chunks. This prevents the same report from appearing in both train and validation sets.

### Custom Tokenizer
For llama2.c with a custom tokenizer:
```bash
# First train a custom tokenizer (if needed)
python llama2.c/tinystories.py train_vocab --vocab_size=4096

# Then prepare HackerOne data with that tokenizer
python training_pipeline/prepare_hackerone.py --tokenizer=llama2c --vocab_size=4096
```

## Comparison: Database vs HuggingFace

| Feature | Database | HuggingFace Direct |
|---------|----------|---------------------|
| Setup | Requires running collector | Direct download |
| Data Freshness | Always up-to-date | Fixed snapshot |
| Custom Reports | Can add your own | Only disclosed reports |
| Continuity | Part of continuous pipeline | One-time preparation |
| Flexibility | Filter by platform/program | Fixed dataset |

## Integration with Continuous Training

The training scheduler `training_pipeline/scheduler.py` can use either source:

1. **HuggingFace mode**: Prepare once, train on fixed dataset
2. **Database mode**: Continuous collection → continuous training

To switch modes, update the scheduler to call the appropriate prepare script.

## Troubleshooting

### "No tokens produced"
- The keyword filter may be too strict
- Check if reports were downloaded
- Try broadening the keyword regex

### "Tokenizer not found"
- For llama2c: Ensure the tokenizer model exists at `data/tok{vocab_size}.model`
- For GPT-2: Ensure tiktoken is installed (`pip install tiktoken`)

### "Dataset too small"
- Need at least 2 reports for train/val split
- May need to broaden the keyword filter
- Check the HuggingFace dataset is accessible

## Next Steps

1. **Inspect exported reports**: Check a few `.txt` files to ensure quality
2. **Tune keyword filter**: Add/remove keywords based on your needs
3. **Experiment with splits**: Try different train/val ratios
4. **Add more platforms**: Integrate Bugcrowd/YesWeHack reports similarly
5. **Create evaluation set**: Hold out some reports for final testing

## References

- HackerOne Dataset: https://huggingface.co/datasets/Hacker0x01/hackerone_disclosed_reports
- llama2.c: https://github.com/karpathy/llama2.c
- nanoGPT: https://github.com/karpathy/nanoGPT
- Duck.ai conversation: Provided guidance on using this dataset
