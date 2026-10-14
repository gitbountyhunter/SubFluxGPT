"""
HackerOne collector for bug bounty data.
Supports both API and HuggingFace dataset methods.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

from datasets import load_dataset
from .base import BaseCollector, Report, Program

logger = logging.getLogger(__name__)


class HackerOneCollector(BaseCollector):
    """Collector for HackerOne platform."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.use_dataset = config.get('use_dataset', True)
        self.dataset_id = config.get('dataset_id', 'Hacker0x01/hackerone_disclosed_reports')
        self.api_key = config.get('api_key')
        self.api_username = config.get('api_username')
        
        # Keywords for filtering relevant reports
        self.relevant_keywords = re.compile(
            r"\b(subdomain|sub-domain|dns|dangling|cname|takeover|"
            r"zone transfer|subdomain takeover)\b",
            re.IGNORECASE,
        )
    
    async def collect_programs(self) -> List[Program]:
        """
        Collect programs from HackerOne.
        
        If using dataset, extract unique programs from reports.
        If using API, use HackerOne programs endpoint.
        """
        if self.use_dataset:
            logger.info("Extracting programs from HuggingFace dataset")
            return await self._extract_programs_from_dataset()
        else:
            logger.info("Fetching programs from HackerOne API")
            return await self._fetch_programs_from_api()
    
    async def _extract_programs_from_dataset(self) -> List[Program]:
        """Extract unique programs from the HuggingFace dataset."""
        try:
            dataset = load_dataset(self.dataset_id, split='train')
            
            programs_map = {}
            for row in dataset:
                program_handle = row.get('program', {}).get('handle')
                program_name = row.get('program', {}).get('name')
                
                if program_handle and program_name:
                    if program_handle not in programs_map:
                        programs_map[program_handle] = Program(
                            platform='hackerone',
                            program_id=program_handle,
                            name=program_name,
                            url=f"https://hackerone.com/{program_handle}"
                        )
            
            programs = list(programs_map.values())
            logger.info(f"Extracted {len(programs)} unique programs from dataset")
            return programs
            
        except Exception as e:
            logger.error(f"Failed to extract programs from dataset: {e}")
            raise
    
    async def _fetch_programs_from_api(self) -> List[Program]:
        """Fetch programs from HackerOne API."""
        # TODO: Implement API-based program collection
        # This requires proper authentication and API structure
        logger.warning("API-based program collection not yet implemented")
        return []
    
    async def collect_reports(self, program_id: str, limit: Optional[int] = None) -> List[Report]:
        """
        Collect reports for a specific program.
        
        Args:
            program_id: HackerOne program handle
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        if self.use_dataset:
            return await self._collect_reports_from_dataset(program_id, limit)
        else:
            return await self._collect_reports_from_api(program_id, limit)
    
    async def _collect_reports_from_dataset(self, program_id: str, limit: Optional[int] = None) -> List[Report]:
        """Collect reports for a program from HuggingFace dataset."""
        try:
            dataset = load_dataset(self.dataset_id, split='train')
            
            reports = []
            for row in dataset:
                program_handle = row.get('program', {}).get('handle')
                
                if program_handle == program_id:
                    report = self._parse_dataset_row(row)
                    if report:
                        reports.append(report)
                        
                        if limit and len(reports) >= limit:
                            break
            
            logger.info(f"Collected {len(reports)} reports for program {program_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to collect reports for program {program_id}: {e}")
            raise
    
    async def _collect_reports_from_api(self, program_id: str, limit: Optional[int] = None) -> List[Report]:
        """Collect reports for a program from HackerOne API."""
        # TODO: Implement API-based report collection
        logger.warning("API-based report collection not yet implemented")
        return []
    
    async def collect_all_reports(self, limit: Optional[int] = None) -> List[Report]:
        """
        Collect all disclosed reports from HackerOne.
        
        Args:
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        if self.use_dataset:
            return await self._collect_all_from_dataset(limit)
        else:
            return await self._collect_all_from_api(limit)
    
    async def _collect_all_from_dataset(self, limit: Optional[int] = None) -> List[Report]:
        """Collect all reports from HuggingFace dataset."""
        try:
            logger.info(f"Loading dataset {self.dataset_id}")
            dataset = load_dataset(self.dataset_id, split='train')
            
            reports = []
            for row in dataset:
                report = self._parse_dataset_row(row)
                if report:
                    reports.append(report)
                    
                    if limit and len(reports) >= limit:
                        break
            
            logger.info(f"Collected {len(reports)} reports from dataset")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to collect reports from dataset: {e}")
            raise
    
    async def _collect_all_from_api(self, limit: Optional[int] = None) -> List[Report]:
        """Collect all reports from HackerOne API."""
        # TODO: Implement API-based collection
        logger.warning("API-based collection not yet implemented")
        return []
    
    def _parse_dataset_row(self, row: Dict[str, Any]) -> Optional[Report]:
        """
        Parse a dataset row into a Report object.
        
        Args:
            row: Dataset row dictionary
            
        Returns:
            Report object or None if parsing fails
        """
        try:
            program = row.get('program', {})
            program_handle = program.get('handle')
            program_name = program.get('name')
            
            # Extract report data
            report_id = str(row.get('id', ''))
            title = row.get('title', '')
            weakness = row.get('weakness', {}).get('name')
            severity = row.get('severity', {}).get('rating')
            reporter = row.get('reporter', {}).get('username')
            bounty_amount = row.get('bounty_amount')
            disclosed_at = row.get('disclosed_at')
            url = row.get('url')
            
            # Extract vulnerability information
            vulnerability_info = row.get('vulnerability_information', '')
            
            # Check if report is relevant (contains subdomain/DNS keywords)
            if not self.relevant_keywords.search(vulnerability_info):
                return None
            
            # Build report object
            report = Report(
                platform='hackerone',
                platform_report_id=report_id,
                program_id=program_handle,
                program_name=program_name,
                title=title,
                weakness=weakness,
                severity=severity,
                reporter=reporter,
                bounty_amount=float(bounty_amount) if bounty_amount else None,
                disclosed_at=datetime.fromisoformat(disclosed_at) if disclosed_at else None,
                url=url,
                raw_content=self._format_report_content(row),
                metadata={
                    'cve_id': row.get('cve_id'),
                    'state': row.get('state'),
                    'substate': row.get('substate')
                }
            )
            
            return report
            
        except Exception as e:
            logger.warning(f"Failed to parse dataset row: {e}")
            return None
    
    def _format_report_content(self, row: Dict[str, Any]) -> str:
        """
        Format report content for training data.
        
        Args:
            row: Dataset row dictionary
            
        Returns:
            Formatted report content string
        """
        program = row.get('program', {})
        program_name = program.get('name')
        title = row.get('title', '')
        weakness = row.get('weakness', {}).get('name')
        vulnerability_info = row.get('vulnerability_information', '')
        
        content = f"Program: {program_name}\n"
        content += f"Report title: {title}\n"
        content += f"Weakness: {weakness}\n"
        content += f"Report details: {vulnerability_info}\n"
        
        return content.strip()
