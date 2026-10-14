"""
Training scheduler for continuous model training.
Orchestrates periodic training runs for multiple model sizes.
"""

import asyncio
import logging
import subprocess
import yaml
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import torch

from data_collector.database_manager import DatabaseManager
from training_pipeline.evaluator import ModelEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingScheduler:
    """Schedules and manages continuous model training."""
    
    def __init__(self, config_path: str = 'config.yaml', verbose: bool = True):
        """
        Initialize the training scheduler.
        
        Args:
            config_path: Path to configuration file
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        if self.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.config = self._load_config(config_path)
        self.training_config = self.config.get('training', {})
        
        # Initialize database
        db_url = self.config['database']['url']
        self.db_manager = DatabaseManager(db_url)
        
        # Model sizes to train
        self.model_sizes = self.training_config.get('model_sizes', ['15M', '42M', '110M'])
        
        # GPT-2 model sizes
        self.gpt2_model_sizes = self.training_config.get('gpt2', {}).get('model_sizes', ['124M', '355M', '774M'])
        
        # llm.c model sizes
        self.llmc_model_sizes = self.training_config.get('llmc', {}).get('model_sizes', ['124M', '350M'])
        
        # Training trigger threshold
        self.min_new_reports = self.training_config.get('min_new_reports', 1000)
        
        # llama2.c configuration
        self.llama2c_config = self.training_config.get('llama2c', {})
        
        # nanoGPT configuration
        self.nanogpt_config = self.training_config.get('nanogpt', {})
        
        # llm.c configuration
        self.llmc_config = self.training_config.get('llmc', {})
        
        # Model evaluator
        self.evaluator = ModelEvaluator(config_path=config_path)
        
        # Track last training run
        self.last_report_count = 0
        self.last_training_time = None
        
        logger.info("Initialized TrainingScheduler")
    
    def log_verbose(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            logger.info(f"[VERBOSE] {message}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    def check_training_trigger(self) -> bool:
        """
        Check if training should be triggered.
        
        Returns:
            True if enough new reports have accumulated
        """
        current_report_count = self.db_manager.get_report_count()
        new_reports = current_report_count - self.last_report_count
        
        self.log_verbose(f"Current report count: {current_report_count}, New reports: {new_reports}")
        logger.info(f"Current report count: {current_report_count}, New reports: {new_reports}")
        
        if new_reports >= self.min_new_reports:
            self.log_verbose(f"Training trigger: {new_reports} new reports >= {self.min_new_reports} threshold")
            logger.info(f"Training trigger: {new_reports} new reports >= {self.min_new_reports} threshold")
            self.last_report_count = current_report_count
            return True
        
        return False
    
    def prepare_data(self, vocab_size: int = 4096) -> bool:
        """
        Prepare training data from database.
        
        Args:
            vocab_size: Vocabulary size for tokenizer
            
        Returns:
            True if successful
        """
        try:
            logger.info("Preparing training data...")
            
            # Run prepare_bugbounty.py
            cmd = [
                'python', 'training_pipeline/prepare_bugbounty.py',
                '--vocab_size', str(vocab_size)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Data preparation failed: {result.stderr}")
                return False
            
            logger.info("Data preparation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare data: {e}")
            return False
    
    def train_llama2c_model(self, model_size: str) -> bool:
        """
        Train a llama2.c model of specified size.
        
        Args:
            model_size: Model size (15M, 42M, 110M)
            
        Returns:
            True if successful
        """
        try:
            self.log_verbose(f"Starting llama2.c training for {model_size} model")
            logger.info(f"Starting llama2.c training for {model_size} model")
            
            # Set model parameters based on size
            model_params = {
                '15M': {'dim': 288, 'n_layers': 6, 'n_heads': 6, 'n_kv_heads': 6},
                '42M': {'dim': 512, 'n_layers': 8, 'n_heads': 8, 'n_kv_heads': 8},
                '110M': {'dim': 768, 'n_layers': 12, 'n_heads': 12, 'n_kv_heads': 12}
            }
            
            params = model_params.get(model_size, model_params['42M'])
            self.log_verbose(f"Model parameters: {params}")
            
            # Build training command
            cmd = [
                'python', 'llama2.c/train.py',
                '--batch_size', str(self.llama2c_config.get('batch_size', 16)),
                '--gradient_accumulation_steps', str(self.llama2c_config.get('gradient_accumulation_steps', 8)),
                '--max_seq_len', str(self.llama2c_config.get('max_seq_len', 256)),
                '--vocab_size', str(self.llama2c_config.get('vocab_size', 4096)),
                '--dim', str(params['dim']),
                '--n_layers', str(params['n_layers']),
                '--n_heads', str(params['n_heads']),
                '--n_kv_heads', str(params['n_kv_heads']),
                '--learning_rate', str(self.llama2c_config.get('learning_rate', 5e-4)),
                '--max_iters', str(self.llama2c_config.get('max_iters', 100000)),
                '--eval_interval', str(self.llama2c_config.get('eval_interval', 2000)),
                '--eval_iters', str(self.llama2c_config.get('eval_iters', 100)),
                '--device', self.llama2c_config.get('device', 'cuda'),
                '--compile', str(self.llama2c_config.get('compile', True)).lower()
            ]
            
            # Run training
            self.log_verbose(f"Running training command: {' '.join(cmd)}")
            logger.info(f"Running training command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if self.verbose:
                self.log_verbose(f"Training stdout: {result.stdout[:500]}")
                if result.stderr:
                    self.log_verbose(f"Training stderr: {result.stderr[:500]}")
            
            if result.returncode != 0:
                logger.error(f"Training failed for {model_size}: {result.stderr}")
                return False
            
            self.log_verbose(f"Training completed successfully for {model_size}")
            logger.info(f"Training completed successfully for {model_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train {model_size} model: {e}")
            return False
    
    def train_nanogpt_model(self, model_size: str) -> bool:
        """
        Train a nanoGPT model of specified size.
        
        Args:
            model_size: Model size (15M, 42M, 110M)
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting nanoGPT training for {model_size} model")
            
            # Set model parameters based on size
            model_params = {
                '15M': {'n_layer': 6, 'n_head': 6, 'n_embd': 384},
                '42M': {'n_layer': 8, 'n_head': 8, 'n_embd': 512},
                '110M': {'n_layer': 12, 'n_head': 12, 'n_embd': 768}
            }
            
            params = model_params.get(model_size, model_params['42M'])
            
            # Build training command
            cmd = [
                'python', 'nanoGPT/train.py',
                '--batch_size', str(self.nanogpt_config.get('batch_size', 64)),
                '--block_size', str(self.nanogpt_config.get('block_size', 256)),
                '--n_layer', str(params['n_layer']),
                '--n_head', str(params['n_head']),
                '--n_embd', str(params['n_embd']),
                '--learning_rate', str(self.nanogpt_config.get('learning_rate', 3e-4)),
                '--max_iters', str(self.nanogpt_config.get('max_iters', 50000)),
                '--eval_interval', str(self.nanogpt_config.get('eval_interval', 1000)),
                '--eval_iters', str(self.nanogpt_config.get('eval_iters', 200)),
                '--device', self.nanogpt_config.get('device', 'cuda')
            ]
            
            # Run training
            logger.info(f"Running training command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Training failed for {model_size}: {result.stderr}")
                return False
            
            logger.info(f"Training completed successfully for {model_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train {model_size} model: {e}")
            return False
    
    def train_llmc_model(self, model_size: str) -> bool:
        """
        Train a llm.c model of specified size.
        
        Args:
            model_size: Model size (124M, 350M, 774M, 1558M)
            
        Returns:
            True if successful
        """
        try:
            self.log_verbose(f"Starting llm.c training for {model_size} model")
            logger.info(f"Starting llm.c training for {model_size} model")
            
            from training_pipeline.train_llmc import LLMCTrainer
            llmc_trainer = LLMCTrainer()
            
            use_gpu = self.llmc_config.get('use_gpu', True)
            self.log_verbose(f"Using GPU: {use_gpu}")
            
            result = llmc_trainer.train_model(model_size, use_gpu=use_gpu)
            
            if result.get('status') != 'success':
                logger.error(f"Training failed for {model_size}: {result.get('error')}")
                return False
            
            self.log_verbose(f"Training completed successfully for {model_size}")
            logger.info(f"Training completed successfully for {model_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train {model_size} model: {e}")
            return False
    
    def run_training_cycle(self) -> Dict[str, Any]:
        """
        Run a complete training cycle for all model sizes.
        
        Returns:
            Dictionary with training results
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'model_sizes': {},
            'success': False
        }
        
        try:
            # Check if training should be triggered
            if not self.check_training_trigger():
                logger.info("Training not triggered - insufficient new reports")
                results['message'] = 'Insufficient new reports for training'
                return results
            
            # Prepare data for llama2.c and nanoGPT
            if not self.prepare_data():
                logger.error("Data preparation failed, aborting training")
                results['error'] = 'Data preparation failed'
                return results
            
            # Prepare data for llm.c
            try:
                from training_pipeline.prepare_llmc import LLMCDataPreparer
                llmc_preparer = LLMCDataPreparer()
                llmc_preparer.prepare()
                logger.info("llm.c data preparation completed")
            except Exception as e:
                logger.warning(f"llm.c data preparation failed (continuing with other models): {e}")
            
            # Train llama2.c models
            llama2c_results = {}
            for model_size in self.model_sizes:
                success = self.train_llama2c_model(model_size)
                llama2c_results[model_size] = 'success' if success else 'failed'
            
            results['model_sizes']['llama2c'] = llama2c_results
            
            # Train GPT-2 models
            from training_pipeline.train_gpt2 import GPT2Trainer
            gpt2_trainer = GPT2Trainer()
            gpt2_results = {}
            for model_size in self.gpt2_model_sizes:
                success = gpt2_trainer.train_model(model_size)
                gpt2_results[model_size] = success.get('status', 'failed')
            
            results['model_sizes']['gpt2'] = gpt2_results
            
            # Train llm.c models
            llmc_results = {}
            for model_size in self.llmc_model_sizes:
                success = self.train_llmc_model(model_size)
                llmc_results[model_size] = 'success' if success else 'failed'
            
            results['model_sizes']['llmc'] = llmc_results
            
            # Train nanoGPT models (optional - comment out if not needed)
            # nanogpt_results = {}
            # for model_size in self.model_sizes:
            #     success = self.train_nanogpt_model(model_size)
            #     nanogpt_results[model_size] = 'success' if success else 'failed'
            # 
            # results['model_sizes']['nanogpt'] = nanogpt_results
            
            # Check if all training succeeded
            all_success = all(status == 'success' for status in llama2c_results.values())
            results['success'] = all_success
            
            self.last_training_time = datetime.utcnow()
            
            # Evaluate models
            logger.info("Evaluating trained models...")
            test_prompts = [
                "Program: example.com\nReport title: XSS vulnerability",
                "Analyze the domain: test.com for potential issues"
            ]
            
            # Evaluate llama2.c models
            for model_size in self.model_sizes:
                model_name = f"llama2c_{model_size}"
                self.evaluator.evaluate_model(model_name, 'llama2c', test_prompts)
            
            # Evaluate GPT-2 models
            for model_size in self.gpt2_model_sizes:
                model_name = f"gpt2_{model_size}"
                self.evaluator.evaluate_model(model_name, 'gpt2', test_prompts)
            
            # Evaluate llm.c models
            for model_size in self.llmc_model_sizes:
                model_name = f"llmc_{model_size}"
                self.evaluator.evaluate_model(model_name, 'llmc', test_prompts)
            
            # Generate comparison report
            all_models = []
            all_models.extend([f"llama2c_{size}" for size in self.model_sizes])
            all_models.extend([f"gpt2_{size}" for size in self.gpt2_model_sizes])
            all_models.extend([f"llmc_{size}" for size in self.llmc_model_sizes])
            
            comparison = self.evaluator.compare_models(all_models)
            logger.info(f"Model comparison: {comparison['ranking']}")
            
            # Generate evaluation report
            report = self.evaluator.generate_report()
            logger.info("Evaluation report generated")
            
            logger.info(f"Training cycle completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Training cycle failed: {e}")
            results['error'] = str(e)
            return results


async def run_scheduler():
    """Run the training scheduler loop."""
    import argparse
    parser = argparse.ArgumentParser(description='Run training scheduler')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()
    
    scheduler = TrainingScheduler(verbose=args.verbose)
    
    logger.info("Starting training scheduler")
    
    # Initial report count
    scheduler.last_report_count = scheduler.db_manager.get_report_count()
    logger.info(f"Initial report count: {scheduler.last_report_count}")
    
    # Run one training cycle immediately
    results = scheduler.run_training_cycle()
    logger.info(f"Initial training cycle: {results}")
    
    # TODO: Add periodic scheduling here
    # For now, just run once and exit


if __name__ == '__main__':
    asyncio.run(run_scheduler())
