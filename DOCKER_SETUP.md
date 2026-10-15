# Docker Setup Guide for SubFluxGPT

Complete guide to running SubFluxGPT with Docker for easy deployment and isolation.

## Prerequisites

- Docker installed (version 20.10 or higher)
- Docker Compose installed (version 2.0 or higher)
- For GPU support: NVIDIA Docker runtime (nvidia-docker2)

## Quick Start

### 1. Clone and Navigate

```bash
cd /path/to/SubFluxGPT
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Build and Start Services

```bash
# Start all core services
docker-compose up -d

# Or start specific profiles
docker-compose --profile cpu up -d           # CPU-only training
docker-compose --profile gpu up -d           # GPU-enabled training
docker-compose --profile monitoring up -d    # Bug bounty monitoring
docker-compose --profile ai up -d            # Self-improving AI
docker-compose --profile recon up -d         # Cloud recon worker
```

### 4. Verify Services

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test inference server
curl http://localhost:8000/health
```

## Services Overview

### Core Services (Always Running)

- **postgres**: PostgreSQL database for data storage
- **redis**: Redis for caching and task queues
- **inference**: FastAPI inference server (port 8000)
- **monitoring**: Monitoring dashboard (port 8080)

### Optional Services (Profile-based)

- **collector**: Data collector from bug bounty platforms
- **trainer-cpu**: CPU-only model training
- **trainer**: GPU-accelerated model training (requires NVIDIA runtime)
- **bugbounty-monitor**: Bug bounty platform monitoring
- **self-improving**: Self-improving LLM system
- **cloud-recon**: Cloud reconnaissance worker

## Docker Profiles

### CPU Profile (No GPU)

```bash
docker-compose --profile cpu up -d
```

Starts: postgres, redis, collector, trainer-cpu, inference, monitoring

### GPU Profile (NVIDIA GPU)

```bash
docker-compose --profile gpu up -d
```

Starts: postgres, redis, collector, trainer, inference, monitoring

**Requirements:**
- NVIDIA GPU
- nvidia-docker2 installed
- NVIDIA Container Toolkit configured

### Monitoring Profile

```bash
docker-compose --profile monitoring up -d
```

Starts: postgres, redis, collector, inference, monitoring, bugbounty-monitor

### AI Profile

```bash
docker-compose --profile ai up -d
```

Starts: postgres, redis, collector, inference, monitoring, self-improving

### Recon Profile

```bash
docker-compose --profile recon up -d
```

Starts: postgres, redis, collector, inference, monitoring, cloud-recon

### Full Stack (All Services)

```bash
docker-compose --profile cpu --profile monitoring --profile ai --profile recon up -d
```

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# Database
DB_PASSWORD=your_secure_password
DATABASE_URL=postgresql://subflux:your_secure_password@postgres:5432/subfluxgpt

# Redis
REDIS_URL=redis://redis:6379/0

# API Keys (Optional)
HACKERONE_API_KEY=your_hackerone_api_key
BUGCROWD_API_TOKEN=your_bugcrowd_token
OPENAI_API_KEY=your_openai_key (if using external APIs)

# BBRF (Optional)
BBRF_API_ENDPOINT=http://localhost:5000
BBRF_API_KEY=your_bbrf_key
BBRF_WORKSPACE=subfluxgpt

# Threat Intelligence (Optional)
VIRUSTOTAL_API_KEY=your_vt_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
SHODAN_API_KEY=your_shodan_key
```

### Volume Mounts

Docker Compose mounts the following directories:

- `./data_collector:/app/data_collector` - Data collector scripts
- `./training_pipeline:/app/training_pipeline` - Training scripts
- `./models:/app/models` - Trained models
- `./logs:/app/logs` - Application logs
- `./data:/app/data` - Learning and training data
- `./targets:/app/targets` - Organized target folders
- `./cloud_recon_data:/app/cloud_recon_data` - Cloud recon results

## Usage Examples

### Run Cloud Recon

```bash
# Enter the inference container
docker-compose exec inference bash

