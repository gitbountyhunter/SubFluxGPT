"""
Main benchmark runner script.
Runs benchmarks comparing local models with external APIs.
"""

import asyncio
import sys
import os
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from benchmarking.benchmark_runner import BenchmarkRunner


def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Run SubFluxGPT benchmarks')
    parser.add_argument('--domain', type=str, required=True, help='Domain to analyze')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--output', type=str, default='benchmarking/results/latest.json', help='Output file for results')
    parser.add_argument('--compare', action='store_true', help='Compare results after benchmark')
    parser.add_argument('--compare-backends', action='store_true', help='Compare local backends (llama2.c, nanoGPT, GPT-2, llm.c)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode with live updates')
    parser.add_argument('--advanced-report', action='store_true', help='Generate advanced statistical report')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Initialize benchmark runner with verbose mode
    runner = BenchmarkRunner(config, verbose=args.verbose)

    try:
        # Run full benchmark
        print(f"\n{'='*60}")
        print(f"Running benchmark for domain: {args.domain}")
        print(f"Verbose mode: {'ENABLED' if args.verbose else 'DISABLED'}")
        print(f"{'='*60}\n")

        results = await runner.run_full_benchmark(args.domain)

        # Save results
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        runner.save_results(args.output)

        print(f"\n{'='*60}")
        print(f"Results saved to: {args.output}")
        print(f"{'='*60}\n")

        # Compare results if requested
        if args.compare:
            comparison = runner.compare_results(args.domain)
            print("\nComparison:")
            import json
            print(json.dumps(comparison, indent=2))
        
        # Compare local backends if requested
        if args.compare_backends:
            backend_comparison = runner.compare_local_backends(args.domain)
            print("\nLocal Backend Comparison:")
            print(json.dumps(backend_comparison, indent=2))
        
        # Generate advanced report if requested
        if args.advanced_report:
            advanced_report = runner.generate_advanced_report(args.domain)
            report_file = args.output.replace('.json', '_advanced_report.json')
            with open(report_file, 'w') as f:
                json.dump(advanced_report, f, indent=2)
            print(f"\nAdvanced report saved to: {report_file}")
            print("\nAdvanced Report Summary:")
            print(json.dumps(advanced_report, indent=2))

    finally:
        # Cleanup
        runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
