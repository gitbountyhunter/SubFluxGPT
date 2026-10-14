# llm.c Integration for SubFluxGPT

## Overview

llm.c is Andrej Karpathy's pure C/CUDA implementation of GPT-2/GPT-3 training. It provides a minimal, high-performance alternative to PyTorch-based training, making it ~7% faster than PyTorch Nightly. This integration adds llm.c as a fourth training backend alongside llama2.c, nanoGPT, and GPT-2 (HuggingFace).

## Why llm.c?

### Advantages
- **Performance**: ~7% faster than PyTorch Nightly
- **Minimal Dependencies**: No need for 245MB of PyTorch or 107MB of cPython
- **Educational Value**: Clean, readable C code for understanding LLM internals
- **CUDA Support**: Native CUDA implementation with cuBLAS, cuDNN, and Flash Attention
- **Multi-GPU**: Built-in support for multi-GPU and multi-node training via NCCL
- **Reproducibility**: Matches PyTorch reference implementation exactly

### Use Cases
- Production training where performance is critical
- Educational purposes to understand LLM architecture
- Multi-GPU training on large clusters
- Resource-constrained environments (smaller dependency footprint)

## Architecture

### Components Added

1. **`training_pipeline/prepare_llmc.py`**
   - Converts bug bounty reports from database to llm.c .bin format
   - Uses GPT-2 tokenizer (tiktoken) for tokenization
   - Creates train/val splits with proper header format

2. **`training_pipeline/train_llmc.py`**
   - Manages llm.c compilation and training
   - Supports both CPU and GPU (CUDA) training
   - Handles multiple model sizes (124M, 350M, 774M, 1558M)
   - Integrates with the training scheduler

3. **`training_pipeline/evaluator.py`**
   - Tracks model performance over time
   - Compares models across different backends
   - Generates evaluation reports
   - Determines when retraining is needed

4. **`inference/llmc_inference.py`**
   - Python wrapper for llm.c inference (placeholder for future implementation)
   - Note: llm.c is primarily a training library; inference requires separate implementation

5. **`training_pipeline/scheduler.py`** (Modified)
   - Added llm.c training to the continuous training loop
   - Integrated model evaluation after training
   - Generates comparison reports across all models

## Setup

### Prerequisites

1. **Extract llm.c**
   ```bash
   # The llm.c code should be extracted to:
   llm.c/llm.c-master/
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies (already in requirements.txt)
   pip install tiktoken numpy

   # For GPU training (CUDA)
   # - CUDA Toolkit 12.x
   # - cuBLAS (usually included with CUDA)
   # - cuDNN (optional, for Flash Attention)
   # - NCCL (for multi-GPU training)
   ```

3. **Verify Installation**
   ```bash
   cd llm.c/llm.c-master
   make  # This will compile the CPU version
   # or
   make train_gpt2cu  # This will compile the CUDA version (if nvcc is available)
   ```

## Usage

### Data Preparation

Convert bug bounty reports to llm.c format:

```bash
python training_pipeline/prepare_llmc.py --config config.yaml --limit 10000 --val_split 0.1
```

This creates:
- `data/llmc/bugbounty_train.bin` - Training data
- `data/llmc/bugbounty_val.bin` - Validation data

### Manual Training

Train a specific model size:

```bash
# Compile and train 124M model with GPU
python training_pipeline/train_llmc.py --model_size 124M --use_gpu

# Compile only (no training)
python training_pipeline/train_llmc.py --compile_only --use_gpu
```

### Automatic Training

The training scheduler automatically trains llm.c models when enough new reports are collected:

```bash
python training_pipeline/scheduler.py
```

This will:
1. Check if 1000+ new reports have been collected
2. Prepare data for all training backends (llama2.c, nanoGPT, GPT-2, llm.c)
3. Train all configured model sizes
4. Evaluate all models
5. Generate comparison reports

### Model Evaluation

Evaluate a specific model:

```bash
python training_pipeline/evaluator.py --model llmc_124M --type llmc
```

Compare multiple models:

