#!/usr/bin/env python3
"""
Main reconnaissance runner script.
Runs security tools on a domain and integrates with BBRF.
"""

import asyncio
import sys
import os
import yaml
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from recon_tools import SecurityToolManager, BBRFClient


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run SubFluxGPT reconnaissance')
    parser.add_argument('--domain', type=str, required=True, help='Domain to recon')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--output', type=str, default='recon_results.json', help='Output file')
    parser.add_argument('--tools', type=str, nargs='+', help='Specific tools to run')
    parser.add_argument('--sync-bbrf', action='store_true', help='Sync results to BBRF')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode with live updates')
    args = parser.parse_args()

    # Setup verbose logging if requested
    if args.verbose:
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        print("Verbose mode enabled")

    # Load configuration
    config = load_config(args.config)

    # Initialize security tool manager
    tool_manager = SecurityToolManager(config)

    # Check available tools
    available = tool_manager.get_available_tools()
    print(f"\nAvailable tools: {', '.join(available)}")

    if not available:
        print("No security tools available. Enable them in config.yaml and ensure they're installed.")
        return

    # Run reconnaissance
    print(f"\n{'='*60}")
    print(f"Running reconnaissance for: {args.domain}")
    print(f"{'='*60}\n")

    results = tool_manager.run_reconnaissance(args.domain)

    # Save results
    import json
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {args.output}")

    # Sync to BBRF if requested
    if args.sync_bbrf:
        print("\nSyncing to BBRF...")
        bbrf_config = config.get('bbrf', {})
        bbrf = BBRFClient(bbrf_config)

        if bbrf.is_available():
            bbrf.create_program(args.domain)

            # Sync domains
            if results['tools'].get('httpx', {}).get('data'):
                for item in results['tools']['httpx']['data']:
                    if 'host' in item:
                        bbrf.add_domain(args.domain, item['host'], source='httpx')

            # Sync URLs
            if results['tools'].get('gau', {}).get('data'):
                for url in results['tools']['gau']['data']:
                    bbrf.add_url(args.domain, url, source='gau')

            print("BBRF sync complete")
        else:
            print("BBRF not available")

    # Print summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    for tool, result in results['tools'].items():
        status = "✓" if result.get('success') else "✗"
        data_count = len(result.get('data', [])) if result.get('data') else 0
        print(f"{status} {tool}: {data_count} items")


if __name__ == '__main__':
    asyncio.run(main())
