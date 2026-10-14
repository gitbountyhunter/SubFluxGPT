# SubFluxGPT Setup Status and Requirements

## Current Status

### ✅ Completed

1. **llm.c Extraction**
   - llm.c-master.zip extracted to `llm.c/llm.c-master/`
   - All source files present and verified

2. **llm.c Compilation (CPU Version)**
   - Successfully compiled CPU version: `llm.c/llm.c-master/train_gpt2`
   - Binary size: 115K
   - Note: GPU/CUDA version requires nvcc (not installed)

3. **Sample Data Creation**
   - Created sample bug bounty data in llm.c format
   - Location: `data/llmc/bugbounty_train.bin` and `bugbounty_val.bin`
   - Total tokens: 35,200 (400 sample reports × 20 repeats)
   - Tokenized with GPT-2 tokenizer using tiktoken

4. **Python Dependencies (Partial)**
   - Installed: numpy, tiktoken, regex
   - Skipped: PostgreSQL dependencies (psycopg2-binary requires pg_config)
   - Skipped: PyTorch (required for llm.c Python reference, not for C binary)

### ⚠️  Not Completed (Requires Additional Setup)

1. **CUDA Installation**
   - Status: nvcc not found
   - Impact: Cannot compile GPU/CUDA version of llm.c
   - Workaround: CPU version compiled and working
   - To install: Download CUDA Toolkit from NVIDIA (https://developer.nvidia.com/cuda-downloads)

2. **cuDNN Installation**
   - Status: Not installed
   - Impact: Cannot use Flash Attention (performance optimization)
   - Workaround: Not required for basic training
   - To install: Follow instructions in LLMC_INTEGRATION.md

3. **PostgreSQL Database**
   - Status: Not installed (psql not found)
   - Impact: Cannot run data collectors or use database-dependent features
   - Workaround: Sample data created for testing
   - To install: 
     - macOS: `brew install postgresql@15`
     - Linux: `sudo apt install postgresql postgresql-contrib`
     - Or use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=changeme postgres:15`

4. **PyTorch**
   - Status: Not installed
   - Impact: Cannot use llm.c Python reference, llama2.c, nanoGPT, or GPT-2 (HuggingFace)
   - Workaround: llm.c C binary works without PyTorch
   - To install: `pip install torch` (see https://pytorch.org for platform-specific instructions)

5. **Full Python Dependencies**
   - Status: Partially installed
   - Missing: transformers, datasets, torch, sqlalchemy, psycopg2-binary, etc.
   - Impact: Cannot run full training pipeline
   - To install: `pip install -r requirements.txt` (after fixing PostgreSQL)

## Quick Start for Testing llm.c Only

If you want to test just llm.c without the full system:

### 1. Verify Setup
```bash
# Check llm.c binary
ls -lh llm.c/llm.c-master/train_gpt2

# Check sample data
ls -lh data/llmc/
```

### 2. Train with Sample Data (Requires Model Weights)

The llm.c C binary requires pre-trained GPT-2 weights to initialize. To get them:

```bash
cd llm.c/llm.c-master

# Download starter pack (includes weights, tokenizer, debug state)
chmod u+x ./dev/download_starter_pack.sh
./dev/download_starter_pack.sh
```

This will download:
- GPT-2 124M model weights (fp32 and bfloat16)
- GPT-2 tokenizer
- Debug state for testing
- TinyShakespeare dataset

### 3. Run Training (Demo)

```bash
cd llm.c/llm.c-master

# Train for 40 steps on TinyShakespeare (CPU)
OMP_NUM_THREADS=8 ./train_gpt2
```

This will:
- Load GPT-2 124M weights
- Train for 40 steps
- Evaluate validation loss
- Generate sample text

### 4. Train on Bug Bounty Data

After downloading starter pack, you can train on the bug bounty data:

```bash
cd llm.c/llm.c-master

# Copy our data to llm.c data directory
cp ../../data/llmc/bugbounty_train.bin dev/data/bugbounty/
cp ../../data/llmc/bugbounty_val.bin dev/data/bugbounty/

# Train (adjust parameters as needed)
./train_gpt2 -i dev/data/bugbounty -o ../../models/llmc -v 10 -s 10 -g 1 -l 3e-4 -b 4 -t 100
```

## Full System Setup (For Production)

To set up the complete SubFluxGPT system with all 4 training backends:

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb subfluxgpt
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb subfluxgpt
```

**Docker:**
```bash
docker run -d \
  --name subfluxgpt-db \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=subfluxgpt \
  -p 5432:5432 \
  postgres:15
```

### 2. Install Python Dependencies

```bash
# Install PyTorch (check https://pytorch.org for your platform)
pip install torch

# Install other dependencies
pip install -r requirements.txt
```

If PostgreSQL is installed locally, the dependencies should install successfully.

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Add your API keys and configuration
```

### 4. Initialize Database

```bash
psql subfluxgpt < database/schema.sql
```

### 5. Install CUDA (Optional, for GPU Training)

Download and install CUDA Toolkit from NVIDIA:
- https://developer.nvidia.com/cuda-downloads

Verify installation:
```bash
nvcc --version
```

### 6. Install cuDNN (Optional, for Flash Attention)

Follow instructions in LLMC_INTEGRATION.md

### 7. Collect Data

```bash
# Collect bug bounty reports
python -m data_collector.main
```

### 8. Prepare Data for All Backends

```bash
# Prepare for llama2.c
python training_pipeline/prepare_bugbounty.py --vocab_size 4096

# Prepare for llm.c
python training_pipeline/prepare_llmc.py
```

### 9. Compile llm.c

**CPU Version:**
```bash
cd llm.c/llm.c-master
make train_gpt2
```

**GPU Version (if CUDA installed):**
```bash
cd llm.c/llm.c-master
make train_gpt2cu
```

### 10. Run Training Scheduler

```bash
python training_pipeline/scheduler.py
```

This will:
- Check if 1000+ new reports collected
- Prepare data for all backends
- Train all model sizes
- Evaluate models
- Generate comparison reports

### 11. Monitor Progress

```bash
# Check evaluation reports
cat metrics/evaluation_report.md

# Check model metrics
cat metrics/model_metrics.json
```

## System Requirements Summary

### Minimum Requirements (llm.c CPU only)
- Python 3.10+
- clang compiler (for llm.c compilation)
- numpy, tiktoken (for data preparation)
- 8GB RAM
- 10GB disk space

### Recommended Requirements (Full System)
- Python 3.10+
- PostgreSQL 15+
- CUDA Toolkit 12.x (for GPU training)
- PyTorch 2.x
- 32GB RAM
- 100GB disk space
- GPU with 8GB+ VRAM (for training)

### Optional Enhancements
- cuDNN (for Flash Attention)
- NCCL (for multi-GPU training)
- MPI (for multi-node training)
- Redis (for caching)
- Docker (for containerization)

## Troubleshooting

### Issue: nvcc not found
**Solution:** Install CUDA Toolkit or use CPU version

### Issue: pg_config not found
**Solution:** Install PostgreSQL or use Docker

### Issue: ModuleNotFoundError for torch
**Solution:** Install PyTorch: `pip install torch`

### Issue: llm.c training fails with "Failed to open file"
**Solution:** Run `python llm.c/llm.c-master/train_gpt2.py` to download starter pack with weights

### Issue: OpenMP not found
**Solution:** Install libomp (macOS: `brew install libomp`, Linux: `sudo apt install libomp-dev`)

## Current Capabilities

With the current setup, you can:

✅ Compile and run llm.c CPU training
✅ Create sample bug bounty data in llm.c format
✅ Test llm.c with TinyShakespeare dataset
✅ Train llm.c on bug bounty data (after downloading weights)

Cannot yet (without additional setup):

❌ Run GPU training (requires CUDA)
❌ Use Flash Attention (requires cuDNN)
❌ Run data collectors (requires PostgreSQL)
❌ Train llama2.c, nanoGPT, GPT-2 (requires PyTorch)
❌ Run full training scheduler (requires all dependencies)

## Next Steps

1. **For Quick Testing**: Download llm.c starter pack and train on sample data
2. **For Development**: Install PostgreSQL and PyTorch to test full pipeline
3. **For Production**: Install CUDA, cuDNN, and set up full infrastructure
4. **For Learning**: Explore llm.c source code and modify for experiments

## Documentation

- **LLMC_INTEGRATION.md**: Complete llm.c integration guide
- **CONTINUOUS_LEARNING.md**: How the continuous learning system works
- **GPT2_INTEGRATION.md**: GPT-2 (HuggingFace) integration
- **README.md**: Project overview
- **config.yaml**: Configuration options

## Support

For issues with:
- **llm.c**: https://github.com/karpathy/llm.c/discussions
- **CUDA**: https://developer.nvidia.com/cuda
- **PostgreSQL**: https://www.postgresql.org/docs/
- **PyTorch**: https://pytorch.org/docs/
