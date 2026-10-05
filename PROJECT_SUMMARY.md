# SubFluxGPT - Project Summary

## Overview

SubFluxGPT is a next-generation AI-powered subdomain enumeration tool designed for bug bounty hunters and security researchers. It improves upon the original SubGPT by:

- Using modern API keys instead of browser cookies
- Supporting multiple AI APIs (Gemini, Claude, OpenAI, Grok, DeepSeek)
- Integrating with Netlas for attack surface reconnaissance
- Providing native BBRF integration for bug bounty workflows
- Including built-in HTTP probing with httpx
- Optimizing for token efficiency and free-tier usage

## Key Features

### 1. Multi-API AI Support
- **Primary**: Google Gemini (generous free tier, large context window)
- **Fallbacks**: Claude, OpenAI, Grok, DeepSeek
- Automatic fallback on API failures
- Token-efficient prompt engineering

### 2. Netlas Integration
- Unlimited developer queries (via Netlas developer program)
- Advanced dork queries
- Certificate extraction
- Service banner analysis
- Data normalization for token efficiency

### 3. BBRF Integration
- Direct domain injection
- Program-based scoping
- Out-of-scope filtering
- Seamless CLI pipeline integration

### 4. DNS Resolution
- A/CNAME record resolution
- Wildcard detection
- Custom resolver support
- Concurrent resolution

### 5. HTTP Probing
- httpx integration
- Status code detection
- Title extraction
- Technology fingerprinting
- Both HTTP and HTTPS support

### 6. CLI Pipeline Design
- Native stdout support
- Pipe to httpx, nuclei, naabu, etc.
- Multiple output formats (text, json, csv)
- Progress reporting

## Project Structure

```
SubFluxGPT/
├── src/subfluxgpt/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # CLI interface (339 lines)
│   ├── ai_router.py         # Multi-API LLM router (266 lines)
│   ├── netlas_client.py     # Netlas API integration (285 lines)
│   ├── bbrf_client.py       # BBRF integration (288 lines)
│   ├── dns_resolver.py      # DNS resolution (254 lines)
│   ├── http_prober.py       # HTTP probing (278 lines)
│   └── utils.py             # Utilities (286 lines)
├── .github/
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── docs/                    # (reserved for future docs)
├── tests/                   # (reserved for future tests)
├── .env.example             # Configuration template
├── .gitignore               # Git ignore rules
├── CONTRIBUTING.md          # Contribution guidelines
├── Dockerfile               # Docker container
├── docker-compose.yml       # Docker Compose configuration
├── EXAMPLES.md              # Usage examples
├── LICENSE                  # MIT License
├── PROJECT_SUMMARY.md       # This file
├── pyproject.toml           # Modern Python project config
├── quickstart.sh            # Quick start script
├── README.md                # Main documentation
├── requirements.txt         # Python dependencies
├── sample_input.txt         # Sample input file
├── SECURITY.md              # Security policy
└── setup.py                 # Setup script
```

## Installation

### Quick Start
```bash
git clone https://github.com/yourusername/SubFluxGPT.git
cd SubFluxGPT
./quickstart.sh
```

### Manual Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Docker
```bash
docker-compose up -d
docker-compose exec subfluxgpt subfluxgpt --help
```

## Configuration

Create a `.env` file from `.env.example` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

Minimum required:
- `GEMINI_API_KEY` (recommended for free tier)

Optional:
- `CLAUDE_API_KEY`
- `OPENAI_API_KEY`
- `GROK_API_KEY`
- `DEEPSEEK_API_KEY`
- `NETLAS_API_KEY`
- `BBRF_SERVER`, `BBRF_USERNAME`, `BBRF_PASSWORD`

## Usage Examples

### Basic Generation
```bash
subfluxgpt -i known_subs.txt -o new_subs.txt --api gemini
```

### With DNS Resolution
```bash
subfluxgpt -i known_subs.txt -o resolved.txt --api gemini --resolve
```

