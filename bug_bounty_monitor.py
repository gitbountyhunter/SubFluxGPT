#!/usr/bin/env python3
"""
Bug Bounty Platform Monitor
Continuously monitors bug bounty platforms for:
- New companies added to platforms
- Scope updates (new apex domains, subdomains)
- Changes to existing programs
Triggers SubFluxGPT for automatic testing
"""

import time
import logging
import requests
import json
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BountyProgram:
    """Represents a bug bounty program"""
    platform: str
    company: str
    program_name: str
    apex_domains: List[str]
    subdomains: List[str]
    in_scope: List[str]
    out_of_scope: List[str]
    last_updated: datetime
    url: str


class BugBountyMonitor:
    """Monitor bug bounty platforms for changes"""

    def __init__(self, db_path: str = 'data/monitor/bounty_monitor.db',
                 check_interval: int = 3600,
                 organize_folders: bool = False,
                 output_dir: str = 'targets',
                 auto_recon: bool = False,
                 recon_cmd: str = None):
        """
        Initialize monitor

        Args:
            db_path: Path to monitoring database
            check_interval: Check interval in seconds (default: 1 hour)
            organize_folders: Organize results by company folders
            output_dir: Base directory for organized folders
            auto_recon: Automatically run recon on new programs
            recon_cmd: Custom recon command (use {domain} placeholder)
        """
        self.db_path = db_path
        self.check_interval = check_interval
        self.monitor_dir = Path('data/monitor')
        self.monitor_dir.mkdir(parents=True, exist_ok=True)

        # Folder organization
        self.organize_folders = organize_folders
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Auto recon
        self.auto_recon = auto_recon
        self.recon_cmd = recon_cmd or "subfluxgpt recon --domain {domain} --verbose"

        # Initialize database
        self._init_db()

        # Queue for triggering SubFluxGPT
        self.trigger_queue = queue.Queue()

        # Control flag
        self.running = False

    def _init_db(self):
        """Initialize monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Programs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                company TEXT NOT NULL,
                program_name TEXT NOT NULL,
                apex_domains TEXT,
                subdomains TEXT,
                in_scope TEXT,
                out_of_scope TEXT,
                last_updated DATETIME,
                url TEXT,
                UNIQUE(platform, company, program_name)
            )
        ''')

        # Changes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_id INTEGER,
                change_type TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (program_id) REFERENCES programs(id)
            )
        ''')

        # New companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS new_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                company TEXT NOT NULL,
                program_name TEXT NOT NULL,
                discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')

        conn.commit()
        conn.close()

        logger.info(f"Monitor database initialized at {self.db_path}")

    def start_monitoring(self):
        """Start continuous monitoring"""
        self.running = True
        logger.info(f"Starting bug bounty monitoring (interval: {self.check_interval}s)")

        while self.running:
            try:
                logger.info("Checking bug bounty platforms...")
                self.check_all_platforms()
                logger.info("Check complete, waiting for next cycle...")

                # Process trigger queue
                self._process_triggers()

                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retry

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Stopping bug bounty monitoring")

    def check_all_platforms(self):
        """Check all bug bounty platforms"""
        # HackerOne
        self.check_hackerone()

        # Bugcrowd
        self.check_bugcrowd()

        # YesWeHack
        self.check_yeswehack()

        # Intigriti
        self.check_intigriti()

    def check_hackerone(self):
        """Check HackerOne for new programs and changes"""
        try:
            # This would use HackerOne API
            # For now, simulate with example data
            logger.info("Checking HackerOne...")

            # In production, you'd use:
            # response = requests.get('https://api.hackerone.com/v1/programs',
            #                          headers={'Authorization': f'Bearer {API_KEY}'})

            # Simulated check
            programs = self._get_hackerone_programs()

            for program in programs:
                self._check_program('hackerone', program)

        except Exception as e:
            logger.error(f"Error checking HackerOne: {e}")

    def check_bugcrowd(self):
        """Check Bugcrowd for new programs and changes"""
        try:
            logger.info("Checking Bugcrowd...")

            programs = self._get_bugcrowd_programs()

            for program in programs:
                self._check_program('bugcrowd', program)

        except Exception as e:
            logger.error(f"Error checking Bugcrowd: {e}")

    def check_yeswehack(self):
        """Check YesWeHack for new programs and changes"""
        try:
            logger.info("Checking YesWeHack...")

            programs = self._get_yeswehack_programs()

            for program in programs:
                self._check_program('yeswehack', program)

        except Exception as e:
            logger.error(f"Error checking YesWeHack: {e}")

    def check_intigriti(self):
        """Check Intigriti for new programs and changes"""
        try:
            logger.info("Checking Intigriti...")

            programs = self._get_intigriti_programs()

            for program in programs:
                self._check_program('intigriti', program)

        except Exception as e:
            logger.error(f"Error checking Intigriti: {e}")

    def _get_hackerone_programs(self) -> List[BountyProgram]:
        """Get HackerOne programs (placeholder)"""
        # In production, fetch from API
        return []

    def _get_bugcrowd_programs(self) -> List[BountyProgram]:
        """Get Bugcrowd programs (placeholder)"""
        # In production, fetch from API
        return []

    def _get_yeswehack_programs(self) -> List[BountyProgram]:
        """Get YesWeHack programs (placeholder)"""
        # In production, fetch from API
        return []

    def _get_intigriti_programs(self) -> List[BountyProgram]:
        """Get Intigriti programs (placeholder)"""
        # In production, fetch from API
        return []

    def _check_program(self, platform: str, program: BountyProgram):
        """Check a program for changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if program exists
        cursor.execute('''
            SELECT id, apex_domains, subdomains, in_scope, last_updated
            FROM programs
            WHERE platform = ? AND company = ? AND program_name = ?
        ''', (platform, program.company, program.program_name))

        existing = cursor.fetchone()

        if existing is None:
            # New program!
            logger.info(f"NEW PROGRAM: {platform} - {program.company}")

            cursor.execute('''
                INSERT INTO programs
                (platform, company, program_name, apex_domains, subdomains,
                 in_scope, out_of_scope, last_updated, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                program.company,
                program.program_name,
                json.dumps(program.apex_domains),
                json.dumps(program.subdomains),
                json.dumps(program.in_scope),
                json.dumps(program.out_of_scope),
                program.last_updated,
                program.url
            ))

            # Log as new company
            cursor.execute('''
                INSERT INTO new_companies (platform, company, program_name)
                VALUES (?, ?, ?)
            ''', (platform, program.company, program.program_name))

            # Queue for SubFluxGPT
            self.trigger_queue.put({
                'type': 'new_program',
                'platform': platform,
                'company': program.company,
                'program': program.program_name,
                'apex_domains': program.apex_domains
            })

        else:
            # Check for changes
            program_id, old_apex, old_subdomains, old_scope, old_updated = existing

            changes = []

            # Check apex domains
            old_apex_list = json.loads(old_apex) if old_apex else []
            if set(old_apex_list) != set(program.apex_domains):
                changes.append({
                    'type': 'apex_domains',
                    'old': old_apex_list,
                    'new': program.apex_domains
                })

            # Check subdomains
            old_sub_list = json.loads(old_subdomains) if old_subdomains else []
            if set(old_sub_list) != set(program.subdomains):
                changes.append({
                    'type': 'subdomains',
                    'old': old_sub_list,
                    'new': program.subdomains
                })

            # Check scope
            old_scope_list = json.loads(old_scope) if old_scope else []
            if set(old_scope_list) != set(program.in_scope):
                changes.append({
                    'type': 'scope',
                    'old': old_scope_list,
                    'new': program.in_scope
                })

            if changes:
                logger.info(f"CHANGES DETECTED: {platform} - {program.company}")

                # Update program
                cursor.execute('''
                    UPDATE programs
                    SET apex_domains = ?, subdomains = ?, in_scope = ?,
                        out_of_scope = ?, last_updated = ?
                    WHERE id = ?
                ''', (
                    json.dumps(program.apex_domains),
                    json.dumps(program.subdomains),
                    json.dumps(program.in_scope),
                    json.dumps(program.out_of_scope),
                    program.last_updated,
                    program_id
                ))

                # Log changes
                for change in changes:
                    cursor.execute('''
                        INSERT INTO changes
                        (program_id, change_type, old_value, new_value)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        program_id,
                        change['type'],
                        json.dumps(change['old']),
                        json.dumps(change['new'])
                    ))

                # Queue for SubFluxGPT
                self.trigger_queue.put({
                    'type': 'scope_change',
                    'platform': platform,
                    'company': program.company,
                    'program': program.program_name,
                    'changes': changes
                })

        conn.commit()
        conn.close()

    def _process_triggers(self):
        """Process trigger queue and execute SubFluxGPT"""
        while not self.trigger_queue.empty():
            try:
                trigger = self.trigger_queue.get()

                logger.info(f"Processing trigger: {trigger['type']}")

                # Execute SubFluxGPT
                self._execute_subfluxgpt(trigger)

            except Exception as e:
                logger.error(f"Error processing trigger: {e}")

    def _execute_subfluxgpt(self, trigger: Dict[str, Any]):
        """Execute SubFluxGPT based on trigger"""
        if trigger['type'] == 'new_program':
            apex_domains = trigger.get('apex_domains', [])
            company = trigger.get('company', 'unknown')
            program = trigger.get('program', 'unknown')

            if apex_domains:
                logger.info(f"Starting recon on new program: {company}")

                # Create company folder if organizing
                if self.organize_folders:
                    company_folder = self._create_company_folder(company, program)
                    self._save_scope_to_folder(company_folder, trigger)

                # Trigger cloud recon
                for apex in apex_domains:
                    if self.organize_folders:
                        self._run_cloud_recon_with_folder(apex, company_folder)
                    else:
                        self._run_cloud_recon(apex)

        elif trigger['type'] == 'scope_change':
            changes = trigger.get('changes', [])
            company = trigger.get('company', 'unknown')
            program = trigger.get('program', 'unknown')

            logger.info(f"Scope changes detected for {company}")

            # Create company folder if organizing
            if self.organize_folders:
                company_folder = self._create_company_folder(company, program)
                self._save_scope_to_folder(company_folder, trigger)

            # Re-run recon on changed domains
            for change in changes:
                if change['type'] == 'apex_domains':
                    for apex in change['new']:
                        if self.organize_folders:
                            self._run_cloud_recon_with_folder(apex, company_folder)
                        else:
                            self._run_cloud_recon(apex)

    def _create_company_folder(self, company: str, program: str) -> Path:
        """Create folder structure for company"""
        # Sanitize company name
        safe_company = company.replace(' ', '_').replace('/', '_').lower()
        safe_program = program.replace(' ', '_').replace('/', '_').lower()

        # Create folder structure
        company_folder = self.output_dir / safe_company / safe_program
        company_folder.mkdir(parents=True, exist_ok=True)

        # Create subfolders
        (company_folder / 'scope').mkdir(exist_ok=True)
        (company_folder / 'recon').mkdir(exist_ok=True)
        (company_folder / 'reports').mkdir(exist_ok=True)
        (company_folder / 'findings').mkdir(exist_ok=True)

        logger.info(f"Created company folder: {company_folder}")
        return company_folder

    def _save_scope_to_folder(self, folder: Path, trigger: Dict[str, Any]):
        """Save scope information to folder"""
        scope_file = folder / 'scope' / 'scope.json'

        scope_data = {
            'company': trigger.get('company'),
            'program': trigger.get('program'),
            'platform': trigger.get('platform'),
            'apex_domains': trigger.get('apex_domains', []),
            'subdomains': trigger.get('subdomains', []),
            'in_scope': trigger.get('in_scope', []),
            'out_of_scope': trigger.get('out_of_scope', []),
            'url': trigger.get('url'),
            'detected_at': datetime.now().isoformat()
        }

        with open(scope_file, 'w') as f:
            json.dump(scope_data, f, indent=2)

        logger.info(f"Saved scope to: {scope_file}")

    def _run_cloud_recon_with_folder(self, apex_domain: str, folder: Path):
        """Run cloud recon and save to company folder"""
        import subprocess

        logger.info(f"Running cloud recon on {apex_domain}")

        # Sanitize domain for filename
        safe_domain = apex_domain.replace('.', '_').replace('/', '_')

        # Output file
        output_file = folder / 'recon' / f"{safe_domain}_cloud_recon.json"

        try:
            # Run cloud recon with output
            result = subprocess.run(
                ['subfluxgpt', 'cloud', '--enhanced', '--apex', apex_domain,
                 '--output', str(output_file), '--verbose'],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                logger.info(f"Cloud recon completed for {apex_domain}, saved to {output_file}")

                # Also feed to AI learning
                self._feed_to_learning(apex_domain, result.stdout)

            else:
                logger.error(f"Cloud recon failed for {apex_domain}: {result.stderr}")

        except Exception as e:
            logger.error(f"Error running cloud recon: {e}")

    def _feed_to_learning(self, domain: str, output: str):
        """Feed recon results to continuous learning"""
        try:
            from ai_integration.continuous_learner import ContinuousLearner

            learner = ContinuousLearner()
            learner.log_tool_output(
                tool='cloud_recon',
                command=f'subfluxgpt cloud --enhanced --apex {domain}',
                stdout=output,
                stderr='',
                analyze=True
            )

            logger.debug(f"Fed {domain} recon results to learning system")

        except Exception as e:
            logger.error(f"Error feeding to learning: {e}")

    def _run_cloud_recon(self, apex_domain: str):
        """Run cloud reconnaissance on apex domain"""
        import subprocess

        logger.info(f"Running cloud recon on {apex_domain}")

        try:
            # Use the subfluxgpt alias
            result = subprocess.run(
                ['subfluxgpt', 'cloud', '--enhanced', '--apex', apex_domain, '--verbose'],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                logger.info(f"Cloud recon completed for {apex_domain}")
            else:
                logger.error(f"Cloud recon failed for {apex_domain}: {result.stderr}")

        except Exception as e:
            logger.error(f"Error running cloud recon: {e}")

    def get_new_programs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get newly discovered programs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT platform, company, program_name, discovered_at
            FROM new_companies
            WHERE processed = FALSE
            ORDER BY discovered_at DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [{
            'platform': row[0],
            'company': row[1],
            'program_name': row[2],
            'discovered_at': row[3]
        } for row in rows]

    def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent scope changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT c.change_type, c.old_value, c.new_value, c.detected_at,
                   p.platform, p.company, p.program_name
            FROM changes c
            JOIN programs p ON c.program_id = p.id
            WHERE c.detected_at >= ?
            ORDER BY c.detected_at DESC
        ''', (since,))

        rows = cursor.fetchall()
        conn.close()

        return [{
            'change_type': row[0],
            'old_value': row[1],
            'new_value': row[2],
            'detected_at': row[3],
            'platform': row[4],
            'company': row[5],
            'program_name': row[6]
        } for row in rows]


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Bug Bounty Platform Monitor')
    parser.add_argument('--interval', type=int, default=3600,
                       help='Check interval in seconds')
    parser.add_argument('--check-once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--list-new', action='store_true',
                       help='List new programs')
    parser.add_argument('--list-changes', type=int, default=24,
                       help='List changes in last N hours')
    parser.add_argument('--organize-folders', action='store_true',
                       help='Organize results by company folders')
    parser.add_argument('--output-dir', type=str, default='targets',
                       help='Base directory for organized folders')
    parser.add_argument('--auto-recon', action='store_true',
                       help='Automatically run recon on new programs')
    parser.add_argument('--recon-cmd', type=str,
                       help='Custom recon command (use {domain} placeholder)')
    parser.add_argument('--platform', type=str,
                       help='Monitor specific platform only')
    parser.add_argument('--platforms', type=str,
                       help='Monitor multiple platforms (comma-separated)')

    args = parser.parse_args()

    monitor = BugBountyMonitor(
        check_interval=args.interval,
        organize_folders=args.organize_folders,
        output_dir=args.output_dir,
        auto_recon=args.auto_recon,
        recon_cmd=args.recon_cmd
    )

    if args.list_new:
        programs = monitor.get_new_programs()
        print(f"New Programs ({len(programs)}):")
        for prog in programs:
            print(f"  - {prog['platform']}: {prog['company']} ({prog['program_name']})")
        return

    if args.list_changes:
        changes = monitor.get_recent_changes(hours=args.list_changes)
        print(f"Recent Changes ({len(changes)}):")
        for change in changes:
            print(f"  - {change['platform']}: {change['company']} - {change['change_type']}")
        return

    if args.check_once:
        monitor.check_all_platforms()
        return

    # Start continuous monitoring
    monitor.start_monitoring()


if __name__ == '__main__':
    main()
