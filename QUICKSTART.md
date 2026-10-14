# SubFluxGPT Quick Start Guide

This guide will help you get SubFluxGPT up and running quickly.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose (recommended)
- PostgreSQL 15+ (if not using Docker)
- Redis (if not using Docker)
- CUDA-capable GPU (for training)

## Option 1: Docker Deployment (Recommended)

### Step 1: Clone and Setup

```bash
cd /Users/beanman/Documents/Desktop/SubFluxGPT
```

### Step 2: Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit the following values:
- `DB_PASSWORD`: Set a secure password for PostgreSQL
- `HACKERONE_API_KEY`: If using HackerOne API (optional, dataset works without it)
- Other API keys as needed

### Step 3: Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Data collector service
- Training scheduler
- Inference server
- Monitoring dashboard

### Step 4: Verify Services

```bash
docker-compose ps
```

All services should show "Up" status.

### Step 5: Access Interfaces

- **Monitoring Dashboard**: http://localhost:8080
- **Inference API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 6: Monitor Data Collection

```bash
docker-compose logs -f collector
```

You should see logs showing data collection from HackerOne (using the HuggingFace dataset).

### Step 7: Monitor Training

```bash
docker-compose logs -f trainer
```

Training will start automatically when enough reports are collected (default: 1000 reports).

## Option 2: Local Development

### Step 1: Set Up Python Environment

```bash
cd /Users/beanman/Documents/Desktop/SubFluxGPT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Set Up Database

```bash
# Install PostgreSQL if not already installed
brew install postgresql  # macOS
# or use your package manager

# Start PostgreSQL
brew services start postgresql

# Create database
createdb subfluxgpt

# Load schema
psql subfluxgpt < database/schema.sql
```

### Step 3: Configure

```bash
cp .env.example .env
nano .env
```

Set `DATABASE_URL` to:
```
DATABASE_URL=postgresql://$(whoami):your_password@localhost:5432/subfluxgpt
```

### Step 4: Run Data Collection

```bash
python -m data_collector.main
```

This will:
1. Connect to HackerOne HuggingFace dataset
2. Extract relevant reports (subdomain/DNS/takeover related)
3. Store in PostgreSQL database
4. Extract domains from reports
5. Store domains in database

### Step 5: Prepare Training Data

```bash
# First, you may want to train a custom tokenizer (optional)
# python llama2.c/tinystories.py train_vocab --vocab_size=4096

# Prepare bug bounty data for training
python training_pipeline/prepare_bugbounty.py --vocab_size 4096
```

This creates:
- `data/bugbounty_tokens/train.bin`
- `data/bugbounty_tokens/val.bin`

### Step 6: Train Models

```bash
# Run the training scheduler
python training_pipeline/scheduler.py
```

This will:
1. Check if enough new reports exist
2. If yes, prepare data
3. Train llama2.c models (15M, 42M, 110M)
4. Save checkpoints to `models/checkpoints/`

### Step 7: Start Inference Server

```bash
python -m inference.model_server
```

Access at http://localhost:8000

### Step 8: Start Monitoring Dashboard

```bash
python -m monitoring.dashboard
```

Access at http://localhost:8080

## Testing the System

### Test Data Collection

```bash
python -m data_collector.main
```

Check the logs to see reports being collected.

### Test Database

```bash
python -c "
from data_collector.database_manager import DatabaseManager
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

db = DatabaseManager(config['database']['url'])
stats = db.get_statistics()
print(f'Total reports: {stats[\"total_reports\"]}')
print(f'Total domains: {stats[\"total_domains\"]}')
"
```

### Test Inference API

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Program: example.com\nReport title: Subdomain takeover",
    "max_new_tokens": 50,
    "temperature": 0.8
  }'
```

## Systemd Services (24/7 Operation)

### Install Services

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

### Check Service Status

```bash
sudo systemctl status subfluxgpt-collector
sudo systemctl status subfluxgpt-trainer
sudo systemctl status subfluxgpt-inference
sudo systemctl status subfluxgpt-monitoring
```

### View Logs

```bash
sudo journalctl -u subfluxgpt-collector -f
sudo journalctl -u subfluxgpt-trainer -f
sudo journalctl -u subfluxgpt-inference -f
sudo journalctl -u subfluxgpt-monitoring -f
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Check PostgreSQL is running:
```bash
brew services list | grep postgresql
```

2. Check database exists:
```bash
psql -l
```

3. Verify DATABASE_URL in `.env`

### Import Errors

If you get import errors:

1. Make sure you're in the virtual environment:
```bash
source venv/bin/activate
```

2. Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Docker Issues

If Docker containers fail to start:

1. Check Docker is running:
```bash
docker ps
```

2. Check logs:
```bash
docker-compose logs
```

3. Rebuild containers:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Training Fails

If training fails:

1. Check CUDA is available:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

2. If no GPU, change device in config.yaml:
```yaml
training:
  llama2c:
    device: cpu
```

3. Check training data exists:
```bash
ls -la data/bugbounty_tokens/
```

## Next Steps

1. **Add more platforms**: Configure Intigriti and Synack in `config.yaml`
2. **Customize training**: Adjust hyperparameters in `config.yaml`
3. **Integrate with Kaspersky**: Set up Kaspersky API in config
4. **Set up monitoring**: Configure alerts and notifications
5. **Scale up**: Deploy to cloud with Kubernetes

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review `config.yaml` for configuration options
- See `README.md` for detailed documentation
