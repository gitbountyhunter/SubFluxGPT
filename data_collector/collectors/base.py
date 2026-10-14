"""
Base collector class for bug bounty platforms.
All platform-specific collectors should inherit from this.
"""

import abc
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Report:
    """Data class representing a bug bounty report."""
    platform: str
    platform_report_id: str
    program_id: str
    program_name: str
    title: str
    weakness: Optional[str] = None
    severity: Optional[str] = None
    reporter: Optional[str] = None
    bounty_amount: Optional[float] = None
    disclosed_at: Optional[datetime] = None
    url: Optional[str] = None
    raw_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Program:
    """Data class representing a bug bounty program."""
    platform: str
    program_id: str
    name: str
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseCollector(abc.ABC):
    """
    Abstract base class for bug bounty platform collectors.
    
    All platform-specific collectors should:
    1. Inherit from this class
    2. Implement the abstract methods
    3. Respect rate limiting
    4. Handle errors gracefully
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the collector with configuration.
        
        Args:
            config: Dictionary containing platform-specific configuration
        """
        self.config = config
        self.platform_name = self.__class__.__name__.replace('Collector', '').lower()
        self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 5)
        
        logger.info(f"Initialized {self.platform_name} collector")
    
    @abc.abstractmethod
    async def collect_programs(self) -> List[Program]:
        """
        Collect all programs from the platform.
        
        Returns:
            List of Program objects
        """
        pass
    
    @abc.abstractmethod
    async def collect_reports(self, program_id: str, limit: Optional[int] = None) -> List[Report]:
        """
        Collect reports for a specific program.
        
        Args:
            program_id: Platform-specific program ID
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        pass
    
    @abc.abstractmethod
    async def collect_all_reports(self, limit: Optional[int] = None) -> List[Report]:
        """
        Collect all disclosed reports from the platform.
        
        Args:
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        pass
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        await asyncio.sleep(self.rate_limit_delay)
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Async function to retry
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_attempts} failed for {func.__name__}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
        
        logger.error(f"All {self.retry_attempts} attempts failed for {func.__name__}")
        raise last_exception
    
    def normalize_report(self, report: Report) -> Report:
        """
        Normalize report data to standard format.
        
        Args:
            report: Report object to normalize
            
        Returns:
            Normalized Report object
        """
        # Ensure platform name is set
        if not report.platform:
            report.platform = self.platform_name
        
        # Normalize whitespace in title
        if report.title:
            report.title = ' '.join(report.title.split())
        
        # Normalize weakness name
        if report.weakness:
            report.weakness = ' '.join(report.weakness.split())
        
        return report
    
    def validate_report(self, report: Report) -> bool:
        """
        Validate that a report has required fields.
        
        Args:
            report: Report object to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not report.platform_report_id:
            logger.warning(f"Report missing platform_report_id: {report.title}")
            return False
        
        if not report.title:
            logger.warning(f"Report missing title: {report.platform_report_id}")
            return False
        
        if not report.program_id:
            logger.warning(f"Report missing program_id: {report.platform_report_id}")
            return False
        
        return True
    
    async def collect_incremental(self, last_collected: Optional[datetime] = None) -> List[Report]:
        """
        Collect reports since a given timestamp.
        
        Args:
            last_collected: Only collect reports after this timestamp
            
        Returns:
            List of new Report objects
        """
        logger.info(f"Collecting incremental reports since {last_collected}")
        
        all_reports = await self.collect_all_reports()
        
        if last_collected:
            new_reports = [
                r for r in all_reports
                if r.disclosed_at and r.disclosed_at > last_collected
            ]
            logger.info(f"Found {len(new_reports)} new reports since {last_collected}")
            return new_reports
        
        return all_reports
    
    async def run_collection(self) -> Dict[str, Any]:
        """
        Run a full collection cycle.
        
        Returns:
            Dictionary with collection statistics
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting collection for {self.platform_name}")
            
            # Collect programs
            programs = await self.collect_programs()
            logger.info(f"Collected {len(programs)} programs")
            
            # Collect reports
            reports = await self.collect_all_reports()
            
            # Validate and normalize reports
            valid_reports = []
            for report in reports:
                report = self.normalize_report(report)
                if self.validate_report(report):
                    valid_reports.append(report)
            
            logger.info(f"Collected {len(valid_reports)} valid reports")
            
            stats = {
                'platform': self.platform_name,
                'status': 'completed',
                'programs_collected': len(programs),
                'reports_collected': len(reports),
                'valid_reports': len(valid_reports),
                'started_at': start_time,
                'completed_at': datetime.now(),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            logger.info(f"Collection completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Collection failed for {self.platform_name}: {e}")
            return {
                'platform': self.platform_name,
                'status': 'failed',
                'error': str(e),
                'started_at': start_time,
                'completed_at': datetime.now()
            }
