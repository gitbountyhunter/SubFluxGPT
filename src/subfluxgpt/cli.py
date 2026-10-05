"""
CLI interface for SubFluxGPT
"""

import argparse
import asyncio
import sys
import os
from typing import Optional, List

from .ai_router import LLMRouter
from .netlas_client import NetlasClient
from .bbrf_client import BBRFClient
from .dns_resolver import DNSResolver
from .http_prober import HTTPProber
from .utils import (
    read_subdomains_from_file,
    write_subdomains_to_file,
    extract_domain,
    normalize_subdomain,
    validate_subdomain,
    deduplicate_subdomains,
    merge_with_known,
    parse_ai_response,
    print_progress,
    format_output
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="SubFluxGPT - AI-powered subdomain enumeration for bug bounty hunters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with Gemini
  subfluxgpt -i subs.txt -o new_subs.txt --api gemini

  # Pipe to BBRF
  subfluxgpt -i subs.txt --api gemini | bbrf domain add -

  # Resolve and probe with httpx
  subfluxgpt -i subs.txt --api gemini --resolve --probe | httpx -status-code

  # Netlas enrichment
  subfluxgpt -i subs.txt --api gemini --netlas-enrich -o enriched.json

  # Multi-API fallback
  subfluxgpt -i subs.txt --api gemini --fallback claude,openai
        """
    )
    
    # Input/Output
    parser.add_argument(
        '-i', '--input',
        help='Input file with known subdomains',
        dest='input_file',
        required=True
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for results (default: stdout)',
        dest='output_file'
    )
    parser.add_argument(
        '--format',
        help='Output format (text, json, csv)',
        dest='output_format',
        default='text',
        choices=['text', 'json', 'csv']
    )
    
    # AI Configuration
    parser.add_argument(
        '--api',
        help='Primary AI API to use',
        dest='api',
        default='gemini',
        choices=['gemini', 'claude', 'openai', 'grok', 'deepseek']
    )
    parser.add_argument(
        '--fallback',
        help='Fallback APIs (comma-separated)',
        dest='fallback_apis',
        default=''
    )
    parser.add_argument(
        '--count',
        help='Number of subdomains to generate',
        dest='count',
        type=int,
        default=50
    )
    
    # DNS Resolution
    parser.add_argument(
        '--resolve',
        help='Resolve generated subdomains',
        dest='resolve',
        action='store_true'
    )
    parser.add_argument(
        '--dont-resolve',
        help='Skip DNS resolution (output only generated)',
        dest='dont_resolve',
        action='store_true'
    )
    parser.add_argument(
        '--wildcard-check',
        help='Check for wildcard DNS',
        dest='wildcard_check',
        action='store_true',
        default=True
    )
    
    # HTTP Probing
    parser.add_argument(
        '--probe',
        help='Probe subdomains with HTTP',
        dest='probe',
        action='store_true'
    )
    parser.add_argument(
        '--probe-scheme',
        help='HTTP scheme to probe (http, https, both)',
        dest='probe_scheme',
        default='https',
        choices=['http', 'https', 'both']
    )
    
    # Netlas Integration
    parser.add_argument(
        '--netlas-enrich',
        help='Enrich results with Netlas data',
        dest='netlas_enrich',
        action='store_true'
    )
    parser.add_argument(
        '--netlas-dork',
        help='Custom Netlas dork query',
        dest='netlas_dork'
    )
    
    # BBRF Integration
    parser.add_argument(
        '--bbrf-program',
        help='BBRF program name for scoping',
        dest='bbrf_program'
    )
    parser.add_argument(
        '--bbrf-scope-check',
        help='Check BBRF scope before adding',
        dest='bbrf_scope_check',
        action='store_true',
        default=True
    )
    
    # Other options
    parser.add_argument(
        '--verbose',
        help='Verbose output',
        dest='verbose',
        action='store_true'
    )
    parser.add_argument(
        '--concurrent',
        help='Concurrent operations',
        dest='concurrent',
        type=int,
        default=50
    )
    
    return parser.parse_args()


async def main():
    """Main async function"""
    args = parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"[Error] Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Read known subdomains
    print(f"[*] Reading subdomains from {args.input_file}...", file=sys.stderr)
    known_subdomains = read_subdomains_from_file(args.input_file)
    
    if not known_subdomains:
        print("[Error] No subdomains found in input file", file=sys.stderr)
        sys.exit(1)
    
    print(f"[*] Loaded {len(known_subdomains)} known subdomains", file=sys.stderr)
    
    # Extract domain
    domain = extract_domain(known_subdomains[0])
    print(f"[*] Target domain: {domain}", file=sys.stderr)
    
    # Normalize subdomains (remove domain suffix)
    normalized_subs = [normalize_subdomain(sub, domain) for sub in known_subdomains]
    normalized_subs = [sub for sub in normalized_subs if validate_subdomain(sub)]
    normalized_subs = deduplicate_subdomains(normalized_subs)
    
    print(f"[*] Normalized to {len(normalized_subs)} unique subdomain patterns", file=sys.stderr)
    
    # Initialize AI router
    fallback_apis = [api.strip() for api in args.fallback_apis.split(',') if api.strip()]
    print(f"[*] Using {args.api} API with fallbacks: {fallback_apis or 'none'}", file=sys.stderr)
    
    try:
        llm_router = LLMRouter(primary_api=args.api, fallback_apis=fallback_apis)
    except ValueError as e:
        print(f"[Error] {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Generate subdomains using AI
    print("[*] Generating subdomains with AI...", file=sys.stderr)
    response = await llm_router.generate_subdomains(
        known_subdomains=normalized_subs[:50],  # Limit to 50 for context
        count=args.count,
        domain=domain
    )
    
    if not response.success:
        print(f"[Error] AI generation failed: {response.error}", file=sys.stderr)
        sys.exit(1)
    
    print(f"[*] AI response received (tokens used: {response.tokens_used})", file=sys.stderr)
    
    # Parse AI response
    generated_subs = parse_ai_response(response.content)
    generated_subs = [validate_subdomain(sub) and sub or None for sub in generated_subs]
    generated_subs = [sub for sub in generated_subs if sub]
    generated_subs = deduplicate_subdomains(generated_subs)
    
    print(f"[*] Generated {len(generated_subs)} new subdomains", file=sys.stderr)
    
    # Add domain suffix
    full_generated = [f"{sub}.{domain}" if not sub.endswith(domain) else sub for sub in generated_subs]
    
    # DNS Resolution
    resolved_subs = []
    if args.resolve and not args.dont_resolve:
        print("[*] Resolving subdomains...", file=sys.stderr)
        dns_resolver = DNSResolver()
        
        if args.wildcard_check:
            dns_resolver.detect_wildcard(domain)
        
        resolution_results = await dns_resolver.resolve_subdomains(
            full_generated,
            wildcard_check=args.wildcard_check,
            concurrent=args.concurrent
        )
        
        resolved_subs = dns_resolver.filter_resolved(resolution_results)
        print(f"[*] Resolved {len(resolved_subs)} subdomains", file=sys.stderr)
        
        # Use resolved for further processing
        subs_to_process = resolved_subs
    else:
        subs_to_process = full_generated
    
    # HTTP Probing
    if args.probe:
        print("[*] Probing subdomains with HTTP...", file=sys.stderr)
        async with HTTPProber() as prober:
            if args.probe_scheme == 'both':
                results = await prober.probe_both_schemes(subs_to_process, concurrent=args.concurrent)
                alive_subs = []
                for sub, data in results.items():
                    if data.get('https') and data['https'].status_code:
                        alive_subs.append(sub)
                    elif data.get('http') and data['http'].status_code:
                        alive_subs.append(sub)
            else:
                probe_results = await prober.probe_subdomains(
                    subs_to_process,
                    scheme=args.probe_scheme,
                    concurrent=args.concurrent
                )
                alive_subs = prober.filter_alive(probe_results)
        
        print(f"[*] Found {len(alive_subs)} alive subdomains", file=sys.stderr)
        subs_to_process = alive_subs
    
    # Netlas Enrichment
    if args.netlas_enrich:
        print("[*] Enriching with Netlas data...", file=sys.stderr)
        async with NetlasClient() as netlas:
            if args.netlas_dork:
                results = await netlas.advanced_dork(args.netlas_dork)
            else:
                results = await netlas.search_domain(domain)
            
            summary = netlas.results_to_summary(results)
            print(f"[*] Netlas data:\n{summary}", file=sys.stderr)
    
    # BBRF Integration
    if args.bbrf_program:
        print(f"[*] Adding to BBRF program: {args.bbrf_program}", file=sys.stderr)
        async with BBRFClient() as bbrf:
            added = await bbrf.add_domains(
                subs_to_process,
                program=args.bbrf_program,
                scope_check=args.bbrf_scope_check
            )
            print(f"[*] Added {added} domains to BBRF", file=sys.stderr)
    
    # Output
    if args.output_file:
        write_subdomains_to_file(subs_to_process, args.output_file)
        print(f"[*] Results written to {args.output_file}", file=sys.stderr)
    else:
        # Print to stdout
        output = format_output(subs_to_process, args.output_format)
        print(output)
    
    print("[*] Done!", file=sys.stderr)


def cli_entry():
    """CLI entry point"""
    args = parse_args()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[Error] {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
