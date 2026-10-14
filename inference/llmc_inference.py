"""
llm.c inference wrapper for SubFluxGPT.
Provides Python interface to llm.c compiled binary for text generation.
"""

import os
import subprocess
import logging
import yaml
from typing import Optional, Dict, Any
import tempfile

logger = logging.getLogger(__name__)


class LLMCInference:
    """Inference wrapper for llm.c models."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize llm.c inference.
        
        Args:
            config_path: Path to configuration file
        """
        # Handle relative path
        if not os.path.isabs(config_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, config_path)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.llmc_config = self.config.get('training', {}).get('llmc', {})
        
        # Paths
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.llmc_dir = os.path.join(self.project_root, 'llm.c', 'llm.c-master')
        self.model_dir = os.path.join(self.project_root, 'models', 'llmc')
        
        # Binary path
        use_gpu = self.llmc_config.get('use_gpu', True)
        if use_gpu:
            self.binary_path = os.path.join(self.llmc_dir, 'train_gpt2cu')
        else:
            self.binary_path = os.path.join(self.llmc_dir, 'train_gpt2')
        
        # Check if binary exists
        if not os.path.exists(self.binary_path):
            logger.warning(f"llm.c binary not found at {self.binary_path}")
            logger.warning("You may need to compile llm.c first")
        
        logger.info("Initialized LLMCInference")
    
    def check_binary(self) -> bool:
        """Check if llm.c binary exists and is executable."""
        return os.path.exists(self.binary_path) and os.access(self.binary_path, os.X_OK)
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.8,
        top_p: float = 0.9,
        model_size: str = '124M',
        checkpoint_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using llm.c model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            model_size: Model size (124M, 350M, 774M, 1558M)
            checkpoint_path: Path to model checkpoint (if None, uses default)
            
        Returns:
            Dictionary with generated text and metadata
        """
        try:
            if not self.check_binary():
                logger.error("llm.c binary not found or not executable")
                return {
                    'success': False,
                    'error': 'llm.c binary not found - compile llm.c first'
                }
            
            # Find checkpoint
            if checkpoint_path is None:
                checkpoint_path = os.path.join(self.model_dir, f'gpt2_{model_size}_model.bin')
            
            if not os.path.exists(checkpoint_path):
                logger.error(f"Checkpoint not found: {checkpoint_path}")
                return {
                    'success': False,
                    'error': f'Model checkpoint not found: {checkpoint_path}'
                }
            
            # Create temporary file for prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            try:
                # Build command
                # Note: llm.c's train_gpt2cu is primarily for training
                # For inference, we might need a separate inference binary or use eval mode
                # For now, this is a placeholder - actual llm.c inference requires
                # either building a separate inference binary or using eval mode
                
                cmd = [
                    self.binary_path,
                    '--checkpoint', checkpoint_path,
                    '--prompt_file', prompt_file,
                    '--max_tokens', str(max_tokens),
                    '--temperature', str(temperature),
                    '--top_p', str(top_p)
                ]
                
                logger.info(f"Running llm.c inference: {' '.join(cmd)}")
                
                # Run inference
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    logger.error(f"Inference failed: {result.stderr}")
                    return {
                        'success': False,
                        'error': result.stderr
                    }
                
                # Parse output
                generated_text = result.stdout.strip()
                
                return {
                    'success': True,
                    'generated_text': generated_text,
                    'model_size': model_size,
                    'checkpoint': checkpoint_path
                }
                
            finally:
                # Clean up temp file
                if os.path.exists(prompt_file):
                    os.unlink(prompt_file)
                    
        except subprocess.TimeoutExpired:
            logger.error("Inference timed out")
            return {
                'success': False,
                'error': 'Inference timed out'
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def tokenize(self, text: str) -> list:
        """
        Tokenize text using GPT-2 tokenizer (for llm.c compatibility).
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of token IDs
        """
        try:
            import tiktoken
            enc = tiktoken.get_encoding("gpt2")
            tokens = enc.encode_ordinary(text)
            return tokens
        except ImportError:
            logger.error("tiktoken not installed - pip install tiktoken")
            return []
    
    def detokenize(self, tokens: list) -> str:
        """
        Detokenize token IDs using GPT-2 tokenizer.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Decoded text
        """
        try:
            import tiktoken
            enc = tiktoken.get_encoding("gpt2")
            text = enc.decode(tokens)
            return text
        except ImportError:
            logger.error("tiktoken not installed - pip install tiktoken")
            return ""


def main():
    """Test llm.c inference."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test llm.c inference")
    parser.add_argument('--prompt', type=str, default="Program: example.com\nReport title: XSS vulnerability",
                        help='Input prompt')
    parser.add_argument('--model_size', type=str, default='124M',
                        help='Model size')
    parser.add_argument('--max_tokens', type=int, default=256,
                        help='Max tokens to generate')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    inference = LLMCInference()
    result = inference.generate(
        prompt=args.prompt,
        max_tokens=args.max_tokens,
        model_size=args.model_size
    )
    
    if result['success']:
        print(f"Generated text:\n{result['generated_text']}")
    else:
        print(f"Error: {result['error']}")


if __name__ == '__main__':
    main()