### Pipe to httpx
```bash
subfluxgpt -i known_subs.txt --api gemini --resolve --probe | httpx -status-code
```

### BBRF Integration
```bash
subfluxgpt -i known_subs.txt --api gemini | bbrf domain add -
```

### Netlas Enrichment
```bash
subfluxgpt -i known_subs.txt --api gemini --netlas-enrich
```

### Multi-API Fallback
```bash
subfluxgpt -i known_subs.txt --api gemini --fallback claude,openai
```

## Comparison with SubGPT

| Feature | SubGPT | SubFluxGPT |
|---------|--------|------------|
| AI APIs | Bing (cookie) | Gemini, Claude, OpenAI, Grok, DeepSeek |
| Authentication | Browser cookies | API keys (secure) |
| Netlas | ❌ | ✅ (unlimited dev access) |
| BBRF | ❌ | ✅ native pipeline |
| httpx | ❌ | ✅ integrated |
| DNS Resolution | Basic | Advanced (wildcard detection) |
| HTTP Probing | ❌ | ✅ |
| Stdout Pipeline | Basic | Advanced |
| Token Optimization | Basic | Advanced |
| Docker Support | ❌ | ✅ |
| Documentation | Basic | Comprehensive |

## API Integration Details

### Supported APIs

1. **Google Gemini** (Primary)
   - Model: gemini-1.5-pro
   - Free tier: Generous daily tokens
   - Large context window
   - Recommended for most users

2. **Anthropic Claude** (Fallback)
   - Model: claude-3-5-sonnet-20241022
   - High-quality responses
   - Good for complex analysis

3. **OpenAI GPT** (Fallback)
   - Model: gpt-4o-mini
   - Widely supported
   - Good token efficiency

4. **xAI Grok** (Fallback)
   - Model: grok-beta
   - Real-time knowledge
   - Good for current events

5. **DeepSeek** (Fallback)
   - Model: deepseek-chat
   - Cost-effective
   - Good performance

### Netlas Integration

- Sign up at https://netlas.io
- Apply for developer program for unlimited queries
- Use `--netlas-enrich` for attack surface data
- Custom dork queries supported

### BBRF Integration

- Native CLI pipeline support
- Program-based scoping
- Out-of-scope filtering
- Direct domain injection

## Development Roadmap

### Phase 1: Core Features (Completed ✅)
- [x] Multi-API AI support
- [x] Netlas integration
- [x] BBRF integration
- [x] DNS resolution
- [x] HTTP probing
- [x] CLI interface
- [x] Documentation

### Phase 2: Enhancements (Future)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Caching layer
- [ ] Progress bars
- [ ] Output formatting improvements

### Phase 3: Advanced Features (Future)
- [ ] Machine learning model for subdomain prediction
- [ ] Historical subdomain tracking
- [ ] Custom prompt templates
- [ ] Web UI
- [ ] API server mode
- [ ] Plugin system

## Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines.

Key areas for contribution:
- Additional AI API integrations
- Performance optimizations
- Bug fixes
- Documentation improvements
- Test coverage

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Inspired by [SubGPT](https://github.com/s0md3v/SubGPT) by s0md3v
- [Netlas.io](https://netlas.io) for their amazing API
- [BBRF](https://github.com/honze-net/bbrf) for bug bounty reconnaissance
- [ProjectDiscovery](https://projectdiscovery.io) for httpx and other tools

## Getting Help

- Open an issue on GitHub
- Check EXAMPLES.md for usage examples
- Read the main README.md
- Join our community (Discord link coming soon)

## Security

See SECURITY.md for security policies and best practices.

## Stars and Forks Goal

This tool is designed to be:
- **Free to use** (Gemini free tier)
- **Open source** (MIT License)
- **Community-driven** (bug bounty focused)
- **Professional** (clean code, good documentation)
- **Integration-friendly** (CLI pipeline design)

With these features, we aim to make SubFluxGPT a rising star in the bug bounty community!

---

**Built for the bug bounty community, by the bug bounty community 🎯**
