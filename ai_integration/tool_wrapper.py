"""
Tool Wrapper - AI-Enabled Security Tool Integration
Wraps all security tools with AI analysis and learning capabilities
"""

import subprocess
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolWrapper:
    """Wrapper for security tools with AI integration"""

    # All supported security tools
    SUPPORTED_TOOLS = {
        'httpx': {
            'command': 'httpx',
            'analysis_type': 'http_probe',
            'ai_tasks': ['analyze_response', 'detect_tech_stack', 'find_vulnerabilities']
        },
        'subfinder': {
            'command': 'subfinder',
            'analysis_type': 'subdomain_discovery',
            'ai_tasks': ['classify_subdomains', 'predict_takeover', 'analyze_patterns']
        },
        'katana': {
            'command': 'katana',
            'analysis_type': 'web_crawling',
            'ai_tasks': ['extract_endpoints', 'analyze_params', 'find_hidden_pages']
        },
        'nuclei': {
            'command': 'nuclei',
            'analysis_type': 'vulnerability_scanning',
            'ai_tasks': ['prioritize_findings', 'analyze_chain', 'suggest_payloads']
        },
        'bbrf': {
            'command': 'bbrf',
            'analysis_type': 'data_management',
            'ai_tasks': ['correlate_data', 'find_patterns', 'enrich_intel']
        },
        'dnsx': {
            'command': 'dnsx',
            'analysis_type': 'dns_resolution',
            'ai_tasks': ['analyze_dns_records', 'detect_wildcards', 'find_suspicious']
        },
        'massdns': {
            'command': 'massdns',
            'analysis_type': 'mass_dns',
            'ai_tasks': ['analyze_resolution_patterns', 'detect_dns_zones']
        },
        'naabu': {
            'command': 'naabu',
            'analysis_type': 'port_scanning',
            'ai_tasks': ['analyze_open_ports', 'detect_services', 'predict_vulnerabilities']
        },
        'gau': {
            'command': 'gau',
            'analysis_type': 'url_archives',
            'ai_tasks': ['analyze_historical_urls', 'find_parameters', 'detect_changes']
        },
        'waybackurls': {
            'command': 'waybackurls',
            'analysis_type': 'wayback_machine',
            'ai_tasks': ['analyze_historical', 'find_live', 'extract_params']
        },
        'ffuf': {
            'command': 'ffuf',
            'analysis_type': 'fuzzing',
            'ai_tasks': ['analyze_fuzz_results', 'detect_anomalies', 'suggest_wordlists']
        },
        'hakrawler': {
            'command': 'hakrawler',
            'analysis_type': 'crawling',
            'ai_tasks': ['extract_js', 'find_endpoints', 'analyze_crawl']
        },
        'assetfinder': {
            'command': 'assetfinder',
            'analysis_type': 'asset_discovery',
            'ai_tasks': ['classify_assets', 'find_related', 'analyze_scope']
        },
        'amass': {
            'command': 'amass',
            'analysis_type': 'comprehensive_recon',
            'ai_tasks': ['analyze_attack_surface', 'find_subdomains', 'correlate_intel']
        }
    }

    def __init__(self, model_path: str = None, enable_learning: bool = True):
        """
        Initialize tool wrapper

        Args:
            model_path: Path to mini AI model for analysis
            enable_learning: Enable continuous learning from tool outputs
        """
        self.model_path = model_path
        self.enable_learning = enable_learning
        self.learning_data_path = Path('data/learning/tool_outputs')
        self.learning_data_path.mkdir(parents=True, exist_ok=True)

        # Import AI analyzer if available
        try:
            from .ai_analyzer import AIAnalyzer
            self.ai_analyzer = AIAnalyzer(model_path=model_path)
        except ImportError:
            self.ai_analyzer = None
            logger.warning("AIAnalyzer not available, running without AI analysis")

    def execute_tool(self, tool_name: str, args: List[str],
                     enable_ai: bool = True,
                     save_output: bool = True) -> Dict[str, Any]:
        """
        Execute a security tool with AI analysis

        Args:
            tool_name: Name of the tool (e.g., 'httpx', 'subfinder')
            args: Command-line arguments for the tool
            enable_ai: Enable AI analysis of output
            save_output: Save output for learning

        Returns:
            Dict with execution results and AI analysis
        """
        if tool_name not in self.SUPPORTED_TOOLS:
            raise ValueError(f"Unsupported tool: {tool_name}")

        tool_config = self.SUPPORTED_TOOLS[tool_name]
        command = [tool_config['command']] + args

        logger.info(f"Executing: {' '.join(command)}")

        # Execute the tool
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            output = {
                'tool': tool_name,
                'command': ' '.join(command),
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'timestamp': datetime.now().isoformat(),
                'success': result.returncode == 0
            }

            # AI Analysis
            if enable_ai and self.ai_analyzer and result.returncode == 0:
                output['ai_analysis'] = self._analyze_output(
                    tool_name,
                    result.stdout,
                    tool_config['ai_tasks']
                )

            # Save for learning
            if save_output and self.enable_learning:
                self._save_for_learning(output)

            return output

        except subprocess.TimeoutExpired:
            logger.error(f"Tool {tool_name} timed out")
            return {
                'tool': tool_name,
                'command': ' '.join(command),
                'exit_code': -1,
                'error': 'Command timed out',
                'success': False
            }
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return {
                'tool': tool_name,
                'command': ' '.join(command),
                'exit_code': -1,
                'error': str(e),
                'success': False
            }

    def _analyze_output(self, tool_name: str, output: str,
                        ai_tasks: List[str]) -> Dict[str, Any]:
        """Analyze tool output with AI"""
        analysis = {}

        for task in ai_tasks:
            try:
                result = self.ai_analyzer.analyze(
                    tool_name=tool_name,
                    task=task,
                    content=output
                )
                analysis[task] = result
            except Exception as e:
                logger.error(f"AI analysis failed for {task}: {e}")
                analysis[task] = {'error': str(e)}

        return analysis

    def _save_for_learning(self, output: Dict[str, Any]):
        """Save tool output for continuous learning"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tool_name = output['tool']
        filename = f"{tool_name}_{timestamp}.json"
        filepath = self.learning_data_path / filename

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)

        logger.debug(f"Saved output for learning: {filepath}")

    def pipe_workflow(self, tools_sequence: List[Dict[str, Any]],
                      enable_ai: bool = True) -> Dict[str, Any]:
        """
        Execute a pipeline of tools (pipe workflow)

        Args:
            tools_sequence: List of dicts with 'tool' and 'args' keys
            enable_ai: Enable AI analysis at each step

        Returns:
            Dict with all pipeline results
        """
        pipeline_results = {
            'steps': [],
            'total_duration': 0,
            'success': True
        }

        # Pass output from one tool to next
        previous_output = None

        for step_idx, step in enumerate(tools_sequence):
            tool_name = step['tool']
            args = step.get('args', [])

            # If this step uses output from previous step
            if previous_output and '{output}' in str(args):
                args = [arg.replace('{output}', previous_output) for arg in args]

            result = self.execute_tool(tool_name, args, enable_ai=enable_ai)
            pipeline_results['steps'].append(result)

            if not result['success']:
                pipeline_results['success'] = False
                break

            # Use stdout as input for next tool
            previous_output = result.get('stdout', '')

        return pipeline_results

    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a supported tool"""
        if tool_name not in self.SUPPORTED_TOOLS:
            raise ValueError(f"Unsupported tool: {tool_name}")

        return self.SUPPORTED_TOOLS[tool_name]

    def list_supported_tools(self) -> List[str]:
        """List all supported security tools"""
        return list(self.SUPPORTED_TOOLS.keys())
