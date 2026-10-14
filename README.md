# SubFluxGPT

A self-generating system that continuously monitors bug bounty platforms (HackerOne, Bugcrowd, YesWeHack, etc.), extracts domains/subdomains from disclosed reports, and trains AI models (llama2.c, nanoGPT, GPT-2, and llm.c) for continuous improvement.

## Architecture

SubFluxGPT consists of several interconnected components:

1. **Data Collection Layer** - Monitors multiple bug bounty platforms
2. **Data Processing Layer** - Extracts and normalizes domains/subdomains
3. **Training Pipeline** - Feeds data to llama2.c, nanoGPT, GPT-2, and llm.c models
4. **Continuous Learning Loop** - Retrains models with new data
5. **Inference Server** - Exposes model capabilities for testing
6. **Monitoring Dashboard** - Tracks system health and performance

## Features

- **Multi-Platform Support**: HackerOne, Bugcrowd, YesWeHack (with extensible architecture for more)
- **Automatic Domain Extraction**: Uses regex and NLP to extract domains from reports
- **Domain Validation**: Async DNS validation and Certificate Transparency log checks
- **Continuous Training**: Trains multiple model sizes (15M, 42M, 110M) automatically
- **Docker Support**: Fully containerized deployment with docker-compose
- **Monitoring Dashboard**: Web interface for tracking system metrics
- **24/7 Operation**: Systemd services for continuous operation

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)
- CUDA-capable GPU (for training)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd SubFluxGPT
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` with your API keys and configuration:
```bash
nano .env
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Docker Deployment (Recommended)

1. Start all services:
```bash
docker-compose up -d
```

2. Check service status:
```bash
docker-compose ps
```

3. View logs:
```bash
docker-compose logs -f collector
docker-compose logs -f trainer
docker-compose logs -f inference
```

4. Access monitoring dashboard:
```
http://localhost:8080
```

5. Access inference API:
```
http://localhost:8000
```

### Local Development

1. Set up PostgreSQL database:
```bash
createdb subfluxgpt
psql subfluxgpt < database/schema.sql
```

2. Run data collection:
```bash
python -m data_collector.main
```

3. Prepare training data:
```bash
python training_pipeline/prepare_bugbounty.py --vocab_size 4096
```

4. Train models:
```bash
python training_pipeline/scheduler.py
```

5. Start inference server:
```bash
python -m inference.model_server
```

6. Start monitoring dashboard:
```bash
python -m monitoring.dashboard
```

## Configuration

Edit `config.yaml` to customize:

- **Database settings**: PostgreSQL connection
- **Platform configurations**: API keys and platform-specific settings
- **Data collection**: Intervals, rate limits, storage limits
- **Domain processing**: Validation methods, DNS settings
- **Training**: Model sizes, hyperparameters, triggers
- **Inference**: Server settings, generation parameters
- **Monitoring**: Logging, metrics collection

## Training Models

### llama2.c Training

The system supports training three model sizes:

- **15M parameters**: Fast training (~3 min on GPU)
- **42M parameters**: Better quality (~10-15 min on GPU)
- **110M parameters**: Best quality (~hours on GPU)

Training is triggered automatically when enough new reports accumulate (default: 1000 reports).

### Custom Training

To train manually:

```bash
# Prepare data
python training_pipeline/prepare_bugbounty.py --vocab_size 4096

# Train specific model size
python llama2.c/train.py \
    --batch_size 16 \
    --gradient_accumulation_steps 8 \
    --max_seq_len 256 \
    --vocab_size 4096 \
    --dim 512 \
    --n_layers 8 \
    --n_heads 8 \
    --n_kv_heads 8 \
    --learning_rate 5e-4 \
    --max_iters 100000
```

## Inference API

### Generate Text

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Program: example.com\nReport title: Subdomain takeover",
    "max_new_tokens": 256,
    "temperature": 0.8,
    "model": "llama2c_42M"
  }'
```

### Analyze Domain

```bash
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "llama2c_42M"
  }'
```

## Systemd Services

For 24/7 operation, install the systemd services:

```bash
# Copy service files
sudo cp systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable subfluxgpt-collector
sudo systemctl enable subfluxgpt-trainer
sudo systemctl enable subfluxgpt-inference
sudo systemctl enable subfluxgpt-monitoring

# Start services
sudo systemctl start subfluxgpt-collector
sudo systemctl start subfluxgpt-trainer
sudo systemctl start subfluxgpt-inference
sudo systemctl start subfluxgpt-monitoring
```

## Project Structure

```
SubFluxGPT/
├── data_collector/          # Data collection module
│   ├── collectors/          # Platform-specific collectors
│   ├── config/              # Platform configurations
│   ├── storage/             # Raw data storage
│   ├── main.py              # Collection coordinator
│   └── database_manager.py  # Database operations
├── domain_processor/        # Domain extraction and validation
│   └── domain_extractor.py
├── training_pipeline/       # Model training
│   ├── prepare_bugbounty.py # Data preparation
│   ├── bugbounty.py         # Dataset loader
│   └── scheduler.py         # Training scheduler
├── inference/               # Model inference
│   └── model_server.py      # FastAPI server
├── monitoring/              # System monitoring
│   └── dashboard.py         # Web dashboard
├── database/                # Database schema
│   └── schema.sql
├── config.yaml              # Main configuration
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## License

MIT License

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## Disclaimer

This tool is for educational and authorized security testing purposes only. Always obtain proper authorization before testing any systems.
