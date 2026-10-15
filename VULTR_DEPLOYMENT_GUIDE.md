# SubFluxGPT Vultr VPS Deployment Guide

Complete guide to deploying SubFluxGPT to a Vultr VPS with Docker.

---

## 🚀 Quick Deployment (Docker - Recommended)

### Prerequisites

- Vultr VPS with at least:
  - 2GB RAM (4GB+ recommended)
  - 2 CPU cores
  - 40GB SSD storage
- SSH access to VPS
- Docker installed on VPS

### Step 1: Connect to VPS

```bash
ssh root@your-vps-ip
```

### Step 2: Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add user to docker group (if not root)
usermod -aG docker $USER
```

### Step 3: Clone Repository

```bash
# Install git
apt install git -y

# Clone repository
git clone https://github.com/gitbountyhunter/SubFluxGPT.git
cd SubFluxGPT
```

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Add your API keys:
```bash
# OpenRouter
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Mistral
MISTRAL_API_KEY=your-mistral-api-key-here

# Grok
GROK_API_KEY=your-grok-api-key-here

# Gemini
GEMINI_API_KEY=your-gemini-api-key-here

# Database
DB_PASSWORD=your_secure_password_here
```

### Step 5: Start Services

```bash
# Start core services
docker-compose up -d

# Or start with specific profiles
docker-compose --profile cpu --profile monitoring up -d
```

### Step 6: Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test inference server
curl http://localhost:8000/health
```

### Step 7: Access from Local Machine

```bash
# SSH tunnel to access services locally
ssh -L 8000:localhost:8000 root@your-vps-ip
ssh -L 8080:localhost:8080 root@your-vps-ip

# Now access in browser:
# http://localhost:8000 - Inference server
# http://localhost:8080 - Monitoring dashboard
```

---

## 🔧 Manual Deployment (Without Docker)

### Step 1: Update System

```bash
ssh root@your-vps-ip
apt update && apt upgrade -y
```

### Step 2: Install Python and Dependencies

```bash
# Install Python 3.10+
apt install python3 python3-pip python3-venv git -y

# Install system dependencies
apt install build-essential libssl-dev libffi-dev python3-dev -y
```

### Step 3: Clone Repository

```bash
git clone https://github.com/gitbountyhunter/SubFluxGPT.git
cd SubFluxGPT
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment

```bash
cp .env.example .env
nano .env
# Add your API keys
```

### Step 7: Create Directories

```bash
mkdir -p data/learning data/self_improving data/monitor
mkdir -p data_collector/storage/raw database models logs
mkdir -p cloud_recon_data benchmarking/results targets
```

### Step 8: Make Script Executable

```bash
chmod +x subfluxgpt
```

### Step 9: Test Installation

```bash
./subfluxgpt
./subfluxgpt ai-stats
```

### Step 10: Run as Service (Optional)

Create systemd service:

```bash
nano /etc/systemd/system/subfluxgpt.service
```

Add:
```ini
[Unit]
Description=SubFluxGPT AI System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/SubFluxGPT
Environment="PATH=/root/SubFluxGPT/venv/bin"
ExecStart=/root/SubFluxGPT/venv/bin/python /root/SubFluxGPT/bug_bounty_monitor.py --interval 3600
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable subfluxgpt
systemctl start subfluxgpt
systemctl status subfluxgpt
```

---

## 🔐 Security Hardening

### 1. Configure Firewall

```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow web services
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 8080/tcp

# Enable firewall
ufw enable
```

### 2. Create Non-Root User (Recommended)

```bash
# Create user
adduser subfluxgpt
usermod -aG docker subfluxgpt

# Switch to user
su - subfluxgpt
cd /home/subfluxgpt
git clone https://github.com/gitbountyhunter/SubFluxGPT.git
cd SubFluxGpt
```

### 3. Use SSH Keys Only

```bash
# On local machine, generate SSH key
ssh-keygen -t rsa -b 4096

# Copy to VPS
ssh-copy-id root@your-vps-ip

# Disable password authentication
nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Set: PubkeyAuthentication yes

# Restart SSH
systemctl restart sshd
```

### 4. Install Fail2Ban

```bash
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📊 Monitoring

### Install Monitoring Tools

```bash
# Install htop
apt install htop -y

# Install nload for network monitoring
apt install nload -y

# Install iotop for I/O monitoring
apt install iotop -y
```

### Monitor Docker Resources

```bash
# Check container stats
docker stats

# Check disk usage
docker system df

# Check logs
docker-compose logs -f --tail=100
```

---

## 🔄 Automatic Updates

### Setup Auto-Update Script

```bash
nano /root/update_subfluxgpt.sh
```

Add:
```bash
#!/bin/bash
cd /root/SubFluxGPT
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

Make executable:
```bash
chmod +x /root/update_subfluxgpt.sh
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /root/update_subfluxgpt.sh
```

---

## 🌐 Domain and SSL

### Setup Domain

1. Point domain to VPS IP
2. Install Nginx reverse proxy:

```bash
apt install nginx -y
```

Configure Nginx:
```bash
nano /etc/nginx/sites-available/subfluxgpt
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /monitoring {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/subfluxgpt /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Setup SSL with Certbot

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## 📈 Performance Optimization

### 1. Optimize Docker

Edit `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
```

Restart Docker:
```bash
systemctl restart docker
```

### 2. Enable Swap

```bash
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 3. Optimize System Limits

Edit `/etc/sysctl.conf`:
```bash
vm.max_map_count=262144
fs.file-max=1000000
net.core.somaxconn=1024
```

Apply:
```bash
sysctl -p
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check resource usage
htop

# Restart services
docker-compose restart
```

### Out of Memory

```bash
# Add swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Reduce Docker memory
nano docker-compose.yml
# Add: mem_limit: 2g
```

### Permission Issues

```bash
# Fix permissions
chown -R $USER:$USER /root/SubFluxGPT
chmod -R 755 /root/SubFluxGPT
```

### Can't Connect

```bash
# Check firewall
ufw status

# Check if services are running
docker-compose ps

# Check port listening
netstat -tlnp | grep 8000
```

---

## 📋 Post-Deployment Checklist

- [ ] Docker installed and running
- [ ] Repository cloned
- [ ] .env configured with API keys
- [ ] Services started successfully
- [ ] Firewall configured
- [ ] SSH keys configured
- [ ] Domain pointed (if applicable)
- [ ] SSL certificate installed (if applicable)
- [ ] Monitoring tools installed
- [ ] Backup strategy in place
- [ ] Auto-update configured
- [ ] Tested all major workflows

---

## 🎯 Quick Reference

### View Logs
```bash
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Update Code
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Check Stats
```bash
docker stats
```

---

## 🚀 Ready to Deploy!

Provide your VPS details and I can help you execute these commands or provide a deployment script.

---

*Last Updated: 2026-10-14*
*VPS Provider: Vultr*
