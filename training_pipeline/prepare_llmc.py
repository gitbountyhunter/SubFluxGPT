"""
Prepare bug bounty data for llm.c training.
Converts database reports to llm.c .bin format with GPT-2 tokenization.
"""

import os
import sys
import logging
import argparse
import yaml
import numpy as np
import tiktoken
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collector.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


# llm.c header format for GPT-2
HEADERS_INFO = {
    "gpt-2": {
        "magic": 20240520,
        "version": 1,
        "token_dtype": np.uint16,
    },
}


def write_datafile(filename, toks, model_desc="gpt-2"):
    """
    Saves token data as a .bin file, for reading in C.
    - First comes a header with 256 int32s
    - The tokens follow, each as uint16 (gpt-2) or uint32 (llama)
    """
    assert len(toks) < 2**31, "token count too large" # ~2.1B tokens
    assert model_desc in ["gpt-2"], f"unknown model descriptor {model_desc}"
    info = HEADERS_INFO[model_desc]
    # construct the header
    header = np.zeros(256, dtype=np.int32) # header is always 256 int32 values
    header[0] = info["magic"]
    header[1] = info["version"]
    header[2] = len(toks) # number of tokens after the 256*4 bytes of header
    # construct the data (numpy array of tokens)
    toks_np = np.array(toks, dtype=info["token_dtype"])
    # write to file
    num_bytes = (256 * 4) + (len(toks) * toks_np.itemsize)
    logger.info(f"writing {len(toks):,} tokens to {filename} ({num_bytes:,} bytes) in the {model_desc} format")
    with open(filename, "wb") as f:
        f.write(header.tobytes())
        f.write(toks_np.tobytes())


class LLMCDataPreparer:
    """Prepares bug bounty data for llm.c training."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the data preparer.
        
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
        
        # Initialize database
        db_url = self.config['database']['url']
        self.db_manager = DatabaseManager(db_url)
        
        # GPT-2 tokenizer
        self.enc = tiktoken.get_encoding("gpt2")
        self.eot = self.enc._special_tokens['']  # end of text token
        
        # Output directory
        self.output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'llmc'
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Initialized LLMCDataPreparer")
    
    def fetch_reports(self, limit: int = None) -> list:
        """
        Fetch bug bounty reports from database.
        
        Args:
            limit: Maximum number of reports to fetch
            
        Returns:
            List of report dictionaries
        """
        try:
            reports = self.db_manager.get_reports_for_training(limit=limit)
            logger.info(f"Fetched {len(reports)} reports from database")
            return reports
        except Exception as e:
            logger.error(f"Failed to fetch reports: {e}")
            raise
    
    def tokenize_reports(self, reports: list) -> list:
        """
        Tokenize bug bounty reports using GPT-2 tokenizer.
        
        Args:
            reports: List of report dictionaries
            
        Returns:
            List of token IDs
        """
        tokens = []
        
        for i, report in enumerate(reports):
            # Add EOT token at start of each report
            tokens.append(self.eot)
            
            # Format report as text
            # Include relevant fields for cybersecurity context
            text_parts = []
            
            if report.get('program'):
                text_parts.append(f"Program: {report['program']}")
            
            if report.get('title'):
                text_parts.append(f"Report title: {report['title']}")
            
            if report.get('vulnerability_type'):
                text_parts.append(f"Vulnerability type: {report['vulnerability_type']}")
            
            if report.get('severity'):
                text_parts.append(f"Severity: {report['severity']}")
            
            if report.get('description'):
                text_parts.append(f"Description: {report['description']}")
            
            if report.get('raw_content'):
                text_parts.append(f"Content: {report['raw_content']}")
            
            # Join and tokenize
            text = '\n'.join(text_parts) + '\n\n'
            encoded = self.enc.encode_ordinary(text)
            tokens.extend(encoded)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Tokenized {i + 1}/{len(reports)} reports")
        
        logger.info(f"Total tokens: {len(tokens):,}")
        return tokens
    
    def split_and_save(self, tokens: list, val_split: float = 0.1):
        """
        Split tokens into train/val and save to .bin files.
        
        Args:
            tokens: List of token IDs
            val_split: Fraction of tokens for validation (default 10%)
        """
        # Calculate split point
        split_idx = int(len(tokens) * (1 - val_split))
        
        val_tokens = tokens[:split_idx]
        train_tokens = tokens[split_idx:]
        
        logger.info(f"Train tokens: {len(train_tokens):,}")
        logger.info(f"Val tokens: {len(val_tokens):,}")
        
        # Save to files
        val_filename = os.path.join(self.output_dir, "bugbounty_val.bin")
        train_filename = os.path.join(self.output_dir, "bugbounty_train.bin")
        
        write_datafile(val_filename, val_tokens, model_desc="gpt-2")
        write_datafile(train_filename, train_tokens, model_desc="gpt-2")
        
        logger.info(f"Saved train/val files to {self.output_dir}")
        
        return {
            'train_file': train_filename,
            'val_file': val_filename,
            'train_tokens': len(train_tokens),
            'val_tokens': len(val_tokens)
        }
    
    def prepare(self, limit: int = None, val_split: float = 0.1):
        """
        Complete preparation pipeline.
        
        Args:
            limit: Maximum number of reports to process
            val_split: Validation split fraction
            
        Returns:
            Dictionary with file paths and token counts
        """
        try:
            logger.info("Starting llm.c data preparation...")
            
            # Fetch reports
            reports = self.fetch_reports(limit=limit)
            
            if not reports:
                logger.warning("No reports found in database")
                return None
            
            # Tokenize
            tokens = self.tokenize_reports(reports)
            
            # Split and save
            result = self.split_and_save(tokens, val_split=val_split)
            
            logger.info("llm.c data preparation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Data preparation failed: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Prepare bug bounty data for llm.c training")
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--limit', type=int, default=None, help='Max number of reports to process')
    parser.add_argument('--val_split', type=float, default=0.1, help='Validation split fraction')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    preparer = LLMCDataPreparer(config_path=args.config)
    result = preparer.prepare(limit=args.limit, val_split=args.val_split)
    
    if result:
        print(f"\nPreparation complete:")
        print(f"  Train file: {result['train_file']}")
        print(f"  Val file: {result['val_file']}")
        print(f"  Train tokens: {result['train_tokens']:,}")
        print(f"  Val tokens: {result['val_tokens']:,}")
    else:
        print("No data prepared - check database has reports")


if __name__ == '__main__':
    main()
