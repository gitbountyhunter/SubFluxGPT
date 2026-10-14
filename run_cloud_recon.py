#!/usr/bin/env python3
"""
Cloud Recon Runner Script
Automated SNI-IP range reconnaissance for cloud providers.
Based on Jason Haddix's workflow with AI enhancements.
"""

import asyncio
import sys
import os
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cloud_recon import CloudReconManager, EnhancedCloudRecon


def main():
    """Main entry point for Cloud Recon."""
    parser = argparse.ArgumentParser(
        description='Cloud Recon - SNI-IP Range Reconnaissance for Bug Bounty',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and process all providers
  python3 run_cloud_recon.py --download --process

  # Filter by specific apex domain
  python3 run_cloud_recon.py --process --apex dell.com

  # Export for BountyCatch
  python3 run_cloud_recon.py --export --project dell_recon

  # Get one-liner commands (Jason Haddix style)
  python3 run_cloud_recon.py --one-liners --apex dell.com

  # Full workflow with AI analysis
  python3 run_cloud_recon.py --full --apex dell.com --project dell_recon --ai
        """
    )

    parser.add_argument('--download', action='store_true', help='Download cloud provider data')
    parser.add_argument('--process', action='store_true', help='Process downloaded data')
    parser.add_argument('--export', action='store_true', help='Export for BountyCatch')
    parser.add_argument('--one-liners', action='store_true', help='Show one-liner commands')
    parser.add_argument('--full', action='store_true', help='Run full workflow')
    parser.add_argument('--apex', type=str, help='Filter by apex domain (e.g., dell.com)')
    parser.add_argument('--project', type=str, default='cloud_recon', help='Project name for BountyCatch')
    parser.add_argument('--provider', type=str, choices=['amazon', 'digitalocean', 'google', 'microsoft', 'oracle'], help='Specific provider')
    parser.add_argument('--output-dir', type=str, default='./cloud_recon_data', help='Output directory')
    parser.add_argument('--ai', action='store_true', help='Enable AI analysis')
    parser.add_argument('--keep-wildcards', action='store_true', help='Keep wildcard domains')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
    
    # Enhanced features
    parser.add_argument('--enhanced', action='store_true', help='Run enhanced cloud recon with killer features')
    parser.add_argument('--no-ip', action='store_true', help='Disable IP analysis (enhanced mode)')
    parser.add_argument('--no-port', action='store_true', help='Disable port scanning (enhanced mode)')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL analysis (enhanced mode)')
    parser.add_argument('--no-tech', action='store_true', help='Disable tech fingerprinting (enhanced mode)')
    parser.add_argument('--threat-intel', action='store_true', help='Enable threat intelligence (enhanced mode)')
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

    # Initialize Cloud Recon Manager
    config = {'output_dir': args.output_dir}
    manager = CloudReconManager(config)

    # Download phase
    if args.download or args.full:
        print("=" * 60)
        print("Downloading Cloud Provider SNI-IP Range Data")
        print("=" * 60)
        print()

        if args.provider:
            results = {args.provider: manager.cloud_recon.download_provider_data(args.provider)}
        else:
            results = manager.cloud_recon.download_all_providers()

        for provider, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {provider}: {'Success' if success else 'Failed'}")

        print()

    # Process phase
    if args.process or args.full:
        print("=" * 60)
        print("Processing SNI-IP Range Data")
        print("=" * 60)
        print()

        if args.provider:
            results = {
                args.provider: manager.cloud_recon.process_provider_data(
                    args.provider,
                    apex_domain=args.apex,
                    keep_wildcards=args.keep_wildcards
                )
            }
        else:
            results = manager.cloud_recon.process_all_providers(
                apex_domain=args.apex,
                keep_wildcards=args.keep_wildcards
            )

        for provider, result in results.items():
            if provider == 'combined':
                print(f"\nCombined Results:")
                print(f"  Domains: {result['stats']['total_domains']}")
                print(f"  Wildcards: {result['stats']['total_wildcards']}")
                print(f"  Apex: {result['stats']['total_apex']}")
            elif result.get('success'):
                stats = result.get('stats', {})
                print(f"✓ {provider}:")
                print(f"  Regular domains: {stats.get('final_domains', 0)}")
                print(f"  Wildcards: {stats.get('final_wildcards', 0)}")
                print(f"  Apex domains: {stats.get('final_apex', 0)}")
            else:
                print(f"✗ {provider}: {result.get('error', 'Failed')}")

        print()

    # Export phase
    if args.export or args.full:
        print("=" * 60)
        print("Exporting for BountyCatch Remix")
        print("=" * 60)
        print()

        try:
            export_path = manager.cloud_recon.export_for_bountycatch(
                args.project,
                use_apex=False
            )
            print(f"✓ Exported to: {export_path}")
            print()
            print(f"To import into BountyCatch Remix:")
            print(f"  python3 bountycatch.py add -p {args.project} -f {export_path}")
        except Exception as e:
            print(f"✗ Export failed: {e}")

        print()

    # One-liners phase
    if args.one_liners:
        print("=" * 60)
        print("Jason Haddix Style One-Liner Commands")
        print("=" * 60)
        print()

        if not args.apex:
            print("Error: --apex required for one-liners")
            return

        if args.provider:
            commands = manager.cloud_recon.get_one_liner_commands(args.provider, args.apex)
            for cmd_info in commands:
                print(f"\n# {cmd_info['description']}")
                print(cmd_info['command'])
        else:
            for provider in manager.cloud_recon.PROVIDERS.keys():
                print(f"\n{'=' * 60}")
                print(f"Provider: {provider}")
                print(f"{'=' * 60}")
                commands = manager.cloud_recon.get_one_liner_commands(provider, args.apex)
                for cmd_info in commands:
                    print(f"\n# {cmd_info['description']}")
                    print(cmd_info['command'])

        print()

    # Full workflow with AI
    if args.full:
        print("=" * 60)
        print("Running Full Cloud Recon Workflow")
        print("=" * 60)
        print()

        results = manager.run_full_workflow(
            apex_domain=args.apex,
            project_name=args.project,
            ai_analysis=args.ai
        )

        # Save results
        results_file = Path(args.output_dir) / 'workflow_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ Workflow complete")
        print(f"✓ Results saved to: {results_file}")
        print()

        # Display AI analysis if available
        if args.ai and 'ai_analysis' in results.get('steps', {}):
            ai_results = results['steps']['ai_analysis']
            print("=" * 60)
            print("AI Analysis Results")
            print("=" * 60)
            print()

            print(f"Risk Level: {ai_results['risk_assessment'].get('level', 'N/A')}")
            print(f"Risk Score: {ai_results['risk_assessment'].get('score', 0)}")
            print()

            if ai_results.get('high_value_targets'):
                print(f"Top 5 High-Value Targets:")
                for target in ai_results['high_value_targets'][:5]:
                    print(f"  - {target['domain']} (score: {target['score']})")
                print()

            if ai_results.get('recommendations'):
                print("Recommendations:")
                for rec in ai_results['recommendations']:
                    print(f"  - {rec}")
                print()

    # Enhanced workflow with killer features
    if args.enhanced:
        print("=" * 60)
        print("Running Enhanced Cloud Recon with Killer Features")
        print("=" * 60)
        print()

        config = {'output_dir': args.output_dir}
        enhanced_recon = EnhancedCloudRecon(config, config_path=args.config)

        results = enhanced_recon.run_killer_recon(
            apex_domain=args.apex,
            project_name=args.project,
            enable_ip_analysis=not args.no_ip,
            enable_port_scan=not args.no_port,
            enable_ssl_analysis=not args.no_ssl,
            enable_tech_fingerprint=not args.no_tech,
            enable_threat_intel=args.threat_intel
        )

        # Display summary
        print()
        print("=" * 60)
        print("ENHANCED CLOUD RECON SUMMARY")
        print("=" * 60)
        print()

        for finding in results.get('summary', {}).get('key_findings', []):
            print(f"\n{finding['category']}:")
            print(f"  {finding['finding']}")

        print(f"\nFull results saved to: {results.get('history_file')}")
        print()


if __name__ == '__main__':
    main()
