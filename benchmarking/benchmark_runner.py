"""
Benchmarking system for comparing local models with external APIs.
Runs both in parallel and compares results.
"""

import asyncio
import logging
import time
import psutil
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external_apis.api_client import MultiAPIClient, APIResponse

# Import load_model lazily to avoid circular dependency
def get_load_model():
    try:
        from inference.model_server import load_model
        return load_model
    except ImportError:
        return None

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run."""
    timestamp: str
    domain: str
    model_type: str  # "local" or "external"
    provider: str  # e.g., "llama2c_42M", "openai", "anthropic"
    model_name: str
    prompt: str
    response: str
    tokens_generated: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    context_window: Optional[int] = None
    memory_mb: Optional[float] = None  # Memory usage in MB
    tokens_per_second: Optional[float] = None  # Throughput metric
    prompt_tokens: Optional[int] = None  # Number of tokens in prompt
    total_tokens: Optional[int] = None  # Total tokens (prompt + generated)
    
    def to_dict(self):
        return asdict(self)


class BenchmarkRunner:
    """Runs benchmarks comparing local and external models."""
    
    def __init__(self, config: Dict[str, Any], verbose: bool = True):
        """
        Initialize benchmark runner.
        
        Args:
            config: Configuration dictionary
            verbose: Enable verbose logging
        """
        self.config = config
        self.external_config = config.get('external_apis', {})
        self.local_config = config.get('local_models', {})
        self.verbose = verbose
        
        # Initialize external API clients
        self.multi_client = MultiAPIClient(self.external_config)
        
        # Results storage
        self.results = []
        
        # Setup verbose logging
        if self.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def log_verbose(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            logger.info(f"[VERBOSE] {message}")
    
    def create_domain_analysis_prompt(self, domain: str) -> str:
        """
        Create a prompt for domain analysis.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Prompt string
        """
        return f"""Analyze the domain: {domain}

Provide:
1. Potential subdomains (api, dev, staging, test, etc.)
2. Common vulnerabilities associated with this domain type
3. Suggested reconnaissance techniques
4. Risk assessment