```bash
python training_pipeline/evaluator.py --compare llama2c_42M gpt2_355M llmc_350M
```

Generate evaluation report:

```bash
python training_pipeline/evaluator.py --report
```

## Configuration

Add to `config.yaml`:

```yaml
training:
  # llm.c specific (Karpathy's C/CUDA implementation)
  llmc:
    use_gpu: true
    precision: BF16  # BF16, FP16, or FP32
    use_cudnn: false  # Enable cuDNN for flash attention (requires cuDNN installation)
    eval_interval: 250
    sample_interval: 250
    num_gpus: 1
    learning_rate: 3e-4
    batch_size: 64
    max_steps: 5000
    model_sizes:
      - 124M
      - 350M
      - 774M
      - 1558M
```

## Model Sizes

| Size | Parameters | Layers | Heads | Channels | Use Case |
|------|------------|--------|-------|----------|----------|
| 124M | 124M | 12 | 12 | 768 | Fast experimentation |
| 350M | 350M | 24 | 16 | 1024 | Balanced performance |
| 774M | 774M | 36 | 20 | 1280 | High quality |
| 1558M | 1558M | 48 | 25 | 1600 | Best quality |

## Comparison with Other Backends

| Feature | llama2.c | nanoGPT | GPT-2 (HF) | llm.c |
|---------|----------|---------|------------|-------|
| Framework | PyTorch + C | PyTorch | PyTorch (HF) | C/CUDA |
| Training Speed | Fast | Fast | Fast | Very Fast (~7% faster than PyTorch) |
| Inference Speed | Very Fast (C) | Fast | Fast | Very Fast (C) |
| Model Sizes | 15M, 42M, 110M | Custom | 124M, 355M, 774M, 1558M | 124M, 350M, 774M, 1558M |
| Pre-trained Weights | No | No | Yes | No (but can init from GPT-2) |
| Multi-GPU | No | Yes | Yes | Yes (NCCL) |
| Multi-Node | No | No | No | Yes (NCCL + MPI) |
| Mixed Precision | Yes | Yes | Yes | Yes (BF16/FP16) |
| Flash Attention | No | No | No | Yes (cuDNN) |
| Dependencies | PyTorch | PyTorch | PyTorch + Transformers | None (for CPU), CUDA (for GPU) |
| Educational Value | High | High | Medium | Very High |
| Ease of Use | Medium | High | Very High | Medium |

## Continuous Learning System

### How It Works

1. **Data Collection**: Bug bounty reports are continuously collected from HackerOne, Bugcrowd, etc.

2. **Training Trigger**: When 1000+ new reports accumulate, training is triggered

3. **Multi-Backend Training**: All four backends (llama2.c, nanoGPT, GPT-2, llm.c) train on the same data

4. **Evaluation**: Each model is evaluated on test prompts after training

5. **Comparison**: Models are compared based on perplexity, loss, and generation time

6. **Reporting**: A comprehensive report is generated showing:
   - Performance metrics for each model
   - Improvement trends over time
   - Rankings by performance
   - Recommendations for retraining

### Evaluation Metrics

- **Perplexity**: Lower is better (measures how well the model predicts the data)
- **Loss**: Training/validation loss
- **Generation Time**: Latency for text generation
- **Success Rate**: Percentage of successful generations

### Retraining Strategy

The system recommends retraining when:
- Performance degrades by >10% (perplexity increase)
- New data patterns emerge (detected via evaluation)
- Configured time interval elapses

## Inference

### Current Status

llm.c is primarily a **training** library. Inference support is limited:

- **Training**: Full support for all model sizes
- **Inference**: Placeholder implementation (requires building separate inference binary)

### Recommended Approach

For inference, use:
- **GPT-2 (HuggingFace)**: Best for production inference with pre-trained weights
- **llama2.c**: Fast C inference for custom-trained models
- **llm.c**: Currently only for training; inference not yet implemented

### Future Work

To add full llm.c inference support:
1. Build a separate inference binary from llm.c
2. Create Python bindings for the inference binary
3. Integrate with the model server
4. Add support for streaming generation

