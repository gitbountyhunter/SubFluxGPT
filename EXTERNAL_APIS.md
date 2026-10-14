# External APIs Integration

SubFluxGPT supports integrating with external AI API providers for production inference while training your own local models in parallel.

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5 (128K context window)
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku (200K context window)
- **Cohere**: Command models (4K context window)
- **Google**: Gemini (32K context window) - optional
- **More providers**: Can be easily added

## Setup

### 1. Configure API Keys

Run the configuration helper:

```bash
python configure_apis.py --create-env
```

This creates a `.env` file template. Edit it to add your API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Cohere
COHERE_API_KEY=your-key-here
```

### 2. Enable Providers in config.yaml

Edit `config.yaml` to enable the providers you want to use:

```yaml
external_apis:
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY:-}
    model: gpt-4-turbo
    context_window: 128000

  anthropic:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY:-}
    model: claude-3-opus-20240229
    context_window: 200000
```

### 3. Load Environment Variables

```bash
# Linux/Mac
source .env

# Windows PowerShell
Get-Content .env | ForEach-Object { $var = $_.Split('='); [Environment]::SetEnvironmentVariable($var[0], $var[1]) }
```

### 4. Verify Configuration

```bash
python configure_apis.py --list
```

## Usage

### Using External APIs in Your Code

```python
from external_apis import MultiAPIClient

# Initialize with config
config = {
    "openai": {"api_key": "your-key", "model": "gpt-4-turbo"},
    "anthropic": {"api_key": "your-key", "model": "claude-3-opus-20240229"}
}

multi_client = MultiAPIClient(config)

# Generate with a specific provider
response = await multi_client.generate("openai", "Analyze example.com")
print(response.content)

# Generate with all providers in parallel
responses = await multi_client.generate_all("Analyze example.com")
for resp in responses:
    print(f"{resp.provider}: {resp.content}")

# Cleanup
multi_client.close_all()
```

### Via Inference Server

The inference server automatically uses external APIs if configured. Requests can specify which model/provider to use:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze example.com",
    "model": "openai_gpt4"
  }'
```

## Benchmarking

Compare your local models against external APIs:

```bash
python run_benchmark.py --domain example.com --compare
```

This runs:
1. All configured local models (llama2.c, GPT-2, nanoGPT)
2. All configured external APIs (OpenAI, Anthropic, etc.)
3. Compares latency, context windows, and response quality

Results are saved to `benchmarking/results/latest.json`.

## Benefits

1. **Production Ready**: Use mature external APIs for production work
2. **Local Training**: Train your own models on your data in parallel
3. **Benchmarking**: Continuously compare local vs external performance
4. **Cost Optimization**: Use cheaper models when appropriate
5. **Privacy**: Keep sensitive data local with your own models
6. **Redundancy**: Multiple providers for reliability

## Adding New Providers

To add a new provider:

1. Create a client class in `external_apis/api_client.py`:

```python
class NewProviderClient(BaseAPIClient):
    def __init__(self, api_key: str, model: str = "default"):
        super().__init__(api_key, model)
        self.base_url = "https://api.newprovider.com"

    async def generate(self, prompt: str, max_tokens: int = 1000, **kwargs) -> APIResponse:
        # Implement API call
        pass
```

2. Add to `APIClientFactory`:

```python
clients = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
    "cohere": CohereClient,
    "newprovider": NewProviderClient,  # Add here
}
```

3. Add configuration to `config.yaml`:

```yaml
external_apis:
  newprovider:
    enabled: false
    api_key: ${NEWPROVIDER_API_KEY:-}
    model: default
    context_window: 32000
```

## Troubleshooting

### API Key Not Found

Make sure:
- API key is in `.env` file
- `.env` is loaded (`source .env`)
- Provider is enabled in `config.yaml`
- Provider key name matches (e.g., `OPENAI_API_KEY`)

### Import Errors

Ensure you're running from the project root:

```bash
cd /path/to/SubFluxGPT
python your_script.py
```

### Rate Limiting

If you hit rate limits:
- Add multiple API keys for the same provider
- Implement request queuing
- Use the benchmark system to track usage

## Security Notes

- Never commit `.env` files to version control
- Use environment variables for production
- Rotate API keys regularly
- Monitor usage for anomalies
- Implement rate limiting in your application
