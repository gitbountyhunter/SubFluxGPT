"""
llm.c training wrapper for SubFluxGPT.
Manages compilation and execution of llm.c for training GPT-2 models on bug bounty data.
"""

import os
import sys
import logging
import subprocess
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LLMCTrainer:
    """Trainer for llm.c (Karpathy's C/CUDA GPT-2 implementation)."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize llm.c trainer.
        
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
        self.data_dir = os.path.join(self.project_root, 'data', 'llmc')
        self.model_dir = os.path.join(self.project_root, 'models', 'llmc')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Model configurations for different GPT-2 sizes
        self.model_configs = {
            '124M': {
                'max_seq_len': 1024,
                'vocab_size': 50257,
                'num_layers': 12,
                'num_heads': 12,
                'channels': 768,
                'num_parameters': 124439808
            },
            '350M': {
                'max_seq_len': 1024,
                'vocab_size': 50257,
                'num_layers': 24,
                'num_heads': 16,
                'channels': 1024,
                'num_parameters': 350000000
            },
            '774M': {
                'max_seq_len': 1024,
                'vocab_size': 50257,
                'num_layers': 36,
                'num_heads': 20,
                'channels': 1280,
                'num_parameters': 774000000
            },
            '1558M': {
                'max_seq_len': 1024,
                'vocab_size': 50257,
                'num_layers': 48,
                'num_heads': 25,
                'channels': 1600,
                'num_parameters': 1558000000
            }
        }
        
        logger.info("Initialized LLMCTrainer")
    
    def check_llmc_exists(self) -> bool:
        """Check if llm.c directory exists."""
        return os.path.exists(self.llmc_dir)
    
    def compile_llmc(self, use_gpu: bool = True, precision: str = 'BF16') -> bool:
        """
        Compile llm.c training binary.
        
        Args:
            use_gpu: Whether to compile CUDA version (True) or CPU version (False)
            precision: Precision mode (BF16, FP16, FP32)
            
        Returns:
            True if compilation successful
        """
        try:
            if not self.check_llmc_exists():
                logger.error(f"llm.c directory not found at {self.llmc_dir}")
                return False
            
            logger.info(f"Compiling llm.c (GPU={use_gpu}, precision={precision})...")
            
            # Change to llm.c directory
            original_dir = os.getcwd()
            os.chdir(self.llmc_dir)
            
            try:
                if use_gpu:
                    # Compile CUDA version
                    cmd = ['make', 'train_gpt2cu', f'PRECISION={precision}']
                    if self.llmc_config.get('use_cudnn', False):
                        cmd.append('USE_CUDNN=1')
                else:
                    # Compile CPU version
                    cmd = ['make', 'train_gpt2']
                
                logger.info(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Compilation failed: {result.stderr}")
                    return False
                
                logger.info("llm.c compilation successful")
                return True
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            logger.error(f"Failed to compile llm.c: {e}")
            return False
    
    def get_binary_path(self, use_gpu: bool = True) -> str:
        """
        Get path to compiled llm.c binary.
        
        Args:
            use_gpu: Whether to use GPU or CPU binary
            
        Returns:
            Path to binary
        """
        if use_gpu:
            return os.path.join(self.llmc_dir, 'train_gpt2cu')
        else:
            return os.path.join(self.llmc_dir, 'train_gpt2')
    
    def check_data_files(self) -> bool:
        """Check if training data files exist."""
        train_file = os.path.join(self.data_dir, 'bugbounty_train.bin')
        val_file = os.path.join(self.data_dir, 'bugbounty_val.bin')
        
        if not os.path.exists(train_file):
            logger.error(f"Training data not found: {train_file}")
            return False
        
        if not os.path.exists(val_file):
            logger.error(f"Validation data not found: {val_file}")
            return False
        
        return True
    
    def train_model(self, model_size: str = '124M', use_gpu: bool = True) -> Dict[str, Any]:
        """
        Train a GPT-2 model using llm.c.
        
        Args:
            model_size: Model size (124M, 350M, 774M, 1558M)
            use_gpu: Whether to use GPU (CUDA) or CPU
            
        Returns:
            Training results dictionary
        """
        try:
            logger.info(f"Starting llm.c training for {model_size} model")
            
            # Check model config
            if model_size not in self.model_configs:
                logger.error(f"Unknown model size: {model_size}")
                return {'status': 'failed', 'error': f'Unknown model size: {model_size}'}
            
            model_config = self.model_configs[model_size]
            
            # Check llm.c exists
            if not self.check_llmc_exists():
                logger.error("llm.c not found - please extract llm.c-master.zip to llm.c/llm.c-master/")
                return {'status': 'failed', 'error': 'llm.c not found'}
            
            # Check data files
            if not self.check_data_files():
                logger.error("Training data not found - run prepare_llmc.py first")
                return {'status': 'failed', 'error': 'Training data not found'}
            
            # Compile if needed
            binary_path = self.get_binary_path(use_gpu)
            if not os.path.exists(binary_path):
                logger.info("Binary not found, compiling...")
                precision = self.llmc_config.get('precision', 'BF16')
                if not self.compile_llmc(use_gpu=use_gpu, precision=precision):
                    return {'status': 'failed', 'error': 'Compilation failed'}
            
            # Build training command
            # llm.c uses command-line arguments for configuration
            cmd = [
                binary_path,
                '-i', self.data_dir,  # input directory with .bin files
                '-o', self.model_dir,  # output directory for checkpoints
                '-v', str(self.llmc_config.get('eval_interval', 250)),  # eval interval
                '-s', str(self.llmc_config.get('sample_interval', 250)),  # sample interval
                '-g', str(self.llmc_config.get('num_gpus', 1)),  # number of GPUs
                '-l', str(self.llmc_config.get('learning_rate', 3e-4)),  # learning rate
                '-b', str(self.llmc_config.get('batch_size', 64)),  # batch size
                '-t', str(self.llmc_config.get('max_steps', 5000)),  # max steps
            ]
            
            # Add model-specific parameters
            # Note: llm.c has specific model configs built in, we may need to modify or use scripts
            
            # Change to llm.c directory for training
            original_dir = os.getcwd()
            os.chdir(self.llmc_dir)
            
            try:
                logger.info(f"Running training command: {' '.join(cmd)}")
                
                # Run training
                # Use subprocess with real-time output
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Stream output
                for line in process.stdout:
                    logger.info(line.rstrip())
                
                process.wait()
                
                if process.returncode != 0:
                    logger.error(f"Training failed with return code {process.returncode}")
                    return {'status': 'failed', 'error': f'Training failed with code {process.returncode}'}
                
                logger.info(f"Training completed successfully for {model_size}")
                
                return {
                    'status': 'success',
                    'model_size': model_size,
                    'output_dir': self.model_dir,
                    'use_gpu': use_gpu
                }
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            logger.error(f"Failed to train {model_size} model: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def train_from_scratch(self, model_size: str = '124M', use_gpu: bool = True) -> Dict[str, Any]:
        """
        Train a GPT-2 model from scratch using llm.c.
        This uses the llm.c scripts for different model sizes.
        
        Args:
            model_size: Model size
            use_gpu: Whether to use GPU
            
        Returns:
            Training results
        """
        try:
            logger.info(f"Training {model_size} from scratch using llm.c scripts")
            
            # llm.c has scripts in the scripts/ directory for different model sizes
            # We'll use the appropriate script
            scripts_dir = os.path.join(self.llmc_dir, 'scripts')
            
            # Find appropriate script
            script_map = {
                '124M': 'gpt2_124M.sh',
                '350M': 'gpt2_350M.sh',
                '774M': 'gpt2_774M.sh',
                '1558M': 'gpt2_160M.sh'  # 1.6B
            }
            
            script_name = script_map.get(model_size)
            if not script_name:
                logger.error(f"No script found for model size {model_size}")
                return {'status': 'failed', 'error': f'No script for {model_size}'}
            
            script_path = os.path.join(scripts_dir, script_name)
            if not os.path.exists(script_path):
                logger.warning(f"Script {script_path} not found, using generic training")
                return self.train_model(model_size, use_gpu)
            
            # For now, use the generic train_model method
            # In the future, we could parse and modify the scripts
            return self.train_model(model_size, use_gpu)
            
        except Exception as e:
            logger.error(f"Failed to train from scratch: {e}")
            return {'status': 'failed', 'error': str(e)}


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train GPT-2 models using llm.c")
    parser.add_argument('--model_size', type=str, default='124M', 
                        choices=['124M', '350M', '774M', '1558M'],
                        help='Model size to train')
    parser.add_argument('--use_gpu', action='store_true', default=True,
                        help='Use GPU (CUDA) for training')
    parser.add_argument('--compile_only', action='store_true',
                        help='Only compile, do not train')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to config file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose mode with live updates')
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.verbose:
        logger.info("Verbose mode enabled")
    
    trainer = LLMCTrainer(config_path=args.config)
    
    if args.compile_only:
        precision = trainer.llmc_config.get('precision', 'BF16')
        logger.info(f"Compiling with GPU={args.use_gpu}, precision={precision}")
        success = trainer.compile_llmc(use_gpu=args.use_gpu, precision=precision)
        print(f"Compilation {'successful' if success else 'failed'}")
    else:
        logger.info(f"Training {args.model_size} model with GPU={args.use_gpu}")
        results = trainer.train_model(args.model_size, use_gpu=args.use_gpu)
        print(f"Training results: {results}")


if __name__ == '__main__':
    main()
