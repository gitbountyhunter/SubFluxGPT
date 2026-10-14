"""
Continuous Learning Orchestrator
Automatically collects bug bounty reports and retrains models
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime
from typing import Dict, Any
import yaml

from data_collector.main import DataCollectionCoordinator
from training_pipeline.scheduler import TrainingScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContinuousLearningOrchestrator:
    """
    Orchestrates continuous data collection and model training.
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the orchestrator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize data collection coordinator
        self.data_coordinator = DataCollectionCoordinator(config_path)
        
        # Initialize training scheduler
        self.training_scheduler = TrainingScheduler(config_path, verbose=True)
        
        # Get intervals from config
        self.collection_interval = self.config.get('data_collection', {}).get('collection_interval', 3600)  # 1 hour
        self.training_trigger_reports = self.config.get('training', {}).get('min_new_reports', 1000)
        
        # State tracking
        self.last_collection_time = None
        self.last_training_time = None
        self.running = False
        
        logger.info("Initialized ContinuousLearningOrchestrator")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    async def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from all platforms.
        
        Returns:
            Collection statistics
        """
        logger.info("Starting data collection cycle")
        
        try:
            results = await self.data_coordinator.collect_from_all_platforms()
            self.last_collection_time = datetime.utcnow()
            
            logger.info(f"Data collection completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def check_training_trigger(self) -> bool:
        """
        Check if training should be triggered.
        
        Returns:
            True if enough new reports for training
        """
        try:
            return self.training_scheduler.check_training_trigger()
        except Exception as e:
            logger.error(f"Failed to check training trigger: {e}")
            return False
    
    async def run_training_cycle(self) -> Dict[str, Any]:
        """
        Run a full training cycle.
        
        Returns:
            Training results
        """
        logger.info("Starting training cycle")
        
        try:
            results = self.training_scheduler.run_training_cycle()
            self.last_training_time = datetime.utcnow()
            
            logger.info(f"Training cycle completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Training cycle failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_collection_cycle(self):
        """
        Run a single collection cycle.
        """
        logger.info("=" * 60)
        logger.info("CONTINUOUS LEARNING - Data Collection Cycle")
        logger.info("=" * 60)
        
        # Collect data
        results = await self.collect_data()
        
        # Check if training should be triggered
        if self.check_training_trigger():
            logger.info("Training trigger threshold reached - starting training cycle")
            await self.run_training_cycle()
        else:
            logger.info("Training threshold not reached - skipping training")
        
        # Print status
        self.print_status()
    
    def print_status(self):
        """Print current system status."""
        logger.info("=" * 60)
        logger.info("CONTINUOUS LEARNING STATUS")
        logger.info("=" * 60)
        
        try:
            stats = self.data_coordinator.get_statistics()
            logger.info(f"Database Statistics: {stats}")
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
        
        logger.info(f"Last Collection: {self.last_collection_time}")
        logger.info(f"Last Training: {self.last_training_time}")
        logger.info(f"Collection Interval: {self.collection_interval}s")
        logger.info(f"Training Trigger: {self.training_trigger_reports} reports")
        logger.info(f"Running: {self.running}")
        logger.info("=" * 60)
    
    def start(self):
        """Start the continuous learning loop."""
        logger.info("Starting continuous learning orchestrator")
        self.running = True
        
        # Schedule data collection
        schedule.every(self.collection_interval).seconds.do(
            lambda: asyncio.create_task(self.run_collection_cycle())
        )
        
        # Run immediately once
        asyncio.create_task(self.run_collection_cycle())
        
        # Keep loop running
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the continuous learning loop."""
        logger.info("Stopping continuous learning orchestrator")
        self.running = False


async def main():
    """Main entry point for continuous learning."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run continuous learning orchestrator')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()
    
    orchestrator = ContinuousLearningOrchestrator(args.config)
    
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    if args.once:
        # Run once and exit
        await orchestrator.run_collection_cycle()
    else:
        # Run continuous loop
        orchestrator.start()


if __name__ == '__main__':
    asyncio.run(main())