## Advanced Usage

### Multi-GPU Training

Train on multiple GPUs:

```bash
# Install NCCL and MPI
sudo apt install openmpi-bin openmpi-doc libopenmpi-dev
# Follow NCCL installation instructions from NVIDIA

# Train with 4 GPUs
cd llm.c/llm.c-master
make train_gpt2cu
mpirun -np 4 ./train_gpt2cu -i ../data/llmc -o ../models/llmc
```

### Flash Attention

Enable cuDNN Flash Attention for faster training:

```bash
# Install cuDNN
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install libcudnn9-dev-cuda-12

# Clone cuDNN frontend
git clone https://github.com/NVIDIA/cudnn-frontend.git ~/cudnn-frontend

# Compile with cuDNN
cd llm.c/llm.c-master
make train_gpt2cu USE_CUDNN=1
```

### Precision Modes

Choose precision based on your hardware:

```yaml
llmc:
  precision: BF16  # Best for modern GPUs (A100, H100, RTX 30/40 series)
  # precision: FP16  # For older GPUs
  # precision: FP32  # Maximum precision, slower
```

## Troubleshooting

### Compilation Errors

**Problem**: `nvcc not found`
- **Solution**: Install CUDA Toolkit from NVIDIA

**Problem**: cuDNN errors
- **Solution**: Set `use_cudnn: false` in config.yaml or install cuDNN

**Problem**: OpenMP not found
- **Solution**: Install libomp (macOS: `brew install libomp`, Linux: `sudo apt install libomp-dev`)

### Training Errors

**Problem**: Data files not found
- **Solution**: Run `python training_pipeline/prepare_llmc.py` first

**Problem**: Out of memory
- **Solution**: Reduce `batch_size` in config.yaml or use a smaller model size

**Problem**: Slow training on CPU
- **Solution**: Use GPU training or reduce model size

### Performance Issues

**Problem**: Training slower than expected
- **Solution**: Enable cuDNN Flash Attention, use BF16 precision, increase batch size

**Problem**: Poor model quality
- **Solution**: Train for more steps, increase learning rate, use more data

## File Structure

```
SubFluxGPT/
├── llm.c/                          # llm.c source code
│   └── llm.c-master/
│       ├── train_gpt2.c            # CPU training
│       ├── train_gpt2.cu           # GPU training (CUDA)
│       ├── train_gpt2.py           # PyTorch reference
│       ├── dev/data/               # Dataset scripts
│       └── scripts/                # Training scripts
├── training_pipeline/
│   ├── prepare_llmc.py             # Data preparation for llm.c
│   ├── train_llmc.py               # llm.c training wrapper
│   ├── scheduler.py                # Training scheduler (modified)
│   └── evaluator.py               # Model evaluation (new)
├── inference/
│   ├── llmc_inference.py           # llm.c inference wrapper (new)
│   └── model_server.py             # Model server (modified)
├── data/
│   └── llmc/                       # llm.c training data
│       ├── bugbounty_train.bin
│       └── bugbounty_val.bin
├── models/
│   └── llmc/                       # llm.c model checkpoints
├── metrics/                        # Evaluation metrics (new)
│   ├── model_metrics.json
│   └── evaluation_report.md
└── config.yaml                     # Configuration (modified)
```

## References

- [llm.c GitHub Repository](https://github.com/karpathy/llm.c)
- [GPT-2 Paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [Karpathy's Zero to Hero Course](https://github.com/karpathy/nn-zero-to-hero)
- [nanoGPT](https://github.com/karpathy/nanoGPT)
- [llama2.c](https://github.com/karpathy/llama2.c)

## Contributing

To improve llm.c integration:

1. Add support for more model architectures (GPT-3, LLaMA, etc.)
2. Implement full inference support
3. Add automatic hyperparameter tuning
4. Integrate with more evaluation metrics (BLEU, ROUGE, etc.)
5. Add distributed training orchestration

## License

llm.c is licensed under MIT. SubFluxGPT maintains its own license (see LICENSE file).