# Run cloud recon
python3 run_cloud_recon.py --download --process --apex example.com
```

### Start Bug Bounty Monitoring

```bash
# Start monitoring profile
docker-compose --profile monitoring up -d

# Check monitoring status
docker-compose exec bugbounty-monitor python bug_bounty_monitor.py --status
```

### Train Models

```bash
# CPU training
docker-compose --profile cpu up -d
docker-compose logs -f trainer-cpu

# GPU training
docker-compose --profile gpu up -d
docker-compose logs -f trainer
```

### Use Inference Server

```bash
# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze the domain: example.com", "model": "gpt2_124M"}'

# Analyze domain
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "model": "gpt2_124M"}'
```

### Access Monitoring Dashboard

```bash
# Open in browser
open http://localhost:8080
```

## GPU Support Setup

### Install NVIDIA Container Toolkit

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker
```

### Configure Docker to Use NVIDIA Runtime

Edit `/etc/docker/daemon.json`:

```json
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

### Verify GPU Access

```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs <service_name>

# Check resource usage
docker stats

# Rebuild containers
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Check postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check database logs
docker-compose logs postgres
```

### GPU Not Detected

```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Check docker-compose GPU configuration
docker-compose config | grep -A 10 deploy
```

### Out of Disk Space

```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Check disk usage
docker system df
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./data ./models ./logs

# Or run with current user ID
docker-compose up -d --user $(id -u):$(id -g)
```

## Advanced Configuration

### Custom Dockerfile

For custom builds, modify `Dockerfile`:

```dockerfile
# Use different Python version
FROM python:3.11-slim

# Add system dependencies
RUN apt-get update && apt-get install -y \
    cuda-toolkit-11-x \
    && rm -rf /var/lib/apt/lists/*

# Install specific PyTorch version
RUN pip install torch==2.0.0 torchvision==0.15.0
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  trainer:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
        reservations:
          cpus: '2'
          memory: 8G
```

### Custom Networks

```yaml
networks:
  subfluxgpt_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Production Deployment

### Use Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml subfluxgpt

# Scale services
docker service scale subfluxgpt_inference=3
```

### Use Kubernetes

Convert to Kubernetes manifests:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert
kompose convert -f docker-compose.yml -o k8s/

# Deploy
kubectl apply -f k8s/
```

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use strong passwords** - Generate secure DB passwords
3. **Limit container privileges** - Run as non-root user when possible
4. **Scan images for vulnerabilities** - Use `docker scan`
5. **Keep images updated** - Regularly rebuild with latest base images
6. **Use secrets management** - For production, use Docker Secrets or external vault
7. **Network isolation** - Use custom networks to isolate services
8. **Resource limits** - Set CPU and memory limits to prevent DoS

## Performance Optimization

### Build Cache

```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build
```

### Multi-stage Builds

The Dockerfile already uses multi-stage builds for smaller images.

### Volume Caching

```yaml
volumes:
  - cache:/tmp/cache
```

## Backup and Restore

### Backup Database

```bash
docker-compose exec postgres pg_dump -U subflux subfluxgpt > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U subflux subfluxgpt
```

### Backup Models

```bash
docker run --rm -v $(pwd)/models:/data -v $(pwd)/backup:/backup alpine tar czf /backup/models.tar.gz /data
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f inference

# Last 100 lines
docker-compose logs --tail=100
```

### Health Checks

```bash
# Check health status
docker-compose ps

# Manual health check
curl http://localhost:8000/health
```

### Metrics

Access Prometheus metrics at `http://localhost:8000/metrics` (if configured)

## Uninstall

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Support

For issues specific to Docker setup:

1. Check Docker logs: `docker-compose logs`
2. Verify Docker version: `docker --version`
3. Check Docker Compose version: `docker-compose --version`
4. Review this guide and troubleshooting section

For general SubFluxGPT issues, see the main documentation.

---

*Last Updated: 2026-10-14*
*Docker Version: 20.10+*
*Docker Compose Version: 2.0+*
