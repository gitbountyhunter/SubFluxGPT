# Continuous Learning System for SubFluxGPT

## Overview

SubFluxGPT implements a continuous learning system where models automatically improve over time as they are trained on new bug bounty reports from HackerOne, Bugcrowd, and other platforms. This document explains how the system works and how models get better.

## How Models Learn

### 1. Data Collection Pipeline

**Sources:**
- HackerOne disclosed reports (via HuggingFace dataset or API)
- Bugcrowd disclosed reports (via API)
- YesWeHack disclosed reports (via API)
- Future: Intigriti, Synack, etc.

**Process:**
1. Collectors run periodically (default: every hour)
2. Reports are extracted with full content
3. Data is normalized and stored in PostgreSQL database
4. Domains/subdomains are extracted and validated
5. Reports are tagged with metadata (vulnerability type, severity, program, etc.)

### 2. Training Trigger

The system automatically triggers training when:
- **New reports accumulate**: Default threshold is 1000 new reports
- **Manual trigger**: Run scheduler manually
- **Scheduled runs**: Configurable time intervals (e.g., weekly)

**Why 1000 reports?**
- Sufficient data for meaningful training
- Balances training frequency with computational cost
- Prevents overfitting on small batches
- Allows models to see diverse vulnerability patterns

### 3. Multi-Backend Training

All four training backends train on the same data:

| Backend | Purpose | Strengths |
|---------|---------|-----------|
| **llama2.c** | Fast C inference | Lightweight, fast training |
| **nanoGPT** | Flexible PyTorch | Easy to modify, good research |
| **GPT-2 (HF)** | Production inference | Pre-trained weights, well-maintained |
| **llm.c** | High-performance C/CUDA | Fastest training, educational |

**Benefits of Multiple Backends:**
- **Redundancy**: If one backend fails, others continue
- **Comparison**: See which architecture performs best
- **Specialization**: Different backends for different use cases
- **Robustness**: Diverse approaches reduce single points of failure

### 4. Data Preparation

Each backend receives data in its preferred format:

**llama2.c:**
- Tokenized with custom tokenizer
- Saved as .bin files with metadata
- Vocabulary size: 4096

**nanoGPT:**
- Text format with GPT-2 tokenizer
- Block size: 256 tokens
- Flexible vocabulary

**GPT-2 (HuggingFace):**
- Text format with GPT-2 tokenizer
- Block size: 512 tokens
- Pre-trained vocabulary (50257)

**llm.c:**
- Tokenized with GPT-2 tokenizer (tiktoken)
- Saved as .bin files with C-compatible header
- Format: uint16 tokens with 256-int32 header
- Vocabulary size: 50257

### 5. Training Process

For each model size (e.g., 124M, 42M, 350M):

1. **Initialize**: Load pre-trained weights (if available) or random init
2. **Train**: Run training loop with configured hyperparameters
3. **Validate**: Evaluate on validation set periodically
4. **Checkpoint**: Save best models based on validation loss
5. **Sample**: Generate sample text to monitor progress

**Hyperparameters (configurable):**
- Learning rate: 3e-4 to 5e-5
- Batch size: 4 to 64
- Gradient accumulation: 4 to 8
- Max steps/epochs: 5000 to 100000
- Evaluation interval: Every 250-2000 steps

### 6. Model Evaluation

After training, each model is evaluated:

**Test Prompts:**
- "Program: example.com\nReport title: XSS vulnerability"
- "Analyze the domain: test.com for potential issues"
- Custom prompts based on recent vulnerabilities

**Metrics Tracked:**
- **Perplexity**: How well the model predicts the data (lower is better)
- **Loss**: Training/validation loss
- **Generation Time**: Latency for text generation
- **Success Rate**: Percentage of successful generations
- **Quality**: Human evaluation of generated reports

**Comparison:**
- Models are ranked by performance
- Trends are tracked over time
- Best model is identified for each use case

### 7. Continuous Improvement Loop

```
Collect Reports → Store in DB → Trigger Training (1000+ reports)
     ↓
Prepare Data (4 formats) → Train Models (4 backends × N sizes)
     ↓
Evaluate Models → Compare Performance → Generate Report
     ↓
Deploy Best Models → Collect More Reports → Repeat
```

## How Models Get Better

### 1. More Data

**Primary Improvement Driver:**
- **Volume**: More reports = more examples to learn from
- **Variety**: Different programs, vulnerability types, industries
- **Recency**: Recent reports reflect current attack patterns
- **Quality**: Disclosed reports are vetted and accurate

**Impact:**
- Better understanding of vulnerability patterns
- Improved domain analysis
- More accurate vulnerability prediction
- Better report generation

### 2. Regular Retraining

**Why Retrain Regularly:**
- **Concept Drift**: New vulnerability types emerge
- **Pattern Evolution**: Attack techniques change
- **Domain Changes**: New technologies, frameworks
- **Quality Improvement**: Models learn from their mistakes

**Retraining Strategy:**
- Automatic when 1000+ new reports
- Manual on-demand for urgent updates
- Scheduled (e.g., weekly) for consistency
- Performance-based (if metrics degrade >10%)

### 3. Hyperparameter Tuning

