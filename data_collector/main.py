"""
Main data collection coordinator.
Orchestrates data collection from multiple platforms.
"""

import asyncio
import logging
import yaml
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from data_collector.collectors.hackerone import HackerOneCollector
from data_collector.collectors.bugcrowd import BugcrowdCollector
from data_collector.collectors.yeswehack import YesWeHackCollector
from data_collector.database_manager import DatabaseManager
from domain_processor.domain_extractor import DomainExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCollectionCoordinator:
    """Coordinates data collection from multiple platforms."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the coordinator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize database
        db_url = self.config['database']['url']
        self.db_manager = DatabaseManager(db_url)
        self.db_manager.create_tables()
        
        # Initialize domain extractor
        domain_config = self.config.get('domain_processing', {})
        self.domain_extractor = DomainExtractor(domain_config)
        
        # Initialize collectors
        self.collectors = self._initialize_collectors()
        
        logger.info("Initialized DataCollectionCoordinator")
    
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
    
    def _initialize_collectors(self) -> Dict[str, Any]:
        """Initialize enabled platform collectors."""
        collectors = {}
        platforms_config = self.config.get('platforms', {})
        
        # HackerOne
        if platforms_config.get('hackerone', {}).get('enabled', False):
            collectors['hackerone'] = HackerOneCollector(
                platforms_config['hackerone']
            )
        
        # Bugcrowd
        if platforms_config.get('bugcrowd', {}).get('enabled', False):
            collectors['bugcrowd'] = BugcrowdCollector(
                platforms_config['bugcrowd']
            )
        
        # YesWeHack
        if platforms_config.get('yeswehack', {}).get('enabled', False):
            collectors['yeswehack'] = YesWeHackCollector(
                platforms_config['yeswehack']
            )
        
        logger.info(f"Initialized {len(collectors)} collectors: {list(collectors.keys())}")
        return collectors
    
    async def collect_from_platform(self, platform_name: str) -> Dict[str, Any]:
        """
        Collect data from a specific platform.
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            Collection statistics
        """
        if platform_name not in self.collectors:
            logger.error(f"Collector for {platform_name} not found")
            return {'platform': platform_name, 'status': 'failed', 'error': 'Collector not found'}
        
        collector = self.collectors[platform_name]
        
        try:
            logger.info(f"Starting collection for {platform_name}")
            
            # Collect reports
            reports = await collector.collect_all_reports()
            
            # Store reports in database
            stored_count = 0
            for report in reports:
                try:
                    self.db_manager.upsert_report(report)
                    stored_count += 1
                except Exception as e:
                    logger.warning(f"Failed to store report {report.platform_report_id}: {e}")
            
            # Extract domains from reports
            domains_processed = 0
            for report in reports:
                if report.raw_content:
                    extracted_domains = self.domain_extractor.extract_domains(report.raw_content)
                    
                    for extracted in extracted_domains:
                        try:
                            self.db_manager.upsert_domain(
                                extracted.domain,
                                extracted.apex_domain,
                                extracted.tld
                            )
                            domains_processed += 1
                        except Exception as e:
                            logger.warning(f"Failed to store domain {extracted.domain}: {e}")
            
            stats = {
                'platform': platform_name,
                'status': 'completed',
                'reports_collected': len(reports),
                'reports_stored': stored_count,
                'domains_extracted': domains_processed,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Collection completed for {platform_name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Collection failed for {platform_name}: {e}")
            return {
                'platform': platform_name,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def collect_from_all_platforms(self) -> Dict[str, Any]:
        """
        Collect data from all enabled platforms in parallel.
        
        Returns:
            Dictionary with collection statistics for each platform
        """
        logger.info("Starting collection from all platforms")
        
        # Run collections in parallel
        tasks = [
            self.collect_from_platform(platform_name)
            for platform_name in self.collectors.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        aggregated = {
            'total_reports': 0,
            'total_domains': 0,
            'platforms': {}
        }
        
        for platform_name, result in zip(self.collectors.keys(), results):
            if isinstance(result, Exception):
                aggregated['platforms'][platform_name] = {
                    'status': 'failed',
                    'error': str(result)
                }
            else:
                aggregated['platforms'][platform_name] = result
                if result.get('status') == 'completed':
                    aggregated['total_reports'] += result.get('reports_stored', 0)
                    aggregated['total_domains'] += result.get('domains_extracted', 0)
        
        logger.info(f"Collection from all platforms completed: {aggregated}")
        return aggregated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current database statistics."""
        return {
            'total_reports': self.db_manager.get_report_count(),
            'total_domains': self.db_manager.get_domain_count(),
            'reports_by_platform': {
                'hackerone': self.db_manager.get_report_count('hackerone'),
                'bugcrowd': self.db_manager.get_report_count('bugcrowd'),
                'yeswehack': self.db_manager.get_report_count('yeswehack')
            }
        }


async def main():
    """Main entry point for data collection."""
    coordinator = DataCollectionCoordinator()
    
    # Print current statistics
    stats = coordinator.get_statistics()
    logger.info(f"Current database statistics: {stats}")
    
    # Collect from all platforms
    results = await coordinator.collect_from_all_platforms()
    logger.info(f"Collection results: {results}")
    
    # Print updated statistics
    stats = coordinator.get_statistics()
    logger.info(f"Updated database statistics: {stats}")


if __name__ == '__main__':
    asyncio.run(main())
