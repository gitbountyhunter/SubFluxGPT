# Mini AI Operations Guide

Complete guide to operating, training, and optimizing SubFluxGPT's mini AIs for maximum intelligence in bug bounty reconnaissance.

## Table of Contents
1. [Introduction](#introduction)
2. [Mini AI Architecture](#mini-ai-architecture)
3. [Getting Started](#getting-started)
4. [Training Mini AIs](#training-mini-ais)
5. [Feeding Information to Mini AIs](#feeding-information-to-mini-ais)
6. [Continuous Learning](#continuous-learning)
7. [Fine-Tuning with Unsloth/QLoRA](#fine-tuning-with-unslothqlora)
8. [Benchmarking and Evaluation](#benchmarking-and-evaluation)
9. [Optimization Strategies](#optimization-strategies)
10. [Advanced Workflows](#advanced-workflows)

---

## Introduction

SubFluxGPT includes 4 mini AI models that continuously learn and improve:

1. **llama2.c** - C-based GPT-2 implementation (15M, 42M, 110M params)
2. **nanoGPT** - PyTorch-based minimal GPT (124M, 355M, 774M, 1558M params)
3. **GPT-2** - Original OpenAI GPT-2 (124M, 355M, 774M, 1558M params)
4. **llm.c** - Karpathy's educational implementation (124M, 350M, 774M, 1558M params)

These mini AIs learn from:
- Every command you run
- Tool outputs (httpx, subfinder, nuclei, etc.)
- Bug bounty reports (HackerOne, Bugcrowd)
- Workflow patterns
- Successful recon findings

---

## Mini AI Architecture

### Model Sizes

| Backend | Model Sizes | Parameters | Use Case |
|---------|-------------|------------|----------|
| llama2.c | 15M, 42M, 110M | Minimal | Quick analysis, pattern matching |
| nanoGPT | 124M, 355M, 774M, 1558M | Small-Medium | Tool output analysis, command suggestion |
| GPT-2 | 124M, 355M, 774M, 1558M | Small-Medium | Text generation, vulnerability classification |
| llm.c | 124M, 350M, 774M, 1558M | Small-Medium | Educational, custom training |

### Training Backends

1. **llama2.c** - Pure C, ultra-fast inference
2. **nanoGPT** - PyTorch, flexible training
3. **GPT-2** - HuggingFace, easy fine-tuning
4. **llm.c** - Educational, custom CUDA kernels

---

## Getting Started

### Quick Start (5 minutes)

```bash
# 1. Train your first mini AI (124M, CPU)
subfluxgpt train --model_size 124M --use_gpu=False --verbose

# 2. Start the inference server
subfluxgpt server --verbose

# 3. Test it
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this HTTP response for vulnerabilities", "model": "gpt2_124M"}'
```

### Activate the Alias

```bash
# The alias is already added to your .zshrc
# Reload your shell or run:
source ~/.zshrc

# Now you can use:
subfluxgpt train --model_size 124M --verbose
subfluxgpt cloud --enhanced --apex example.com
subfluxgpt recon --domain example.com
```

---

## Training Mini AIs

### Basic Training

```bash
# Train with llama2.c backend
subfluxgpt train --model_size 124M --use_gpu=False --verbose

# Train with nanoGPT backend
python3 training_pipeline/train_gpt2.py --model_size 124M --verbose

# Train with llm.c backend
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False --verbose
```

### Training Options

```bash
subfluxgpt train --help

Options:
  --model_size       Model size (15M, 42M, 110M, 124M, 350M, 355M, 774M, 1558M)
  --use_gpu          Use GPU for training (default: False)
  --epochs           Number of training epochs (default: 10)
  --batch_size       Batch size (default: 4)
  --learning_rate    Learning rate (default: 1e-3)
  --verbose          Enable verbose logging
```

### Training from Bug Bounty Data

```bash
# Prepare dataset from learning database
subfluxgpt fine-tune --prepare-dataset

# Fine-tune with prepared dataset
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune \
  --model-size 124M --epochs 3 --batch-size 4
```

---

## Feeding Information to Mini AIs

### Method 1: Automatic Learning (Recommended)

The continuous learning system automatically learns from:

1. **Commands you run**
   ```bash
   # Every command is logged
   subfluxgpt recon --domain example.com
   # Mini AI learns: this is a successful pattern
   ```

2. **Tool outputs**
   ```bash
   # Tool outputs are analyzed
   httpx -u example.com -silent -json
   # Mini AI learns: analyze HTTP responses
   ```

3. **Bug bounty reports**
   ```bash
   # Reports are fed automatically
   subfluxgpt learn --start
   # Mini AI learns from real vulnerabilities
   ```

### Method 2: Manual Data Feeding

```bash
# Add custom training data
python3 -c "
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()
learner.log_command('httpx', ['-u', 'example.com'], 0, 5.2)
learner.log_tool_output('httpx', 'httpx -u example.com', '200 OK', '')
learner.log_finding('httpx', 'alive_host', 'info', 'example.com')
"
```

### Method 3: Dataset Preparation

```bash
# Export learning data as training dataset
python3 -c "
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()
learner.export_training_dataset('data/custom_dataset.json')
"
```

---

## Continuous Learning

### Enable Continuous Learning

```bash
# Start the continuous learning daemon
subfluxgpt learn --start

# This runs in the background and:
# - Logs every command you run
# - Analyzes tool outputs
# - Extracts patterns
# - Updates training data
```

### Monitor Learning Progress

```bash
# Check learning statistics
python3 -c "
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()
stats = learner.get_learning_stats()
print(json.dumps(stats, indent=2))
"
```

Output:
```json
{
  "total_commands": 1523,
  "successful_commands": 1498,
  "total_outputs": 1523,
  "total_workflows": 45,
  "total_findings": 234,
  "findings_by_severity": {
    "critical": 12,
    "high": 45,
    "medium": 89,
    "low": 88
  }
}
```

### Get Successful Workflows

```bash
# See what workflows work best
python3 -c "
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()
workflows = learner.get_successful_workflows(min_success=5)
for wf in workflows:
    print(f\"{wf['pattern']}: {wf['success_count']} successes\")
"
```

---

## Fine-Tuning with Unsloth/QLoRA

### Install Unsloth

```bash
# Install Unsloth (recommended for Mac)
brew install --cask unsloth

# Or install manually
curl -fsSL https://unsloth.ai/install.sh | sh
```

### Prepare Dataset

```bash
# Prepare bug bounty dataset
subfluxgpt fine-tune --prepare-dataset
```

### Fine-Tune with QLoRA

```bash
# Fine-tune 124M model
subfluxgpt fine-tune --finetune \
  --dataset data/datasets/bugbounty_finetune \
  --model-size 124M \
  --epochs 3 \
  --batch-size 4 \
  --learning-rate 2e-4
```

### Evaluate Fine-Tuned Model

```bash
# Evaluate model performance
subfluxgpt fine-tune --evaluate \
  models/finetuned/finetuned_124M_20261014 \
  --dataset data/datasets/test_dataset
```

### QLoRA Benefits

- **Memory Efficient**: Fine-tune 65B models on single GPU
- **No Accuracy Loss**: Full 16-bit performance
- **Fast Training**: 2x faster with 70% less VRAM
- **Quantization**: 4-bit NF4 quantization

---

## Benchmarking and Evaluation

### Run Benchmarks

```bash
# Benchmark all models
subfluxgpt benchmark --domain example.com --verbose --advanced-report
```

### Benchmark Options

```bash
subfluxgpt benchmark --help

Options:
  --domain           Target domain for testing
  --models           Models to benchmark (comma-separated)
  --backends         Backends to test (comma-separated)
  --verbose          Enable verbose logging
  --advanced-report  Generate advanced statistical report
```

### Benchmark Metrics

- **Memory Usage**: RAM/VRAM consumption
- **Throughput**: Tokens per second
- **Latency**: Response time
- **Accuracy**: Task performance
- **Statistical Analysis**: Mean, std dev, median

### View Benchmark Results

```bash
# Results saved to: data/benchmarking/results_*.json
cat data/benchmarking/results_20261014_143022.json
```

---

## Optimization Strategies

### 1. Model Selection

```bash
# For quick analysis (low latency)
subfluxgpt train --model_size 15M --use_gpu=False

# For complex analysis (higher accuracy)
subfluxgpt train --model_size 774M --use_gpu=True
```

### 2. Batch Processing

```bash
# Process multiple domains at once
for domain in $(cat domains.txt); do
  subfluxgpt recon --domain $domain --verbose
done
```

### 3. Pipeline Optimization

```bash
# Use AI-integrated tool wrapper
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper

wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com'], enable_ai=True)
print(result['ai_analysis'])
"
```

### 4. Continuous Improvement

```bash
# Always run learning in background
subfluxgpt learn --start &

# Monitor bug bounty platforms
subfluxgpt monitor --interval 3600 &
```

---

## Advanced Workflows

### Workflow 1: Full AI-Powered Recon

```bash
# 1. Discover subdomains with AI analysis
subfinder -d example.com -silent | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-silent', '-json'], enable_ai=True)
print(result['ai_analysis'])
"

# 2. Crawl with AI endpoint extraction
katana -u example.com -silent -json | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('nuclei', ['-silent', '-json'], enable_ai=True)
print(result['ai_analysis'])
"
```

### Workflow 2: Self-Improving Loop

```bash
# Start self-improving LLM
subfluxgpt learn --start

# Start bug bounty monitor
subfluxgpt monitor --interval 3600

# Run recon (learning from every command)
subfluxgpt recon --domain example.com --verbose
```

### Workflow 3: Custom Fine-Tuning

```bash
# 1. Collect data from your workflows
subfluxgpt recon --domain target1.com
subfluxgpt recon --domain target2.com
subfluxgpt recon --domain target3.com

# 2. Prepare dataset
subfluxgpt fine-tune --prepare-dataset

# 3. Fine-tune model
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune

# 4. Use fine-tuned model
subfluxgpt server --model models/finetuned/finetuned_124M
```

---

## Best Practices

### 1. Start Small
- Begin with 124M models
- Train on CPU first
- Scale up as needed

### 2. Feed Quality Data
- Use real bug bounty reports
- Include successful workflows
- Log failed attempts too

### 3. Monitor Performance
- Check benchmark results regularly
- Track learning statistics
- Evaluate fine-tuned models

### 4. Iterate Continuously
- Run learning in background
- Update models weekly
- Experiment with hyperparameters

### 5. Use AI Integration
- Enable AI analysis on all tools
- Learn from every command
- Automate repetitive tasks

---

## Troubleshooting

### Issue: Model training is slow

**Solution**:
```bash
# Use smaller model
subfluxgpt train --model_size 15M --use_gpu=False

# Reduce batch size
subfluxgpt train --model_size 124M --batch-size 2
```

### Issue: Out of memory

**Solution**:
```bash
# Use QLoRA quantization
subfluxgpt fine-tune --finetune --dataset ... --use-gpu

# Reduce model size
subfluxgpt train --model_size 124M
```

### Issue: Learning data not being saved

**Solution**:
```bash
# Check database exists
ls -la data/learning/learning.db

# Reinitialize database
rm data/learning/learning.db
subfluxgpt learn --start
```

---

## Resources

- [MASTER_COMMAND_GUIDE.md](MASTER_COMMAND_GUIDE.md) - Complete command reference
- [AI_WORKFLOWS.md](AI_WORKFLOWS.md) - AI workflow documentation
- [CONTINUOUS_LEARNING.md](CONTINUOUS_LEARNING.md) - Learning system details
- [Unsloth Documentation](https://unsloth.ai/docs) - Fine-tuning guide
- [QLoRA Paper](https://arxiv.org/abs/2305.14314) - Research paper

---

## Summary

SubFluxGPT's mini AIs are designed to:
- ✅ Learn from every command you run
- ✅ Analyze tool outputs automatically
- ✅ Improve with bug bounty reports
- ✅ Fine-tune efficiently with QLoRA
- ✅ Benchmark and optimize continuously

**Key Commands**:
- `subfluxgpt train` - Train models
- `subfluxgpt learn` - Continuous learning
- `subfluxgpt fine-tune` - Fine-tune with Unsloth
- `subfluxgpt benchmark` - Evaluate performance
- `subfluxgpt monitor` - Monitor bug bounty platforms

**Next Steps**:
1. Train your first model: `subfluxgpt train --model_size 124M --verbose`
2. Start learning: `subfluxgpt learn --start`
3. Enable monitoring: `subfluxgpt monitor --interval 3600`
4. Fine-tune after data collection: `subfluxgpt fine-tune --prepare-dataset`

---

*Last Updated: 2026-10-14*
*System: Mac (32GB RAM, 8-core, 19 CPU)*