**Optimization Areas:**
- Learning rate schedules
- Batch sizes
- Model architectures
- Training duration

**Approach:**
- Grid search on small datasets
- Bayesian optimization for production
- Learning from successful training runs
- A/B testing different configurations

### 4. Ensemble Methods

**Future Enhancement:**
- Combine predictions from multiple models
- Weight models by performance
- Specialized models for different vulnerability types
- Voting systems for consensus

### 5. Feedback Loop

**Human-in-the-Loop:**
- Security researchers review generated reports
- Feedback used to fine-tune models
- Bad generations flagged for improvement
- Good patterns reinforced

**Automated Feedback:**
- Compare generated reports with real reports
- Measure similarity metrics
- Track which patterns lead to good predictions
- Adjust training based on success metrics

## Evaluation and Metrics

### Performance Tracking

**Stored in `metrics/model_metrics.json`:**
```json
{
  "llama2c_42M": [
    {
      "timestamp": "2026-10-14T12:00:00",
      "metrics": {
        "perplexity": 15.3,
        "loss": 2.73,
        "avg_generation_time_ms": 234,
        "success_rate": 0.95
      }
    }
  ]
}
```

**Trend Analysis:**
- Track perplexity over time (should decrease)
- Monitor loss curves
- Compare generation speed
- Identify performance degradation

### Comparison Reports

**Generated in `metrics/evaluation_report.md`:**
- Model rankings by performance
- Improvement trends
- Best model for each use case
- Recommendations for retraining

## Deployment Strategy

### Model Selection

**For Inference:**
- **Fast response**: llama2.c (C inference)
- **High quality**: GPT-2 (HuggingFace) with fine-tuning
- **Best accuracy**: llm.c trained models (when inference is implemented)
- **Balanced**: Compare and choose based on metrics

**For Training:**
- Train all backends for redundancy
- Deploy best-performing model
- Keep previous versions for rollback
- A/B test new models before full deployment

### Rollout Process

1. **Train**: New models on latest data
2. **Evaluate**: Compare with current models
3. **Test**: Run in parallel with current models
4. **Monitor**: Track performance in production
5. **Deploy**: Switch if improvement is significant
6. **Rollback**: Keep previous models if issues arise

## Failure Handling

### Training Failures

**Common Issues:**
- Insufficient data
- GPU memory errors
- Compilation errors
- Data format issues

**Recovery:**
- Log errors for debugging
- Skip failed backend, continue with others
- Alert administrators for manual intervention
- Keep previous models as fallback

### Performance Degradation

**Detection:**
- Automatic monitoring of metrics
- Perplexity increase >10%
- Loss increase >10%
- User complaints

**Recovery:**
- Automatic retraining trigger
- Rollback to previous model
- Investigate data quality issues
- Adjust hyperparameters

## Scalability

### Horizontal Scaling

**Multi-GPU Training:**
- llm.c supports NCCL for multi-GPU
- Train larger models faster
- Distribute across multiple nodes

**Distributed Collection:**
- Multiple collector instances
- Load balancing across platforms
- Parallel data processing

### Vertical Scaling

**Model Sizes:**
- Start small (15M, 42M) for quick iteration
- Scale up (110M, 350M) for better quality
- Use largest (774M, 1558M) for production

**Infrastructure:**
- Cloud GPUs for training
- CPUs for data collection
- Fast storage for checkpoints
- Monitoring and alerting

## Future Enhancements

### Planned Features

1. **Active Learning**
   - Select most informative reports for training
   - Prioritize rare vulnerability types
   - Balance dataset distribution

2. **Curriculum Learning**
   - Start with simple vulnerabilities
   - Progress to complex patterns
   - Adapt difficulty based on performance

3. **Transfer Learning**
   - Pre-train on general cybersecurity data
   - Fine-tune on bug bounty reports
   - Use knowledge from related domains

4. **Reinforcement Learning**
   - Optimize for specific metrics
   - Learn from human feedback
   - Improve report quality over time

5. **Automated Hyperparameter Tuning**
   - Bayesian optimization
   - Neural architecture search
   - Automated learning rate schedules

## Monitoring and Observability

### Key Metrics

**Training Metrics:**
- Loss curves
- Perplexity trends
- Training time
- GPU utilization

**Inference Metrics:**
- Generation latency
- Success rate
- User satisfaction
- Error rates

**System Metrics:**
- Report collection rate
- Database size
- Storage usage
- API response times

### Alerts

**Trigger Alerts When:**
- Training fails
- Performance degrades >10%
- Data collection stops
- Disk space <10%
- GPU utilization <50% during training

## Conclusion

The continuous learning system ensures that SubFluxGPT models improve over time by:

1. **Regularly ingesting new bug bounty reports**
2. **Training multiple model architectures on the same data**
3. **Evaluating and comparing performance**
4. **Deploying the best-performing models**
5. **Iterating based on feedback and metrics**

This creates a virtuous cycle where models get better with each training cycle, leading to more accurate vulnerability detection, better domain analysis, and higher-quality report generation.

The multi-backend approach provides robustness and allows the system to leverage the strengths of different architectures, while the evaluation system ensures that only the best models are deployed to production.
