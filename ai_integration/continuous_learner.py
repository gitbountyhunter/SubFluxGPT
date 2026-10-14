"""
Continuous Learning System
Mini AIs learn from every command, result, and workflow
Enables self-improving models that grow with usage
"""

import json
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class ContinuousLearner:
    """Continuous learning system for mini AIs"""

    def __init__(self, db_path: str = 'data/learning/learning.db'):
        """
        Initialize continuous learning system

        Args:
            db_path: Path to SQLite database for learning data
        """
        self.db_path = db_path
        self.learning_dir = Path('data/learning')
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

        # Training data accumulators
        self.command_history = []
        self.tool_outputs = []
        self.successful_patterns = defaultdict(int)
        self.failure_patterns = defaultdict(int)

    def _init_db(self):
        """Initialize learning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                tool TEXT NOT NULL,
                args TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exit_code INTEGER,
                duration REAL,
                success BOOLEAN
            )
        ''')

        # Tool outputs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool TEXT NOT NULL,
                command TEXT NOT NULL,
                stdout TEXT,
                stderr TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                output_hash TEXT,
                analyzed BOOLEAN DEFAULT FALSE
            )
        ''')

        # Workflow patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                tool_sequence TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Findings table (for vulnerability discoveries)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool TEXT NOT NULL,
                finding_type TEXT NOT NULL,
                severity TEXT,
                target TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE
            )
        ''')

        # Learning metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        logger.info(f"Learning database initialized at {self.db_path}")

    def log_command(self, tool: str, args: List[str], exit_code: int,
                    duration: float):
        """
        Log a command execution for learning

        Args:
            tool: Tool name
            args: Command arguments
            exit_code: Exit code
            duration: Execution duration in seconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO commands (command, tool, args, exit_code, duration, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            f"{tool} {' '.join(args)}",
            tool,
            json.dumps(args),
            exit_code,
            duration,
            exit_code == 0
        ))

        conn.commit()
        conn.close()

        # Update pattern counters
        pattern = f"{tool}_{hashlib.md5(' '.join(args).encode()).hexdigest()[:8]}"
        if exit_code == 0:
            self.successful_patterns[pattern] += 1
        else:
            self.failure_patterns[pattern] += 1

        logger.debug(f"Logged command: {tool} {' '.join(args)}")

    def log_tool_output(self, tool: str, command: str, stdout: str,
                        stderr: str, analyze: bool = True):
        """
        Log tool output for learning

        Args:
            tool: Tool name
            command: Full command
            stdout: Standard output
            stderr: Standard error
            analyze: Whether to analyze output for patterns
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create hash of output for deduplication
        output_hash = hashlib.md5((stdout + stderr).encode()).hexdigest()

        cursor.execute('''
            INSERT INTO tool_outputs (tool, command, stdout, stderr, output_hash, analyzed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tool, command, stdout, stderr, output_hash, analyze))

        conn.commit()
        conn.close()

        if analyze:
            self._analyze_output(tool, stdout, stderr)

        logger.debug(f"Logged tool output: {tool}")

    def log_workflow(self, tool_sequence: List[str], success: bool):
        """
        Log a workflow pattern

        Args:
            tool_sequence: List of tools in sequence
            success: Whether workflow was successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        pattern = ' -> '.join(tool_sequence)

        cursor.execute('''
            INSERT OR REPLACE INTO workflow_patterns
            (pattern, tool_sequence, success_count, failure_count, last_used)
            VALUES (?, ?,
                COALESCE((SELECT success_count FROM workflow_patterns WHERE pattern = ?), 0) + ?,
                COALESCE((SELECT failure_count FROM workflow_patterns WHERE pattern = ?), 0) + ?,
                CURRENT_TIMESTAMP)
        ''', (pattern, json.dumps(tool_sequence), pattern,
              1 if success else 0, pattern,
              0 if success else 1))

        conn.commit()
        conn.close()

        logger.debug(f"Logged workflow: {pattern}")

    def log_finding(self, tool: str, finding_type: str, severity: str,
                    target: str, verified: bool = False):
        """
        Log a security finding

        Args:
            tool: Tool that found it
            finding_type: Type of finding
            severity: Severity level
            target: Target domain/URL
            verified: Whether verified
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO findings (tool, finding_type, severity, target, verified)
            VALUES (?, ?, ?, ?, ?)
        ''', (tool, finding_type, severity, target, verified))

        conn.commit()
        conn.close()

        logger.info(f"Logged finding: {finding_type} on {target} (severity: {severity})")

    def _analyze_output(self, tool: str, stdout: str, stderr: str):
        """Analyze tool output for learning patterns"""
        # Extract patterns from output
        patterns = self._extract_patterns(tool, stdout)

        # Store in patterns table
        for pattern in patterns:
            self._store_pattern(tool, pattern)

    def _extract_patterns(self, tool: str, output: str) -> List[str]:
        """Extract patterns from tool output"""
        patterns = []

        # Tool-specific pattern extraction
        if tool == 'subfinder':
            # Extract subdomain patterns
            lines = output.strip().split('\n')
            for line in lines:
                if '.' in line:
                    parts = line.split('.')
                    if len(parts) > 2:
                        patterns.append(f"subdomain_length_{len(parts)}")

        elif tool == 'nuclei':
            # Extract vulnerability patterns
            if 'critical' in output.lower():
                patterns.append('critical_vuln')
            if 'high' in output.lower():
                patterns.append('high_vuln')

        elif tool == 'httpx':
            # Extract HTTP status patterns
            if '200' in output:
                patterns.append('http_200')
            if '403' in output:
                patterns.append('http_403')
            if '500' in output:
                patterns.append('http_500')

        return patterns

    def _store_pattern(self, tool: str, pattern: str):
        """Store a pattern in the database"""
        # This could be expanded to track pattern frequency
        pass

    def get_training_data(self, tool: str = None,
                          limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get training data for model fine-tuning

        Args:
            tool: Filter by tool (optional)
            limit: Maximum number of records

        Returns:
            List of training examples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if tool:
            cursor.execute('''
                SELECT command, args, success, exit_code
                FROM commands
                WHERE tool = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (tool, limit))
        else:
            cursor.execute('''
                SELECT command, args, success, exit_code
                FROM commands
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        training_data = []
        for row in rows:
            training_data.append({
                'command': row[0],
                'args': json.loads(row[1]),
                'success': row[2],
                'exit_code': row[3]
            })

        return training_data

    def get_successful_workflows(self, min_success: int = 5) -> List[Dict[str, Any]]:
        """
        Get successful workflow patterns

        Args:
            min_success: Minimum success count

        Returns:
            List of successful workflows
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT pattern, tool_sequence, success_count, failure_count, last_used
            FROM workflow_patterns
            WHERE success_count >= ?
            ORDER BY success_count DESC
        ''', (min_success,))

        rows = cursor.fetchall()
        conn.close()

        workflows = []
        for row in rows:
            workflows.append({
                'pattern': row[0],
                'tool_sequence': json.loads(row[1]),
                'success_count': row[2],
                'failure_count': row[3],
                'last_used': row[4]
            })

        return workflows

    def export_training_dataset(self, output_path: str):
        """
        Export learning data as training dataset

        Args:
            output_path: Path to export dataset
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Export commands
        cursor.execute('SELECT * FROM commands')
        commands = cursor.fetchall()

        # Export tool outputs
        cursor.execute('SELECT * FROM tool_outputs')
        outputs = cursor.fetchall()

        # Export workflows
        cursor.execute('SELECT * FROM workflow_patterns')
        workflows = cursor.fetchall()

        conn.close()

        dataset = {
            'commands': commands,
            'tool_outputs': outputs,
            'workflows': workflows,
            'exported_at': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)

        logger.info(f"Exported training dataset to {output_path}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Command stats
        cursor.execute('SELECT COUNT(*) FROM commands')
        stats['total_commands'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM commands WHERE success = 1')
        stats['successful_commands'] = cursor.fetchone()[0]

        # Tool output stats
        cursor.execute('SELECT COUNT(*) FROM tool_outputs')
        stats['total_outputs'] = cursor.fetchone()[0]

        # Workflow stats
        cursor.execute('SELECT COUNT(*) FROM workflow_patterns')
        stats['total_workflows'] = cursor.fetchone()[0]

        # Finding stats
        cursor.execute('SELECT COUNT(*) FROM findings')
        stats['total_findings'] = cursor.fetchone()[0]

        cursor.execute('SELECT severity, COUNT(*) FROM findings GROUP BY severity')
        stats['findings_by_severity'] = dict(cursor.fetchall())

        conn.close()

        return stats
