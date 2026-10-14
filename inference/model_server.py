"""
FastAPI inference server for SubFluxGPT models.
Provides REST API for model inference and domain analysis.
"""

import logging
import os
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
import torch
import yaml
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SubFluxGPT Inference Server", version="1.0.0")


class GenerationRequest(BaseModel):
    """Request model for text generation."""
    prompt: str
    max_new_tokens: int = 256
    temperature: float = 0.8
    top_p: float = 0.9
    model: str = "llama2c_42M"  # llama2c_15M, llama2c_42M, llama2c_110M, gpt2_124M, gpt2_355M, gpt2_774M


class GenerationResponse(BaseModel):
    """Response model for text generation."""
    generated_text: str
    tokens_generated: int
    model: str
    latency_ms: float


class DomainAnalysisRequest(BaseModel):
    """Request model for domain analysis."""
    domain: str
    model: str = "llama2c_42M"  # llama2c_15M, llama2c_42M, llama2c_110M, gpt2_124M, gpt2_355M, gpt2_774M


class DomainAnalysisResponse(BaseModel):
    """Response model for domain analysis."""
    domain: str
    analysis: str
    suggested_subdomains: List[str]
    suggested_vulnerabilities: List[str]
    model: str


# Model cache (TODO: Implement actual model loading)
models = {}

# GPT-2 model mappings
GPT2_MODELS = {
    'gpt2_124M': 'gpt2',
    'gpt2_355M': 'gpt2-medium',
    'gpt2_774M': 'gpt2-large',
    'gpt2_1558M': 'gpt2-xl'
}

# llm.c model mappings
LLMC_MODELS = {
    'llmc_124M': '124M',
    'llmc_350M': '350M',
    'llmc_774M': '774M',
    'llmc_1558M': '1558M'
}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SubFluxGPT Inference Server",
        "version": "1.0.0",
        "endpoints": {
            "/generate": "Generate text from prompt",
            "/analyze_domain": "Analyze a domain",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "models_loaded": list(models.keys())}


