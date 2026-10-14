#!/usr/bin/env python3
"""
Self-Improving LLM System
Continuously feeds HackerOne/Bugcrowd reports to mini LLMs
Models learn from real-world bug bounty reports and improve over time
"""

import logging
import json
import sqlite3
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelfImprovingLLM:
    """Self-improving LLM system fed with bug bounty reports"""

    def __init__(self, db_path: str = 'data/self_improving/reports.db',
                 update_interval: int = 86400):
        """
        Initialize self-improving system

        Args:
            db_path: Path to reports database
            update_interval: Update interval in seconds (default: 24 hours)
        """
        self.db_path = db_path
        self.update_interval = update_interval
        self.data_dir = Path('data/self_improving')
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

        # Control flag
        self.running = False

    def _init_db(self):
        """Initialize reports database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                report_id TEXT NOT NULL,
                title TEXT,
                severity TEXT,
                vulnerability_type TEXT,
                description TEXT,
                disclosure_url TEXT,
                bounty_amount REAL,
                reported_at DATETIME,
                disclosed_at DATETIME,
                processed BOOLEAN DEFAULT FALSE,
                embedding_vector BLOB,
                UNIQUE(platform, report_id)
            )
        ''')

        # Training examples table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                example_type TEXT NOT NULL,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        ''')

        # Learning progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                value REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        logger.info(f"Self-improving database initialized at {self.db_path}")

    def start_continuous_learning(self):
        """Start continuous learning loop"""
        self.running = True
        logger.info(f"Starting continuous learning (interval: {self.update_interval}s)")

        while self.running:
            try:
                logger.info("Fetching new bug bounty reports...")
                self.fetch_reports()

                logger.info("Processing reports for training...")
                self.process_reports()

                logger.info("Updating models...")
                self.update_models()

                logger.info("Learning cycle complete, waiting...")
                time.sleep(self.update_interval)

            except KeyboardInterrupt:
                logger.info("Learning stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"Error in learning cycle: {e}")
                time.sleep(3600)  # Wait 1 hour before retry

    def stop_learning(self):
        """Stop continuous learning"""
        self.running = False
        logger.info("Stopping continuous learning")

    def fetch_reports(self):
        """Fetch reports from bug bounty platforms"""
        # HackerOne disclosed reports
        self.fetch_hackerone_reports()

        # Bugcrowd reports
        self.fetch_bugcrowd_reports()

    def fetch_hackerone_reports(self):
        """Fetch disclosed reports from HackerOne"""
        try:
            logger.info("Fetching HackerOne reports...")

            # In production, use HackerOne API
            # For now, simulate with example data structure

            # Example of what the API would return:
            # response = requests.get('https://api.hackerone.com/v1/reports',
            #                          headers={'Authorization': f'Bearer {API_KEY}'})

            # Placeholder: You would parse the API response here
            reports = []

            for report in reports:
                self._store_report('hackerone', report)

            logger.info(f"Fetched {len(reports)} HackerOne reports")

        except Exception as e:
            logger.error(f"Error fetching HackerOne reports: {e}")

    def fetch_bugcrowd_reports(self):
        """Fetch reports from Bugcrowd"""
        try:
            logger.info("Fetching Bugcrowd reports...")

            # In production, use Bugcrowd API
            reports = []

            for report in reports:
                self._store_report('bugcrowd', report)

            logger.info(f"Fetched {len(reports)} Bugcrowd reports")

        except Exception as e:
            logger.error(f"Error fetching Bugcrowd reports: {e}")

    def _store_report(self, platform: str, report: Dict[str, Any]):
        """Store a report in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO reports
                (platform, report_id, title, severity, vulnerability_type,
                 description, disclosure_url, bounty_amount, reported_at, disclosed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                report.get('id'),
                report.get('title'),
                report.get('severity'),
                report.get('vulnerability_type'),
                report.get('description'),
                report.get('disclosure_url'),
                report.get('bounty_amount'),
                report.get('reported_at'),
                report.get('disclosed_at')
            ))

            conn.commit()
            logger.debug(f"Stored report: {platform} - {report.get('id')}")

        except sqlite3.IntegrityError:
            # Report already exists
            pass
        finally:
            conn.close()

    def process_reports(self):
        """Process unprocessed reports into training examples"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get unprocessed reports
        cursor.execute('''
            SELECT id, title, severity, vulnerability_type, description
            FROM reports
            WHERE processed = FALSE
            LIMIT 100
        ''')

        reports = cursor.fetchall()

        for report in reports:
            report_id, title, severity, vuln_type, description = report

            # Create training examples
            examples = self._create_training_examples(
                title, severity, vuln_type, description
            )

            # Store examples
            for example in examples:
                cursor.execute('''
                    INSERT INTO training_examples
                    (report_id, example_type, input_text, output_text)
                    VALUES (?, ?, ?, ?)
                ''', (report_id, example['type'], example['input'], example['output']))

            # Mark as processed
            cursor.execute('UPDATE reports SET processed = TRUE WHERE id = ?', (report_id,))

        conn.commit()
        conn.close()

        logger.info(f"Processed {len(reports)} reports into training examples")

    def _create_training_examples(self, title: str, severity: str,
                                   vuln_type: str, description: str) -> List[Dict[str, str]]:
        """Create training examples from a report"""
        examples = []

        # Example 1: Severity classification
        examples.append({
            'type': 'severity_classification',
            'input': f"Vulnerability: {title}\nType: {vuln_type}\nDescription: {description[:500]}",
            'output': f"Severity: {severity}"
        })

        # Example 2: Vulnerability type classification
        examples.append({
            'type': 'vulnerability_classification',
            'input': f"Title: {title}\nDescription: {description[:500]}",
            'output': f"Type: {vuln_type}"
        })

        # Example 3: Description summarization
        examples.append({
            'type': 'summarization',
            'input': description,
            'output': f"{title} - {severity} severity {vuln_type}"
        })

        # Example 4: Command suggestion
        examples.append({
            'type': 'command_suggestion',
            'input': f"Vulnerability: {vuln_type}\nTarget: example.com",
            'output': self._suggest_command(vuln_type)
        })

        return examples

    def _suggest_command(self, vuln_type: str) -> str:
        """Suggest command based on vulnerability type"""
        commands = {
            'XSS': 'nuclei -u example.com -t xss-templates/',
            'SQL Injection': 'sqlmap -u example.com/page?id=1',
            'SSRF': 'nuclei -u example.com -t ssrf-templates/',
            'IDOR': 'nuclei -u example.com -t idor-templates/',
            'RCE': 'nuclei -u example.com -t rce-templates/',
            'Subdomain Takeover': 'subfinder -d example.com | httpx',
            'Information Disclosure': 'nuclei -u example.com -t info-disclosure/'
        }

        for key, cmd in commands.items():
            if key.lower() in vuln_type.lower():
                return cmd

        return 'nuclei -u example.com'

    def update_models(self):
        """Update mini LLMs with new training data"""
        try:
            # Export training data
            dataset_path = self.export_training_data()

            # Trigger fine-tuning
            from unsloth_finetuner import UnslothFineTuner

            tuner = UnslothFineTuner()
            result = tuner.finetune_qlora(
                dataset_path=dataset_path,
                model_size='124M',
                epochs=1,
                batch_size=4
            )

            if result['success']:
                logger.info(f"Model updated: {result['output_path']}")

                # Record progress
                self._record_progress('model_update', 1.0)

        except Exception as e:
            logger.error(f"Error updating models: {e}")

    def export_training_data(self, output_path: str = None) -> str:
        """Export training data for fine-tuning"""
        if output_path is None:
            output_path = self.data_dir / 'training_dataset.json'

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT input_text, output_text, example_type
            FROM training_examples
            ORDER BY created_at DESC
            LIMIT 10000
        ''')

        rows = cursor.fetchall()
        conn.close()

        training_data = []
        for row in rows:
            training_data.append({
                'input': row[0],
                'output': row[1],
                'type': row[2]
            })

        with open(output_path, 'w') as f:
            json.dump(training_data, f, indent=2)

        logger.info(f"Exported {len(training_data)} training examples to {output_path}")
        return str(output_path)

    def _record_progress(self, metric: str, value: float):
        """Record learning progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO learning_progress (metric, value)
            VALUES (?, ?)
        ''', (metric, value))

        conn.commit()
        conn.close()

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Report stats
        cursor.execute('SELECT COUNT(*) FROM reports')
        stats['total_reports'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM reports WHERE processed = TRUE')
        stats['processed_reports'] = cursor.fetchone()[0]

        # Training example stats
        cursor.execute('SELECT COUNT(*) FROM training_examples')
        stats['total_examples'] = cursor.fetchone()[0]

        cursor.execute('''
            SELECT example_type, COUNT(*)
            FROM training_examples
            GROUP BY example_type
        ''')
        stats['examples_by_type'] = dict(cursor.fetchall())

        # Platform stats
        cursor.execute('''
            SELECT platform, COUNT(*)
            FROM reports
            GROUP BY platform
        ''')
        stats['reports_by_platform'] = dict(cursor.fetchall())

        # Progress stats
        cursor.execute('''
            SELECT metric, AVG(value)
            FROM learning_progress
            GROUP BY metric
        ''')
        stats['progress_metrics'] = dict(cursor.fetchall())

        conn.close()

        return stats


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Self-Improving LLM System')
    parser.add_argument('--start', action='store_true',
                       help='Start continuous learning')
    parser.add_argument('--fetch', action='store_true',
                       help='Fetch reports once')
    parser.add_argument('--process', action='store_true',
                       help='Process reports once')
    parser.add_argument('--export', action='store_true',
                       help='Export training data')
    parser.add_argument('--stats', action='store_true',
                       help='Show learning statistics')

    args = parser.parse_args()

    system = SelfImprovingLLM()

    if args.start:
        system.start_continuous_learning()

    elif args.fetch:
        system.fetch_reports()

    elif args.process:
        system.process_reports()

    elif args.export:
        system.export_training_data()

    elif args.stats:
        stats = system.get_learning_stats()
        print(json.dumps(stats, indent=2))

    else:
        print("No action specified. Use --start, --fetch, --process, --export, or --stats")


if __name__ == '__main__':
    main()
