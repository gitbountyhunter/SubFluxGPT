"""
GPT-2 training module for SubFluxGPT.
Trains GPT-2 models on bug bounty data using HuggingFace Transformers.
"""

import os
import logging
import yaml
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling, Trainer, TrainingArguments

logger = logging.getLogger(__name__)


class GPT2Trainer:
    """Trainer for GPT-2 models on bug bounty data."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize GPT-2 trainer.

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
        
        self.training_config = self.config.get('training', {})
        self.gpt2_config = self.training_config.get('gpt2', {})
        
        # Model sizes and their corresponding GPT-2 architectures
        self.model_sizes = {
            '124M': 'gpt2',         # Small
            '355M': 'gpt2-medium',   # Medium
            '774M': 'gpt2-large',   # Large
            '1558M': 'gpt2-xl'      # Extra Large
        }
        
        logger.info("Initialized GPT2Trainer")
    
    def prepare_tokenizer(self, vocab_size: int = 50257):
        """
        Initialize GPT-2 tokenizer.
        
        Args:
            vocab_size: Vocabulary size (default GPT-2 uses 50257)
            
        Returns:
            GPT2Tokenizer instance
        """
        # Use GPT-2 tokenizer
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        
        logger.info(f"Initialized GPT-2 tokenizer with vocab size: {len(tokenizer)}")
        return tokenizer
    
    def prepare_dataset(self, tokenizer, train_file: str, val_file: str, block_size: int = 512):
        """
        Prepare datasets for training.
        
        Args:
            tokenizer: GPT2Tokenizer instance
            train_file: Path to training data file
            val_file: Path to validation data file
            block_size: Maximum sequence length
            
        Returns:
            Tuple of (train_dataset, val_dataset)
        """
        train_dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=train_file,
            block_size=block_size
        )
        
        val_dataset = TextDataset(
            tokenizer=tokenizer,
            file_path=val_file,
            block_size=block_size
        )
        
        logger.info(f"Prepared datasets - Train: {len(train_dataset)}, Val: {len(val_dataset)}")
        return train_dataset, val_dataset
    
    def train_model(self, model_size: str = '124M', output_dir: str = './models/gpt2'):
        """
        Train a GPT-2 model.
        
        Args:
            model_size: Model size (124M, 355M, 774M, 1558M)
            output_dir: Directory to save model checkpoints
            
        Returns:
            Training results
        """
        try:
            # Get model architecture
            model_name = self.model_sizes.get(model_size, 'gpt2')
            
            logger.info(f"Training GPT-2 model: {model_name} ({model_size})")
            
            # Initialize tokenizer
            tokenizer = self.prepare_tokenizer()
            
            # Prepare datasets
            train_file = self.gpt2_config.get('train_file', 'data/bugbounty_tokens/train.txt')
            val_file = self.gpt2_config.get('val_file', 'data/bugbounty_tokens/val.txt')
            
            # Convert .bin files to text if needed
            self._convert_bin_to_text_if_needed(train_file, 'train')
            self._convert_bin_to_text_if_needed(val_file, 'val')
            
            block_size = self.gpt2_config.get('block_size', 512)
            train_dataset, val_dataset = self.prepare_dataset(tokenizer, train_file, val_file, block_size)
            
            # Initialize model
            model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                overwrite_output_dir=True,
                num_train_epochs=self.gpt2_config.get('num_train_epochs', 3),
                per_device_train_batch_size=self.gpt2_config.get('batch_size', 4),
                per_device_eval_batch_size=self.gpt2_config.get('batch_size', 4),
                gradient_accumulation_steps=self.gpt2_config.get('gradient_accumulation_steps', 4),
                learning_rate=self.gpt2_config.get('learning_rate', 5e-5),
                weight_decay=self.gpt2_config.get('weight_decay', 0.01),
                warmup_steps=self.gpt2_config.get('warmup_steps', 500),
                logging_steps=self.gpt2_config.get('logging_steps', 100),
                save_steps=self.gpt2_config.get('save_steps', 1000),
                eval_steps=self.gpt2_config.get('eval_steps', 1000),
                save_total_limit=self.gpt2_config.get('save_total_limit', 3),
                fp16=self.gpt2_config.get('fp16', torch.cuda.is_available()),
                evaluation_strategy='steps',
                load_best_model_at_end=True,
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
            )
            
            # Train
            logger.info("Starting training...")
            trainer.train()
            
            # Save final model
            trainer.save_model(output_dir)
            tokenizer.save_pretrained(output_dir)
            
            logger.info(f"Training completed. Model saved to {output_dir}")
            
            return {
                'status': 'success',
                'model_size': model_size,
                'output_dir': output_dir
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _convert_bin_to_text_if_needed(self, file_path: str, split_name: str):
        """
        Convert .bin token files to text if they don't exist as text.
        
        Args:
            file_path: Path to text file
            split_name: Name of split (train/val)
        """
        import numpy as np
        from data_collector.database_manager import DatabaseManager
        
        # If text file doesn't exist, create it from database
        if not os.path.exists(file_path):
            logger.info(f"Creating {file_path} from database")
            
            # Get reports from database
            db_url = self.config['database']['url']
            db_manager = DatabaseManager(db_url)
            
            reports = db_manager.get_reports_for_training()
            
            # Format as text
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for report in reports:
                    f.write(report['raw_content'] + '\n\n')
            
            logger.info(f"Created {file_path} with {len(reports)} reports")


def main():
    """Main entry point for GPT-2 training."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_size', type=str, default='124M', choices=['124M', '355M', '774M', '1558M'])
    parser.add_argument('--output_dir', type=str, default='./models/gpt2')
    args = parser.parse_args()
    
    trainer = GPT2Trainer()
    results = trainer.train_model(args.model_size, args.output_dir)
    
    print(f"Training results: {results}")


if __name__ == '__main__':
    main()
