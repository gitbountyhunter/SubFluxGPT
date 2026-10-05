<<<<<<< HEAD
# SubFluxGPT
Next-gen AI-powered subdomain enumeration for bug bounty hunters. Multi-API support (Gemini, Claude, OpenAI), Netlas integration, BBRF workflow, and httpx probing. Modern SubGPT alternative with free-tier optimization.
=======
# SubFluxGPT 🚀

> Next-generation AI-powered subdomain enumeration for bug bounty hunters and security researchers

SubFluxGPT analyzes your existing subdomains and uses multiple AI APIs (Gemini, Claude, OpenAI, Grok, DeepSeek) to predict new subdomains that traditional tools might miss. With integrated Netlas reconnaissance, BBRF support, and seamless CLI pipeline integration, it's designed for modern bug bounty workflows.

## ✨ Features

- **Multi-API AI Support**: Gemini (primary), Claude (fallback), OpenAI, Grok, DeepSeek
- **Netlas Integration**: Unlimited developer queries for attack surface discovery
- **BBRF Pipeline**: Direct integration with bug bounty reconnaissance frameworks
- **Smart DNS Resolution**: Wildcard detection and validation
- **HTTP Probing**: Built-in httpx integration for live subdomain checking
- **Token-Efficient**: Optimized prompts to maximize API usage
- **Stdout Pipeline**: Designed for CLI workflows and tool chaining
- **Free Tier Friendly**: Optimized for Gemini's generous free tier

## 🎯 Use Cases

```bash
# Basic subdomain generation with Gemini
subfluxgpt -i subs.txt -o new_subs.txt --api gemini

# Pipe directly to BBRF
subfluxgpt -i subs.txt --api gemini | bbrf domain add -

# Generate + resolve + probe with httpx
subfluxgpt -i subs.txt --api gemini --resolve --probe | httpx -status-code

# Use Netlas for attack surface enrichment
subfluxgpt -i subs.txt --api gemini --netlas-enrich

# Fallback to Claude if Gemini fails
subfluxgpt -i subs.txt --api gemini --fallback claude
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SubFluxGPT.git
cd SubFluxGPT

# Install with pip
pip install -r requirements.txt
pip install -e .
```

## 🔑 Configuration

Create a `.env` file or set environment variables:

```bash
# Primary AI API (recommended: Gemini for free tier)
GEMINI_API_KEY=your_gemini_key
CLAUDE_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
GROK_API_KEY=your_grok_key
DEEPSEEK_API_KEY=your_deepseek_key

# Netlas API (free for developers)
NETLAS_API_KEY=your_netlas_key

# BBRF (optional)
BBRF_SERVER=http://localhost:8080
BBRF_USERNAME=your_username
BBRF_PASSWORD=your_password
```

## 🚀 Usage

### Basic Subdomain Generation

```bash
subfluxgpt -i known_subs.txt -o predicted_subs.txt --api gemini
```

### With DNS Resolution

```bash
subfluxgpt -i known_subs.txt -o resolved_subs.txt --api gemini --resolve
```

### HTTP Probing Integration

```bash
subfluxgpt -i known_subs.txt --api gemini --resolve --probe | httpx -status-code -title
```

### Netlas Attack Surface Enrichment

```bash
subfluxgpt -i known_subs.txt --api gemini --netlas-enrich -o enriched.json
```

### BBRF Integration

```bash
# Direct pipe to BBRF
subfluxgpt -i known_subs.txt --api gemini | bbrf domain add -

# With program scoping
subfluxgpt -i known_subs.txt --api gemini --bbrf-program target_program
```

### Multi-API Fallback

```bash
# Try Gemini, fallback to Claude
subfluxgpt -i known_subs.txt --api gemini --fallback claude

# Custom chain
subfluxgpt -i known_subs.txt --api gemini --fallback claude,openai
```

## 🏗️ Architecture

```
SubFluxGPT/
├── src/
│   └── subfluxgpt/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── ai_router.py        # Multi-API LLM router
│       ├── netlas_client.py    # Netlas API integration
│       ├── bbrf_client.py      # BBRF integration
│       ├── dns_resolver.py     # DNS resolution & wildcard detection
│       ├── http_prober.py      # httpx integration
│       └── utils.py            # Utilities
├── tests/
├── docs/
└── requirements.txt
```

## 🔧 Module Details

### AI Router (`ai_router.py`)
- Supports multiple LLM APIs with unified interface
- Automatic fallback on API failures
- Token-efficient prompt engineering
- Context window optimization

### Netlas Client (`netlas_client.py`)
- Advanced dork queries
- Certificate extraction
- Service banner analysis
- Data normalization for token efficiency

### BBRF Client (`bbrf_client.py`)
- Direct domain injection
- Program-based scoping
- Out-of-scope filtering
- JSON data storage

### DNS Resolver (`dns_resolver.py`)
- A/CNAME record resolution
- Wildcard detection
- Custom resolver support
- Rate limiting

### HTTP Prober (`http_prober.py`)
- httpx integration
- Status code detection
- Title extraction
- Technology fingerprinting

## 📊 Comparison with SubGPT

| Feature | SubGPT | SubFluxGPT |
|---------|--------|------------|
| AI APIs | Bing (cookie-based) | Gemini, Claude, OpenAI, Grok, DeepSeek |
| Netlas | ❌ | ✅ (unlimited dev access) |
| BBRF | ❌ | ✅ native pipeline |
| httpx | ❌ | ✅ integrated |
| API Keys | Cookie extraction | Secure env vars |
| Token Optimization | Basic | Advanced |
| Wildcard Detection | Basic | Advanced |
| HTTP Probing | ❌ | ✅ |
| Stdout Pipeline | Basic | Advanced |

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Inspired by [SubGPT](https://github.com/s0md3v/SubGPT) by s0md3v
- [Netlas.io](https://netlas.io) for their amazing API and developer program
- [BBRF](https://github.com/honze-net/bbrf) for bug bounty reconnaissance
- [ProjectDiscovery](https://projectdiscovery.io) for httpx and other tools

## ⭐ Star History

If you find this tool useful, please consider giving it a star on GitHub!

## 📞 Support

- Open an issue for bug reports
- Join our Discord community
- Check the documentation in `/docs`

---

**Built for the bug bounty community, by the bug bounty community 🎯**
>>>>>>> 614f35a (Initial commit: SubFluxGPT v1.0.0)