@app.post("/generate", response_model=GenerationResponse)
async def generate_text(request: GenerationRequest):
    """
    Generate text from a prompt.
    
    Args:
        request: GenerationRequest with prompt and parameters
        
    Returns:
        GenerationResponse with generated text
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generation request: prompt='{request.prompt}', model={request.model}")

        # Check if model is loaded
        if request.model not in models or not models[request.model].get('loaded'):
            # Try to load the model
            load_model(request.model)

        # For GPT-2 models, use the loaded model and tokenizer
        if request.model in models and models[request.model].get('type') == 'gpt2':
            model = models[request.model]['model']
            tokenizer = models[request.model]['tokenizer']
            
            # Generate text using GPT-2
            inputs = tokenizer.encode(request.prompt, return_tensors='pt')
            if torch.cuda.is_available():
                inputs = inputs.to('cuda')
                model = model.to('cuda')
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=request.max_new_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    do_sample=True
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            tokens_generated = len(outputs[0]) - len(inputs[0])
        elif request.model in models and models[request.model].get('type') == 'llmc':
            # llm.c models - not yet implemented for inference
            logger.warning(f"llm.c inference not yet implemented for {request.model}")
            generated_text = f"llm.c inference not yet implemented. Use GPT-2 models instead."
            tokens_generated = len(generated_text.split())
        else:
            # Placeholder for llama2.c and nanoGPT
            generated_text = f"Generated response for: {request.prompt}"
            tokens_generated = len(generated_text.split())
        
        latency_ms = (time.time() - start_time) * 1000
        
        return GenerationResponse(
            generated_text=generated_text,
            tokens_generated=tokens_generated,
            model=request.model,
            latency_ms=latency_ms
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_domain", response_model=DomainAnalysisResponse)
async def analyze_domain(request: DomainAnalysisRequest, run_benchmark: bool = Query(False, description="Run benchmark comparison with external APIs")):
    """
    Analyze a domain using the trained model.

    Args:
        request: DomainAnalysisRequest with domain
        run_benchmark: If True, run benchmark comparison with external APIs

    Returns:
        DomainAnalysisResponse with analysis results
    """
    try:
        logger.info(f"Domain analysis request: domain={request.domain}, model={request.model}")

        # Generate analysis using the local model
        gen_request = GenerationRequest(
            prompt=f"Analyze the domain: {request.domain}\n\nProvide potential subdomains and vulnerabilities.",
            max_new_tokens=256,
            temperature=0.8,
            model=request.model
        )
        gen_response = await generate_text(gen_request)

        analysis = gen_response.generated_text

        # Parse analysis for suggestions (simple heuristic)
        suggested_subdomains = ["api", "dev", "staging", "test", "admin", "www"]
        suggested_vulnerabilities = ["subdomain takeover", "dns misconfiguration", "xss", "sqli"]

        # Run benchmark if requested
        if run_benchmark:
            logger.info(f"Running benchmark for domain: {request.domain}")
            try:
                import asyncio
                from benchmarking.benchmark_runner import BenchmarkRunner

                async def run_benchmark_task():
                    # Load config
                    with open('config.yaml', 'r') as f:
                        config = yaml.safe_load(f)

                    runner = BenchmarkRunner(config)
                    try:
                        results = await runner.run_full_benchmark(request.domain)
                        # Save results
                        os.makedirs('benchmarking/results', exist_ok=True)
                        runner.save_results('benchmarking/results/latest.json')
                        logger.info(f"Benchmark completed with {len(results)} results")
                    finally:
                        runner.cleanup()

                # Run benchmark in background
                asyncio.create_task(run_benchmark_task())
            except Exception as e:
                logger.warning(f"Benchmark failed: {e}")

        return DomainAnalysisResponse(
            domain=request.domain,
            analysis=analysis,
            suggested_subdomains=suggested_subdomains,
            suggested_vulnerabilities=suggested_vulnerabilities,
            model=request.model
        )

    except Exception as e:
        logger.error(f"Domain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def load_model(model_name: str):
    """
    Load a model into memory.
    
    Args:
        model_name: Name of the model to load
    """
    # TODO: Implement actual model loading
    # This would load the llama2.c or nanoGPT model
    logger.info(f"Loading model: {model_name}")
    
    # If it's a GPT-2 model, load using HuggingFace Transformers
    if model_name.startswith('gpt2_'):
        try:
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            
            hf_model_name = GPT2_MODELS.get(model_name, 'gpt2')
            model_path = f"./models/gpt2/{model_name}"
            
            if os.path.exists(model_path):
                # Load fine-tuned model
                model = GPT2LMHeadModel.from_pretrained(model_path)
                tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            else:
                # Load pre-trained model
                model = GPT2LMHeadModel.from_pretrained(hf_model_name)
                tokenizer = GPT2Tokenizer.from_pretrained(hf_model_name)
            
            models[model_name] = {
                "loaded": True,
                "type": "gpt2",
                "model": model,
                "tokenizer": tokenizer
            }
            logger.info(f"Loaded GPT-2 model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load GPT-2 model {model_name}: {e}")
            models[model_name] = {"loaded": False, "error": str(e)}
    elif model_name.startswith('llmc_'):
        # llm.c models - note: llm.c is primarily for training
        # Inference would require building a separate inference binary
        # For now, mark as placeholder
        logger.info(f"llm.c model {model_name} - inference not yet implemented")
        models[model_name] = {
            "loaded": False,
            "type": "llmc",
            "error": "llm.c inference not yet implemented - use GPT-2 (HuggingFace) for now"
        }
    else:
        # Load llama2.c or nanoGPT model
        models[model_name] = {"loaded": True}


def main():
    """Main entry point for the inference server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Start SubFluxGPT inference server')
    parser.add_argument('--host', type=str, default=None, help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    parser.add_argument('--workers', type=int, default=None, help='Number of workers')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()
    
    # Setup verbose logging if requested
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("Verbose mode enabled")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    if not os.path.exists(config_path):
        config_path = 'config.yaml'

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    inference_config = config.get('inference', {})
    host = args.host or inference_config.get('host', '0.0.0.0')
    port = args.port or inference_config.get('port', 8000)
    workers = args.workers or inference_config.get('workers', 4)
    
    # Load default model
    default_model = inference_config.get('default_model', 'llama2c_42M')
    logger.info(f"Loading default model: {default_model}")
    load_model(default_model)
    
    logger.info(f"Starting inference server on {host}:{port} with {workers} workers")
    
    uvicorn.run(
        "inference.model_server:app",
        host=host,
        port=port,
        workers=workers,
        reload=False
    )


if __name__ == '__main__':
    main()