Be specific and actionable."""
    
    async def benchmark_local_model(self, domain: str, model_name: str) -> BenchmarkResult:
        """
        Benchmark a local model with advanced metrics.
        
        Args:
            domain: Domain to analyze
            model_name: Name of local model
            
        Returns:
            BenchmarkResult
        """
        start_time = time.time()
        start_memory = self.get_memory_usage()
        prompt = self.create_domain_analysis_prompt(domain)
        
        self.log_verbose(f"Starting benchmark for local model: {model_name}")
        
        try:
            # Load model if not already loaded
            load_model_fn = get_load_model()
            if load_model_fn is None:
                raise ImportError("model_server not available. Install fastapi and dependencies.")

            from inference.model_server import models, GPT2_MODELS

            if model_name not in models or not models[model_name].get('loaded'):
                self.log_verbose(f"Loading model: {model_name}")
                load_model_fn(model_name)
            
            # Generate response
            if model_name in models and models[model_name].get('type') == 'gpt2':
                import torch
                from transformers import GPT2LMHeadModel, GPT2Tokenizer
                
                model = models[model_name]['model']
                tokenizer = models[model_name]['tokenizer']
                
                inputs = tokenizer.encode(prompt, return_tensors='pt')
                prompt_tokens = len(inputs[0])
                self.log_verbose(f"Prompt tokens: {prompt_tokens}")
                
                if torch.cuda.is_available():
                    inputs = inputs.to('cuda')
                    model = model.to('cuda')
                    self.log_verbose("Using CUDA GPU")
                
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_new_tokens=512,
                        temperature=0.8,
                        do_sample=True
                    )
                
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                tokens_generated = len(outputs[0]) - len(inputs[0])
                total_tokens = len(outputs[0])
                context_window = 1024  # GPT-2 context window
                
                self.log_verbose(f"Generated {tokens_generated} tokens (total: {total_tokens})")
            else:
                # Placeholder for llama2.c and nanoGPT
                response = f"Local model {model_name} analysis for {domain}"
                tokens_generated = 100
                prompt_tokens = len(prompt.split())
                total_tokens = prompt_tokens + tokens_generated
                context_window = 256
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            end_memory = self.get_memory_usage()
            memory_used = end_memory - start_memory
            tokens_per_second = (tokens_generated / (end_time - start_time)) if end_time > start_time else 0
            
            self.log_verbose(f"Latency: {latency_ms:.2f}ms, Memory: {memory_used:.2f}MB, Tokens/sec: {tokens_per_second:.2f}")
            
            return BenchmarkResult(
                timestamp=datetime.utcnow().isoformat(),
                domain=domain,
                model_type="local",
                provider="local",
                model_name=model_name,
                prompt=prompt,
                response=response,
                tokens_generated=tokens_generated,
                latency_ms=latency_ms,
                success=True,
                context_window=context_window,
                memory_mb=memory_used,
                tokens_per_second=tokens_per_second,
                prompt_tokens=prompt_tokens,
                total_tokens=total_tokens
            )
            
        except Exception as e:
            logger.error(f"Local model {model_name} benchmark failed: {e}")
            return BenchmarkResult(
                timestamp=datetime.utcnow().isoformat(),
                domain=domain,
                model_type="local",
                provider="local",
                model_name=model_name,
                prompt=prompt,
                response="",
                tokens_generated=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e),
                memory_mb=self.get_memory_usage() - start_memory
            )
    
    async def benchmark_external_api(self, domain: str, provider: str) -> BenchmarkResult:
        """
        Benchmark an external API with advanced metrics.
        
        Args:
            domain: Domain to analyze
            provider: Provider name
            
        Returns:
            BenchmarkResult
        """
        start_time = time.time()
        start_memory = self.get_memory_usage()
        prompt = self.create_domain_analysis_prompt(domain)
        
        self.log_verbose(f"Starting benchmark for external API: {provider}")
        
        try:
            response = await self.multi_client.generate(
                provider,
                prompt,
                max_tokens=512
            )
            
            # Get context window from config
            context_windows = {
                "openai": 128000,
                "anthropic": 200000,
                "cohere": 4096
            }
            context_window = context_windows.get(provider, 4096)
            
            end_time = time.time()
            latency_ms = response.latency_ms if response.latency_ms else (end_time - start_time) * 1000
            end_memory = self.get_memory_usage()
            memory_used = end_memory - start_memory
            tokens_per_second = (response.tokens_used / (end_time - start_time)) if end_time > start_time and response.tokens_used else 0
            
            self.log_verbose(f"API Response: {response.tokens_used} tokens, {latency_ms:.2f}ms")
            
            return BenchmarkResult(
                timestamp=datetime.utcnow().isoformat(),
                domain=domain,
                model_type="external",
                provider=provider,
                model_name=response.model,
                prompt=prompt,
                response=response.content,
                tokens_generated=response.tokens_used,
                latency_ms=latency_ms,
                success=response.success,
                error=response.error,
                context_window=context_window,
                memory_mb=memory_used,
                tokens_per_second=tokens_per_second,
                prompt_tokens=None,  # API may not provide this
                total_tokens=response.tokens_used
            )
            
        except Exception as e:
            logger.error(f"External API {provider} benchmark failed: {e}")
            return BenchmarkResult(
                timestamp=datetime.utcnow().isoformat(),
                domain=domain,
                model_type="external",
                provider=provider,
                model_name="unknown",
                prompt=prompt,
                response="",
                tokens_generated=0,
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e),
                memory_mb=self.get_memory_usage() - start_memory
            )
    
    async def run_full_benchmark(self, domain: str) -> List[BenchmarkResult]:
        """
        Run benchmark on all configured models and APIs.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            List of BenchmarkResult objects
        """
        logger.info(f"Running full benchmark for domain: {domain}")
        
        # Get local models to benchmark
        local_models = self.local_config.get('models', ['llama2c_42M', 'gpt2_124M'])
        
        # Get external providers to benchmark
        external_providers = list(self.multi_client.clients.keys())
        
        # Run all benchmarks in parallel
        tasks = []
        
        # Local model benchmarks
        for model_name in local_models:
            tasks.append(self.benchmark_local_model(domain, model_name))
        
        # External API benchmarks
        for provider in external_providers:
            tasks.append(self.benchmark_external_api(domain, provider))
        
        results = await asyncio.gather(*tasks)
        
        # Store results
        self.results.extend(results)
        
        # Log summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        logger.info(f"Benchmark complete: {len(successful)} successful, {len(failed)} failed")
        
        for result in successful:
            logger.info(
                f"  {result.provider}/{result.model_name}: "
                f"{result.latency_ms:.0f}ms, {result.tokens_generated} tokens"
            )
        
        return results
    
    def save_results(self, filepath: str):
        """
        Save benchmark results to file.
        
        Args:
            filepath: Path to save results
        """
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        
        logger.info(f"Saved {len(self.results)} benchmark results to {filepath}")
    
    def compare_results(self, domain: str) -> Dict[str, Any]:
        """
        Compare benchmark results for a domain.
        
        Args:
            domain: Domain to compare
            
        Returns:
            Comparison dictionary
        """
        domain_results = [r for r in self.results if r.domain == domain]
        
        if not domain_results:
            return {"error": "No results found for domain"}
        
        comparison = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "total_runs": len(domain_results),
            "successful_runs": len([r for r in domain_results if r.success]),
            "by_provider": {}
        }
        
        for result in domain_results:
            if result.success:
                comparison["by_provider"][f"{result.provider}/{result.model_name}"] = {
                    "latency_ms": result.latency_ms,
                    "tokens": result.tokens_generated,
                    "context_window": result.context_window,
                    "response_length": len(result.response)
                }
        
        return comparison
    
    def compare_local_backends(self, domain: str) -> Dict[str, Any]:
        """
        Compare different local LLM backends (llama2.c, nanoGPT, GPT-2, llm.c) with advanced metrics.
        
        Args:
            domain: Domain to compare
            
        Returns:
            Comparison dictionary with backend rankings
        """
        # Filter for local models only
        local_results = [r for r in self.results if r.domain == domain and r.model_type == "local"]
        
        if not local_results:
            return {"error": "No local model results found for domain"}
        
        # Group by backend type
        backends = {
            'llama2c': [],
            'nanogpt': [],
            'gpt2': [],
            'llmc': []
        }
        
        for result in local_results:
            if result.success:
                if result.model_name.startswith('llama2c'):
                    backends['llama2c'].append(result)
                elif result.model_name.startswith('nanogpt'):
                    backends['nanogpt'].append(result)
                elif result.model_name.startswith('gpt2'):
                    backends['gpt2'].append(result)
                elif result.model_name.startswith('llmc'):
                    backends['llmc'].append(result)
        
        # Calculate advanced metrics for each backend
        backend_stats = {}
        for backend, results in backends.items():
            if results:
                avg_latency = sum(r.latency_ms for r in results) / len(results)
                avg_tokens = sum(r.tokens_generated for r in results) / len(results)
                avg_response_len = sum(len(r.response) for r in results) / len(results)
                avg_memory = sum(r.memory_mb or 0 for r in results) / len(results)
                avg_tokens_per_sec = sum(r.tokens_per_second or 0 for r in results) / len(results)
                
                # Calculate standard deviation for latency
                latency_values = [r.latency_ms for r in results]
                latency_std = math.sqrt(sum((x - avg_latency) ** 2 for x in latency_values) / len(latency_values)) if len(latency_values) > 1 else 0
                
                backend_stats[backend] = {
                    "num_models": len(results),
                    "avg_latency_ms": avg_latency,
                    "latency_std_ms": latency_std,
                    "avg_tokens": avg_tokens,
                    "avg_response_length": avg_response_len,
                    "avg_memory_mb": avg_memory,
                    "avg_tokens_per_second": avg_tokens_per_sec,
                    "models": [r.model_name for r in results]
                }
        
        # Rank by latency (lower is better)
        ranking = sorted(
            [(backend, stats['avg_latency_ms']) for backend, stats in backend_stats.items()],
            key=lambda x: x[1]
        )
        
        # Rank by throughput (higher is better)
        throughput_ranking = sorted(
            [(backend, stats['avg_tokens_per_second']) for backend, stats in backend_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        comparison = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "comparison_type": "local_backends_advanced",
            "backend_stats": backend_stats,
            "ranking_by_latency": [item[0] for item in ranking],
            "ranking_by_throughput": [item[0] for item in throughput_ranking],
            "summary": {
                "fastest_backend": ranking[0][0] if ranking else None,
                "slowest_backend": ranking[-1][0] if ranking else None,
                "highest_throughput_backend": throughput_ranking[0][0] if throughput_ranking else None,
                "total_backends_tested": len([b for b in backends.values() if b])
            }
        }
        
        self.log_verbose(f"Backend comparison: {comparison['summary']}")
        return comparison
    
    def generate_advanced_report(self, domain: str) -> Dict[str, Any]:
        """
        Generate an advanced benchmarking report with statistical analysis.
        
        Args:
            domain: Domain to analyze
            
        Returns:
            Advanced report dictionary
        """
        domain_results = [r for r in self.results if r.domain == domain]
        
        if not domain_results:
            return {"error": "No results found for domain"}
        
        successful = [r for r in domain_results if r.success]
        failed = [r for r in domain_results if not r.success]
        
        # Calculate overall statistics
        if successful:
            latencies = [r.latency_ms for r in successful]
            token_counts = [r.tokens_generated for r in successful]
            memory_usage = [r.memory_mb or 0 for r in successful]
            throughput = [r.tokens_per_second or 0 for r in successful]
            
            report = {
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat(),
                "overview": {
                    "total_runs": len(domain_results),
                    "successful_runs": len(successful),
                    "failed_runs": len(failed),
                    "success_rate": len(successful) / len(domain_results) if domain_results else 0
                },
                "performance_statistics": {
                    "latency": {
                        "min_ms": min(latencies),
                        "max_ms": max(latencies),
                        "avg_ms": sum(latencies) / len(latencies),
                        "median_ms": sorted(latencies)[len(latencies) // 2],
                        "std_ms": math.sqrt(sum((x - sum(latencies) / len(latencies)) ** 2 for x in latencies) / len(latencies))
                    },
                    "tokens_generated": {
                        "min": min(token_counts),
                        "max": max(token_counts),
                        "avg": sum(token_counts) / len(token_counts),
                        "total": sum(token_counts)
                    },
                    "memory_usage": {
                        "min_mb": min(memory_usage),
                        "max_mb": max(memory_usage),
                        "avg_mb": sum(memory_usage) / len(memory_usage)
                    },
                    "throughput": {
                        "min_tokens_sec": min(throughput),
                        "max_tokens_sec": max(throughput),
                        "avg_tokens_sec": sum(throughput) / len(throughput)
                    }
                },
                "by_model_type": {
                    "local": {
                        "count": len([r for r in successful if r.model_type == "local"]),
                        "avg_latency_ms": sum(r.latency_ms for r in successful if r.model_type == "local") / len([r for r in successful if r.model_type == "local"]) if [r for r in successful if r.model_type == "local"] else 0
                    },
                    "external": {
                        "count": len([r for r in successful if r.model_type == "external"]),
                        "avg_latency_ms": sum(r.latency_ms for r in successful if r.model_type == "external") / len([r for r in successful if r.model_type == "external"]) if [r for r in successful if r.model_type == "external"] else 0
                    }
                },
                "recommendations": self._generate_recommendations(successful)
            }
        else:
            report = {
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat(),
                "overview": {
                    "total_runs": len(domain_results),
                    "successful_runs": 0,
                    "failed_runs": len(failed),
                    "success_rate": 0
                },
                "error": "No successful benchmark runs"
            }
        
        return report
    
    def _generate_recommendations(self, results: List[BenchmarkResult]) -> List[str]:
        """Generate recommendations based on benchmark results."""
        recommendations = []
        
        if not results:
            return ["No successful runs to analyze"]
        
        # Compare local vs external
        local_results = [r for r in results if r.model_type == "local"]
        external_results = [r for r in results if r.model_type == "external"]
        
        if local_results and external_results:
            avg_local_latency = sum(r.latency_ms for r in local_results) / len(local_results)
            avg_external_latency = sum(r.latency_ms for r in external_results) / len(external_results)
            
            if avg_local_latency < avg_external_latency:
                speedup = (avg_external_latency / avg_local_latency) - 1
                recommendations.append(f"Local models are {speedup:.1%} faster than external APIs")
            else:
                slowdown = (avg_local_latency / avg_external_latency) - 1
                recommendations.append(f"External APIs are {slowdown:.1%} faster than local models")
        
        # Memory usage recommendations
        memory_usage = [r.memory_mb for r in results if r.memory_mb]
        if memory_usage:
            avg_memory = sum(memory_usage) / len(memory_usage)
            if avg_memory > 1000:
                recommendations.append(f"High memory usage detected ({avg_memory:.1f}MB avg). Consider using smaller models or quantization.")
        
        # Throughput recommendations
        throughput = [r.tokens_per_second for r in results if r.tokens_per_second]
        if throughput:
            avg_throughput = sum(throughput) / len(throughput)
            if avg_throughput < 10:
                recommendations.append(f"Low throughput detected ({avg_throughput:.1f} tokens/sec). Consider batch processing or model optimization.")
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources."""
        self.multi_client.close_all()
