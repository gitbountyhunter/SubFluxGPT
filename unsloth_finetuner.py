#!/usr/bin/env python3
"""
Unsloth/QLoRA Fine-Tuner
Efficient fine-tuning of mini LLMs for bug bounty reconnaissance
Uses QLoRA (Quantized Low-Rank Adaptation) for memory-efficient training
"""

import logging
import json
import torch
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnslothFineTuner:
    """Fine-tuner using Unsloth/QLoRA"""

    def __init__(self, base_model: str = 'gpt2',
                 output_dir: str = 'models/finetuned'):
        """
        Initialize fine-tuner

        Args:
            base_model: Base model to fine-tune
            output_dir: Directory to save fine-tuned models
        """
        self.base_model = base_model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check if Unsloth is available
        self.unsloth_available = self._check_unsloth()

        if not self.unsloth_available:
            logger.warning("Unsloth not available, will use alternative fine-tuning")

    def _check_unsloth(self) -> bool:
        """Check if Unsloth is available"""
        try:
            import unsloth
            logger.info("Unsloth is available")
            return True
        except ImportError:
            logger.info("Unsloth not installed, install with: pip install unsloth")
            return False

    def finetune_qlora(self,
                      dataset_path: str,
                      model_size: str = '124M',
                      epochs: int = 3,
                      batch_size: int = 4,
                      learning_rate: float = 2e-4,
                      use_gpu: bool = True) -> Dict[str, Any]:
        """
        Fine-tune model using QLoRA

        Args:
            dataset_path: Path to training dataset
            model_size: Model size
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            use_gpu: Use GPU if available

        Returns:
            Training results
        """
        logger.info(f"Starting QLoRA fine-tuning of {model_size} model")

        if self.unsloth_available:
            return self._finetune_with_unsloth(
                dataset_path, model_size, epochs, batch_size, learning_rate, use_gpu
            )
        else:
            return self._finetune_fallback(
                dataset_path, model_size, epochs, batch_size, learning_rate
            )

    def _finetune_with_unsloth(self,
                              dataset_path: str,
                              model_size: str,
                              epochs: int,
                              batch_size: int,
                              learning_rate: float,
                              use_gpu: bool) -> Dict[str, Any]:
        """Fine-tune using Unsloth"""
        try:
            from unsloth import FastLanguageModel
            from transformers import TrainingArguments
            from trl import SFTTrainer
            from datasets import load_from_disk

            logger.info("Loading model with Unsloth...")

            # Load base model
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.base_model,
                max_seq_length=2048,
                dtype=None,
                load_in_4bit=True
            )

            # Configure LoRA
            model = FastLanguageModel.get_peft_model(
                model,
                r=16,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                              "gate_proj", "up_proj", "down_proj"],
                lora_alpha=16,
                lora_dropout=0,
                bias="none",
                use_gradient_checkpointing=True,
                random_state=3407,
                use_rslora=False,
                loftq_config=None
            )

            # Load dataset
            logger.info(f"Loading dataset from {dataset_path}")
            dataset = load_from_disk(dataset_path)

            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(self.output_dir),
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=4,
                learning_rate=learning_rate,
                weight_decay=0.01,
                logging_steps=10,
                save_steps=100,
                fp16=use_gpu,
                bf16=False,
                max_grad_norm=0.3,
                warmup_ratio=0.03,
                lr_scheduler_type="cosine",
                report_to="none"
            )

            # Trainer
            trainer = SFTTrainer(
                model=model,
                tokenizer=tokenizer,
                train_dataset=dataset,
                dataset_text_field="text",
                max_seq_length=2048,
                args=training_args
            )

            # Train
            logger.info("Starting training...")
            trainer.train()

            # Save model
            output_path = self.output_dir / f"finetuned_{model_size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model.save_pretrained(str(output_path))
            tokenizer.save_pretrained(str(output_path))

            logger.info(f"Model saved to {output_path}")

            return {
                'success': True,
                'output_path': str(output_path),
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate
            }

        except Exception as e:
            logger.error(f"Unsloth fine-tuning failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _finetune_fallback(self,
                          dataset_path: str,
                          model_size: str,
                          epochs: int,
                          batch_size: int,
                          learning_rate: float) -> Dict[str, Any]:
        """Fallback fine-tuning without Unsloth"""
        try:
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                TrainingArguments,
                Trainer,
                DataCollatorForLanguageModeling
            )
            from peft import LoraConfig, get_peft_model, TaskType
            from datasets import load_from_disk

            logger.info("Using fallback fine-tuning with PEFT/LoRA")

            # Load model and tokenizer
            logger.info(f"Loading model: {self.base_model}")
            model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            tokenizer.pad_token = tokenizer.eos_token

            # Configure LoRA
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["q_proj", "v_proj"]
            )

            model = get_peft_model(model, peft_config)
            model.print_trainable_parameters()

            # Load dataset
            logger.info(f"Loading dataset from {dataset_path}")
            dataset = load_from_disk(dataset_path)

            # Tokenize dataset
            def tokenize_function(examples):
                return tokenizer(
                    examples["text"],
                    truncation=True,
                    max_length=512,
                    padding="max_length"
                )

            tokenized_dataset = dataset.map(tokenize_function, batched=True)

            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(self.output_dir),
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=4,
                learning_rate=learning_rate,
                weight_decay=0.01,
                logging_steps=10,
                save_steps=100,
                fp16=True,
                max_grad_norm=0.3,
                warmup_ratio=0.03,
                lr_scheduler_type="cosine",
                report_to="none"
            )

            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )

            # Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator
            )

            # Train
            logger.info("Starting training...")
            trainer.train()

            # Save model
            output_path = self.output_dir / f"finetuned_{model_size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model.save_pretrained(str(output_path))
            tokenizer.save_pretrained(str(output_path))

            logger.info(f"Model saved to {output_path}")

            return {
                'success': True,
                'output_path': str(output_path),
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate
            }

        except Exception as e:
            logger.error(f"Fallback fine-tuning failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def prepare_bugbounty_dataset(self,
                                   learning_db_path: str = 'data/learning/learning.db',
                                   output_path: str = 'data/datasets/bugbounty_finetune') -> Dict[str, Any]:
        """
        Prepare bug bounty dataset for fine-tuning

        Args:
            learning_db_path: Path to learning database
            output_path: Path to save prepared dataset

        Returns:
            Dataset preparation results
        """
        try:
            from ai_integration.continuous_learner import ContinuousLearner
            from datasets import Dataset

            logger.info("Preparing bug bounty dataset...")

            # Load learning data
            learner = ContinuousLearner(db_path=learning_db_path)
            training_data = learner.get_training_data(limit=10000)

            # Convert to training format
            texts = []
            for item in training_data:
                # Create training examples
                text = f"Command: {item['command']}\n"
                text += f"Success: {item['success']}\n"
                text += f"Exit Code: {item['exit_code']}\n"
                texts.append(text)

            # Create dataset
            dataset = Dataset.from_dict({"text": texts})

            # Save dataset
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            dataset.save_to_disk(str(output_path))

            logger.info(f"Dataset saved to {output_path}")
            logger.info(f"Total examples: {len(texts)}")

            return {
                'success': True,
                'output_path': str(output_path),
                'num_examples': len(texts)
            }

        except Exception as e:
            logger.error(f"Dataset preparation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def evaluate_model(self, model_path: str,
                      test_dataset_path: str) -> Dict[str, Any]:
        """
        Evaluate fine-tuned model

        Args:
            model_path: Path to fine-tuned model
            test_dataset_path: Path to test dataset

        Returns:
            Evaluation results
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from datasets import load_from_disk
            import numpy as np

            logger.info(f"Evaluating model: {model_path}")

            # Load model
            model = AutoModelForCausalLM.from_pretrained(model_path)
            tokenizer = AutoTokenizer.from_pretrained(model_path)

            # Load test dataset
            test_dataset = load_from_disk(test_dataset_path)

            # Simple evaluation: perplexity
            total_loss = 0
            total_count = 0

            for item in test_dataset:
                inputs = tokenizer(item['text'], return_tensors='pt', truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = model(**inputs, labels=inputs['input_ids'])
                    loss = outputs.loss
                    total_loss += loss.item()
                    total_count += 1

            avg_loss = total_loss / total_count
            perplexity = np.exp(avg_loss)

            logger.info(f"Average loss: {avg_loss:.4f}")
            logger.info(f"Perplexity: {perplexity:.4f}")

            return {
                'success': True,
                'avg_loss': avg_loss,
                'perplexity': perplexity,
                'num_samples': total_count
            }

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Unsloth/QLoRA Fine-Tuner')
    parser.add_argument('--prepare-dataset', action='store_true',
                       help='Prepare bug bounty dataset')
    parser.add_argument('--finetune', action='store_true',
                       help='Run fine-tuning')
    parser.add_argument('--evaluate', type=str,
                       help='Evaluate model at path')
    parser.add_argument('--dataset', type=str,
                       help='Dataset path')
    parser.add_argument('--model-size', type=str, default='124M',
                       help='Model size')
    parser.add_argument('--epochs', type=int, default=3,
                       help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-4,
                       help='Learning rate')
    parser.add_argument('--use-gpu', action='store_true',
                       help='Use GPU')

    args = parser.parse_args()

    tuner = UnslothFineTuner()

    if args.prepare_dataset:
        result = tuner.prepare_bugbounty_dataset()
        print(json.dumps(result, indent=2))

    elif args.finetune:
        if not args.dataset:
            print("Error: --dataset required for fine-tuning")
            return

        result = tuner.finetune_qlora(
            dataset_path=args.dataset,
            model_size=args.model_size,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            use_gpu=args.use_gpu
        )
        print(json.dumps(result, indent=2))

    elif args.evaluate:
        result = tuner.evaluate_model(args.evaluate, args.dataset)
        print(json.dumps(result, indent=2))

    else:
        print("No action specified. Use --prepare-dataset, --finetune, or --evaluate")


if __name__ == '__main__':
    main()
