"""
Bugcrowd collector for bug bounty data.
Uses Bugcrowd API for data collection.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import aiohttp
import re

from .base import BaseCollector, Report, Program

logger = logging.getLogger(__name__)


class BugcrowdCollector(BaseCollector):
    """Collector for Bugcrowd platform."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_token = config.get('api_token')
        self.base_url = config.get('base_url', 'https://api.bugcrowd.com')
        
        # Keywords for filtering relevant reports
        self.relevant_keywords = re.compile(
            r"\b(subdomain|sub-domain|dns|dangling|cname|takeover|"
            r"zone transfer|subdomain takeover)\b",
            re.IGNORECASE,
        )
    
    async def collect_programs(self) -> List[Program]:
        """
        Collect programs from Bugcrowd API.
        
        Returns:
            List of Program objects
        """
        try:
            programs = []
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.api_token}',
                    'Accept': 'application/json'
                }
                
                # Fetch programs from Bugcrowd API
                # Note: This is a placeholder - actual API endpoints may differ
                async with session.get(
                    f'{self.base_url}/programs',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for program_data in data.get('programs', []):
                            program = Program(
                                platform='bugcrowd',
                                program_id=str(program_data.get('id')),
                                name=program_data.get('name'),
                                url=program_data.get('url'),
                                metadata={
                                    'code': program_data.get('code'),
                                    'submission_state': program_data.get('submission_state')
                                }
                            )
                            programs.append(program)
                    else:
                        logger.error(f"Failed to fetch programs: {response.status}")
            
            logger.info(f"Collected {len(programs)} programs from Bugcrowd")
            return programs
            
        except Exception as e:
            logger.error(f"Failed to collect Bugcrowd programs: {e}")
            raise
    
    async def collect_reports(self, program_id: str, limit: Optional[int] = None) -> List[Report]:
        """
        Collect reports for a specific program.
        
        Args:
            program_id: Bugcrowd program ID
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        try:
            reports = []
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.api_token}',
                    'Accept': 'application/json'
                }
                
                # Fetch reports for the program
                # Note: This is a placeholder - actual API endpoints may differ
                async with session.get(
                    f'{self.base_url}/programs/{program_id}/reports',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for report_data in data.get('reports', []):
                            report = self._parse_api_response(report_data)
                            if report:
                                reports.append(report)
                                
                                if limit and len(reports) >= limit:
                                    break
                    else:
                        logger.error(f"Failed to fetch reports: {response.status}")
            
            logger.info(f"Collected {len(reports)} reports for program {program_id}")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to collect reports for program {program_id}: {e}")
            raise
    
    async def collect_all_reports(self, limit: Optional[int] = None) -> List[Report]:
        """
        Collect all disclosed reports from Bugcrowd.
        
        Args:
            limit: Maximum number of reports to collect
            
        Returns:
            List of Report objects
        """
        try:
            # First collect all programs
            programs = await self.collect_programs()
            
            all_reports = []
            for program in programs:
                # Collect reports for each program
                reports = await self.collect_reports(program.program_id)
                all_reports.extend(reports)
                
                if limit and len(all_reports) >= limit:
                    break
            
            logger.info(f"Collected {len(all_reports)} total reports from Bugcrowd")
            return all_reports
            
        except Exception as e:
            logger.error(f"Failed to collect all Bugcrowd reports: {e}")
            raise
    
    def _parse_api_response(self, data: Dict[str, Any]) -> Optional[Report]:
        """
        Parse Bugcrowd API response into a Report object.
        
        Args:
            data: API response dictionary
            
        Returns:
            Report object or None if parsing fails
        """
        try:
            # Extract report data
            report_id = str(data.get('id', ''))
            title = data.get('title', '')
            weakness = data.get('vulnerability_type', {}).get('name')
            severity = data.get('severity_rating')
            reporter = data.get('researcher', {}).get('username')
            bounty_amount = data.get('bounty_amount')
            disclosed_at = data.get('disclosed_at')
            url = data.get('url')
            
            # Extract vulnerability information
            vulnerability_info = data.get('description', '')
            
            # Check if report is relevant
            if not self.relevant_keywords.search(vulnerability_info):
                return None
            
            # Build report object
            report = Report(
                platform='bugcrowd',
                platform_report_id=report_id,
                program_id=str(data.get('program', {}).get('id')),
                program_name=data.get('program', {}).get('name'),
                title=title,
                weakness=weakness,
                severity=severity,
                reporter=reporter,
                bounty_amount=float(bounty_amount) if bounty_amount else None,
                disclosed_at=datetime.fromisoformat(disclosed_at) if disclosed_at else None,
                url=url,
                raw_content=self._format_report_content(data),
                metadata={
                    'state': data.get('state'),
                    'target': data.get('target', {}).get('type')
                }
            )
            
            return report
            
        except Exception as e:
            logger.warning(f"Failed to parse Bugcrowd API response: {e}")
            return None
    
    def _format_report_content(self, data: Dict[str, Any]) -> str:
        """
        Format report content for training data.
        
        Args:
            data: API response dictionary
            
        Returns:
            Formatted report content string
        """
        program = data.get('program', {})
        program_name = program.get('name')
        title = data.get('title', '')
        weakness = data.get('vulnerability_type', {}).get('name')
        description = data.get('description', '')
        
        content = f"Program: {program_name}\n"
        content += f"Report title: {title}\n"
        content += f"Weakness: {weakness}\n"
        content += f"Report details: {description}\n"
        
        return content.strip()
