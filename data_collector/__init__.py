"""Data collector module for SubFluxGPT."""

from data_collector.collectors.base import BaseCollector, Report, Program
from data_collector.collectors.hackerone import HackerOneCollector
from data_collector.collectors.bugcrowd import BugcrowdCollector
from data_collector.collectors.yeswehack import YesWeHackCollector
from data_collector.database_manager import DatabaseManager

__all__ = [
    'BaseCollector',
    'Report',
    'Program',
    'HackerOneCollector',
    'BugcrowdCollector',
    'YesWeHackCollector',
    'DatabaseManager'
]
