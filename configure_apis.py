"""
API configuration helper for SubFluxGPT.
Helps set up multiple external API keys for production inference.
"""

import os
import yaml
from pathlib import Path


def create_env_template():
    """Create a .env file template for API keys."""
    env_template = """# SubFluxGPT API Keys Configuration
# Copy this file to .env and fill in your API keys

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Cohere
COHERE_API_KEY=your_cohere_api_key_here

# Google (optional)
GOOGLE_API_KEY=your_google_api_key_here

# Additional providers can be added here
# AZURE_OPENAI_API_KEY=your_azure_key
# HUGGINGFACE_API_KEY=your_huggingface_key
# TOGETHER_API_KEY=your_together_key
# PERPLEXITY_API_KEY=your_perplexity_key
"""

    env_path = Path('.env')
    if env_path.exists():
        print(f".env file already exists at {env_path}")
        overwrite = input("Overwrite? (y/N): ")
        if overwrite.lower() != 'y':
            print("Keeping existing .env file")
            return

    with open(env_path, 'w') as f:
        f.write(env_template)

    print(f"Created .env template at {env_path}")
    print("Edit this file to add your API keys")


def update_config_with_apis(config_path='config.yaml'):
    """Update config.yaml to enable specific API providers."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get list of available providers
    external_apis = config.get('external_apis', {})

    print("\nAvailable API providers:")
    for provider in external_apis.keys():
        status = "enabled" if external_apis[provider].get('enabled', False) else "disabled"
        print(f"  - {provider}: {status}")

    print("\nTo enable a provider:")
    print("1. Add the API key to your .env file")
    print("2. Set 'enabled: true' in config.yaml for that provider")
    print("3. Restart the inference server")

    print("\nExample: To enable OpenAI:")
    print("  1. Add OPENAI_API_KEY=sk-... to .env")
    print("  2. In config.yaml, set openai.enabled: true")


def list_apis_from_env():
    """List API keys that are currently set in environment."""
    api_keys = {
        'OPENAI_API_KEY': 'OpenAI',
        'ANTHROPIC_API_KEY': 'Anthropic',
        'COHERE_API_KEY': 'Cohere',
        'GOOGLE_API_KEY': 'Google',
    }

    print("\nAPI Keys found in environment:")
    found_any = False
    for env_var, provider in api_keys.items():
        value = os.environ.get(env_var)
        if value:
            found_any = True
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {provider}: {masked}")
        else:
            print(f"  ✗ {provider}: not set")

    if not found_any:
        print("  No API keys found in environment")
        print("  Add them to .env file and run: source .env (or set in your shell)")


def main():
    """Main entry point."""
    print("SubFluxGPT API Configuration Helper")
    print("=" * 50)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-env', action='store_true', help='Create .env template')
    parser.add_argument('--list', action='store_true', help='List configured API keys')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config.yaml')
    args = parser.parse_args()

    if args.create_env:
        create_env_template()

    if args.list:
        list_apis_from_env()

    if not args.create_env and not args.list:
        # Show help by default
        print("\nUsage:")
        print("  python configure_apis.py --create-env   # Create .env template")
        print("  python configure_apis.py --list         # List configured API keys")
        print("\nOr run with no flags to see current config status")
        update_config_with_apis(args.config)


if __name__ == '__main__':
    main()
