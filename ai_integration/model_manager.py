"""
AI Model Manager - Competing AI Model System
Manages 30+ AI models with automatic selection, leaderboard, and learning
Models compete for workflows and learn which is best for each task
"""

import logging
import json
import time
import asyncio
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict
import random
import os

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Track model performance metrics"""
    model_id: str
    model_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_response_time: float = 0.0
    avg_quality_score: float = 0.0
    task_performance: Dict[str, float] = None  # Per-task performance
    last_used: str = None

    def __post_init__(self):
        if self.task_performance is None:
            self.task_performance = {}


@dataclass
class ModelTask:
    """Task for AI models"""
    task_id: str
    task_type: str
    description: str
    required_capabilities: List[str]
    priority: str
    input_data: Any
    context: Dict[str, Any]


class AIModelManager:
    """Manages competing AI models with leaderboard and learning"""

    def __init__(self, config_path: str = '.env'):
        """
        Initialize AI Model Manager

        Args:
            config_path: Path to .env file with API keys
        """
        self.config_path = config_path
        self.models = {}
        self.model_performance = {}
        self.task_queue = asyncio.Queue()
        self.leaderboard = {}
        self.running = False
        self.monitor_thread = None

        # Load API keys and models
        self._load_configuration()

        # Initialize performance tracking
        self._init_performance_tracking()

        # Load learning data
        self._load_learning_data()

    def _load_configuration(self):
        """Load API keys and model configurations"""
        from dotenv import load_dotenv
        load_dotenv(self.config_path)

        # OpenRouter Models
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key:
            self.models['openrouter'] = {
                'api_key': openrouter_key,
                'base_url': os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                'models': {
                    'primary': os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3-ultra-550b-a55b:free'),
                    'fallback': os.getenv('OPENROUTER_FALLBACK_MODEL', 'openrouter/free'),
                    'pool': [
                        os.getenv('OPENROUTER_MODEL_1', 'thinkingmachines/inkling-small:free'),
                        os.getenv('OPENROUTER_MODEL_2', 'nvidia/nemotron-3.5-lightning:free'),
                        os.getenv('OPENROUTER_MODEL_3', 'dots-studio/dots-3-note-preview:free'),
                        os.getenv('OPENROUTER_MODEL_4', 'nvidia/nemotron-3-ultra-550b-a55b:free'),
                        os.getenv('OPENROUTER_MODEL_5', 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free'),
                        os.getenv('OPENROUTER_MODEL_6', 'google/gemma-4-31b-it:free'),
                        os.getenv('OPENROUTER_MODEL_7', 'google/gemma-4-26b-a4b-it:free'),
                        os.getenv('OPENROUTER_MODEL_8', 'nvidia/nemotron-3-super-120b-a12b:free'),
                        os.getenv('OPENROUTER_MODEL_9', 'poolside/laguna-s-2.1:free'),
                        os.getenv('OPENROUTER_MODEL_10', 'poolside/laguna-xs-2.1:free'),
                        os.getenv('OPENROUTER_MODEL_11', 'cohere/north-mini-code:free'),
                        os.getenv('OPENROUTER_MODEL_12', 'nvidia/nemotron-3.5-content-safety:free'),
                    ]
                }
            }
            logger.info(f"Loaded OpenRouter with {len(self.models['openrouter']['models']['pool'])} models")

        # Mistral
        mistral_key = os.getenv('MISTRAL_API_KEY')
        if mistral_key:
            self.models['mistral'] = {
                'api_key': mistral_key,
                'base_url': 'https://api.mistral.ai/v1',
                'models': {
                    'primary': 'mistral-large-latest',
                    'pool': ['mistral-large-latest', 'mistral-medium', 'mistral-small-latest']
                }
            }
            logger.info("Loaded Mistral models")

        # Grok (xAI)
        grok_key = os.getenv('GROK_API_KEY')
        if grok_key:
            self.models['grok'] = {
                'api_key': grok_key,
                'base_url': 'https://api.x.ai/v1',
                'models': {
                    'primary': 'grok-beta',
                    'pool': ['grok-beta']
                }
            }
            logger.info("Loaded Grok models")

        # Gemini
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            self.models['gemini'] = {
                'api_key': gemini_key,
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'models': {
                    'primary': 'gemini-1.5-pro',
                    'pool': ['gemini-1.5-pro', 'gemini-1.5-flash']
                }
            }
            logger.info("Loaded Gemini models")

        # Initialize performance tracking for all models
        for provider, config in self.models.items():
            for model in config['models']['pool']:
                model_id = f"{provider}/{model}"
                self.model_performance[model_id] = ModelPerformance(
                    model_id=model_id,
                    model_name=model
                )

        logger.info(f"Total models loaded: {len(self.model_performance)}")

    def _init_performance_tracking(self):
        """Initialize performance tracking database"""
        self.performance_db_path = Path('data/learning/model_performance.json')
        self.performance_db_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_learning_data(self):
        """Load previous learning data"""
        if self.performance_db_path.exists():
            try:
                with open(self.performance_db_path, 'r') as f:
                    data = json.load(f)
                    for model_id, perf_data in data.items():
                        if model_id in self.model_performance:
                            self.model_performance[model_id] = ModelPerformance(**perf_data)
                logger.info(f"Loaded learning data for {len(data)} models")
            except Exception as e:
                logger.warning(f"Failed to load learning data: {e}")

    def _save_learning_data(self):
        """Save learning data"""
        try:
            data = {
                model_id: asdict(perf)
                for model_id, perf in self.model_performance.items()
            }
            with open(self.performance_db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")

    def select_best_model(self, task_type: str, capabilities: List[str] = None) -> str:
        """
        Select the best model for a task based on performance history

        Args:
            task_type: Type of task (e.g., 'vulnerability_analysis', 'payload_generation')
            capabilities: Required capabilities

        Returns:
            Model ID for the best model
        """
        capabilities = capabilities or []

        # Get models that have performed this task before
        candidates = []
        for model_id, perf in self.model_performance.items():
            if task_type in perf.task_performance:
                candidates.append((model_id, perf.task_performance[task_type]))

        # If we have candidates, pick the best one
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_model = candidates[0][0]
            logger.info(f"Selected best model for {task_type}: {best_model} (score: {candidates[0][1]:.2f})")
            return best_model

        # If no candidates, select based on capabilities and load balancing
        return self._select_model_by_capabilities(task_type, capabilities)

    def _select_model_by_capabilities(self, task_type: str, capabilities: List[str]) -> str:
        """Select model based on capabilities and load balancing"""
        # For now, use round-robin across all models
        all_models = list(self.model_performance.keys())
        # Use least-used model
        all_models.sort(key=lambda m: self.model_performance[m].total_calls)
        selected = all_models[0]
        logger.info(f"Selected model for {task_type} (first-time): {selected}")
        return selected

    async def execute_task(self, task: ModelTask) -> Dict[str, Any]:
        """
        Execute a task with the best available model

        Args:
            task: ModelTask to execute

        Returns:
            Task result with performance metrics
        """
        start_time = time.time()

        # Select best model
        model_id = self.select_best_model(task.task_type, task.required_capabilities)
        provider, model = model_id.split('/', 1)

        # Execute with selected model
        try:
            result = await self._call_model(provider, model, task)
            response_time = time.time() - start_time

            # Update performance
            self._update_performance(model_id, task.task_type, True, response_time, result.get('quality_score', 0.8))

            return {
                'success': True,
                'model_used': model_id,
                'result': result,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Model {model_id} failed: {e}")

            # Try fallback
            fallback = self._get_fallback_model(provider)
            if fallback:
                try:
                    result = await self._call_model(provider, fallback, task)
                    response_time = time.time() - start_time
                    self._update_performance(f"{provider}/{fallback}", task.task_type, True, response_time, result.get('quality_score', 0.7))
                    return {
                        'success': True,
                        'model_used': f"{provider}/{fallback}",
                        'result': result,
                        'response_time': response_time,
                        'timestamp': datetime.now().isoformat(),
                        'fallback': True
                    }
                except Exception as e2:
                    logger.error(f"Fallback also failed: {e2}")

            # Update performance for failure
            self._update_performance(model_id, task.task_type, False, response_time, 0.0)

            return {
                'success': False,
                'model_used': model_id,
                'error': str(e),
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }

    async def _call_model(self, provider: str, model: str, task: ModelTask) -> Dict[str, Any]:
        """Call a specific model API"""
        if provider == 'openrouter':
            return await self._call_openrouter(model, task)
        elif provider == 'mistral':
            return await self._call_mistral(model, task)
        elif provider == 'grok':
            return await self._call_grok(model, task)
        elif provider == 'gemini':
            return await self._call_gemini(model, task)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openrouter(self, model: str, task: ModelTask) -> Dict[str, Any]:
        """Call OpenRouter API"""
        import httpx

        config = self.models['openrouter']
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'HTTP-Referer': 'https://subfluxgpt.local',
            'X-Title': 'SubFluxGPT'
        }

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': self._get_system_prompt(task.task_type)},
                {'role': 'user', 'content': str(task.input_data)}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                'content': data['choices'][0]['message']['content'],
                'model': data['model'],
                'tokens_used': data.get('usage', {}).get('total_tokens', 0)
            }

    async def _call_mistral(self, model: str, task: ModelTask) -> Dict[str, Any]:
        """Call Mistral API"""
        import httpx

        config = self.models['mistral']
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': self._get_system_prompt(task.task_type)},
                {'role': 'user', 'content': str(task.input_data)}
            ],
            'temperature': 0.7
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                'content': data['choices'][0]['message']['content'],
                'model': data['model'],
                'tokens_used': data.get('usage', {}).get('total_tokens', 0)
            }

    async def _call_grok(self, model: str, task: ModelTask) -> Dict[str, Any]:
        """Call Grok (xAI) API"""
        import httpx

        config = self.models['grok']
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': self._get_system_prompt(task.task_type)},
                {'role': 'user', 'content': str(task.input_data)}
            ],
            'temperature': 0.7
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                'content': data['choices'][0]['message']['content'],
                'model': data['model'],
                'tokens_used': data.get('usage', {}).get('total_tokens', 0)
            }

    async def _call_gemini(self, model: str, task: ModelTask) -> Dict[str, Any]:
        """Call Gemini API"""
        import httpx

        config = self.models['gemini']
        headers = {'Content-Type': 'application/json'}

        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': self._get_system_prompt(task.task_type) + '\n\n' + str(task.input_data)}
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 1000
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config['base_url']}/{model}:generateContent?key={config['api_key']}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                'content': data['candidates'][0]['content']['parts'][0]['text'],
                'model': model,
                'tokens_used': data.get('usageMetadata', {}).get('totalTokenCount', 0)
            }

    def _get_system_prompt(self, task_type: str) -> str:
        """Get system prompt for task type"""
        prompts = {
            'vulnerability_analysis': "You are an expert security analyst. Analyze the input for security vulnerabilities and provide detailed findings.",
            'payload_generation': "You are an expert penetration tester. Generate security testing payloads for the given vulnerability type.",
            'threat_intel': "You are a threat intelligence analyst. Analyze the input for security threats and provide risk assessment.",
            'attack_path': "You are an expert security researcher. Identify potential attack chains and correlations.",
            'report_generation': "You are a professional security report writer. Generate clear, actionable vulnerability reports.",
            'command_suggestion': "You are an expert security tool operator. Suggest optimal commands for security testing.",
            'code_analysis': "You are an expert code auditor. Analyze code for security vulnerabilities.",
            'general': "You are a helpful AI assistant specialized in security research."
        }
        return prompts.get(task_type, prompts['general'])

    def _get_fallback_model(self, provider: str) -> Optional[str]:
        """Get fallback model for provider"""
        if provider == 'openrouter':
            return self.models['openrouter']['models']['fallback']
        return None

    def _update_performance(self, model_id: str, task_type: str, success: bool,
                          response_time: float, quality_score: float):
        """Update model performance metrics"""
        perf = self.model_performance[model_id]
        perf.total_calls += 1
        perf.last_used = datetime.now().isoformat()

        if success:
            perf.successful_calls += 1
            # Update average response time
            perf.avg_response_time = (perf.avg_response_time * (perf.successful_calls - 1) + response_time) / perf.successful_calls
            # Update task performance
            if task_type not in perf.task_performance:
                perf.task_performance[task_type] = quality_score
            else:
                # Exponential moving average
                alpha = 0.3
                perf.task_performance[task_type] = alpha * quality_score + (1 - alpha) * perf.task_performance[task_type]
        else:
            perf.failed_calls += 1

        # Save learning data periodically
        if perf.total_calls % 10 == 0:
            self._save_learning_data()

    def get_leaderboard(self, task_type: str = None) -> List[Dict[str, Any]]:
        """
        Get leaderboard of models

        Args:
            task_type: Filter by task type (optional)

        Returns:
            Sorted list of model performance
        """
        leaderboard = []

        for model_id, perf in self.model_performance.items():
            if task_type and task_type not in perf.task_performance:
                continue

            score = perf.task_performance.get(task_type, perf.avg_quality_score) if task_type else perf.avg_quality_score

            leaderboard.append({
                'model_id': model_id,
                'model_name': perf.model_name,
                'total_calls': perf.total_calls,
                'success_rate': perf.successful_calls / perf.total_calls if perf.total_calls > 0 else 0,
                'avg_response_time': perf.avg_response_time,
                'score': score,
                'last_used': perf.last_used
            })

        # Sort by score
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return leaderboard

    def start_leaderboard_monitor(self, update_interval: int = 5):
        """Start live leaderboard monitor in terminal"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._leaderboard_monitor_loop, args=(update_interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Leaderboard monitor started")

    def _leaderboard_monitor_loop(self, update_interval: int):
        """Leaderboard monitor loop"""
        import sys
        from datetime import datetime

        try:
            while self.running:
                # Clear screen (works on Unix)
                os.system('clear' if os.name != 'nt' else 'cls')

                print("=" * 80)
                print("🥷 SUBFLUXGPT AI MODEL LEADERBOARD - LIVE MONITOR")
                print("=" * 80)
                print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Total Models: {len(self.model_performance)}")
                print(f"Total API Calls: {sum(p.total_calls for p in self.model_performance.values())}")
                print("=" * 80)

                # Overall leaderboard
                print("\n📊 OVERALL PERFORMANCE LEADERBOARD")
                print("-" * 80)
                leaderboard = self.get_leaderboard()
                for i, model in enumerate(leaderboard[:10], 1):
                    print(f"{i:2d}. {model['model_id'][:50]:50s} | Score: {model['score']:.3f} | Calls: {model['total_calls']:4d} | Success: {model['success_rate']:.1%}")

                # Per-task leaderboards
                task_types = ['vulnerability_analysis', 'payload_generation', 'threat_intel', 'attack_path']
                for task in task_types:
                    task_leaderboard = self.get_leaderboard(task)
                    if task_leaderboard:
                        print(f"\n🎯 {task.upper().replace('_', ' ')} LEADERBOARD")
                        print("-" * 80)
                        for i, model in enumerate(task_leaderboard[:5], 1):
                            print(f"{i:2d}. {model['model_id'][:50]:50s} | Score: {model['score']:.3f} | Calls: {model['total_calls']:4d}")

                print("\n" + "=" * 80)
                print("Press Ctrl+C to stop monitor")
                print("=" * 80)

                time.sleep(update_interval)

        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user")
            self.running = False

    def stop_leaderboard_monitor(self):
        """Stop leaderboard monitor"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Leaderboard monitor stopped")

    def get_model_stats(self) -> Dict[str, Any]:
        """Get overall model statistics"""
        total_calls = sum(p.total_calls for p in self.model_performance.values())
        total_success = sum(p.successful_calls for p in self.model_performance.values())
        total_failed = sum(p.failed_calls for p in self.model_performance.values())

        return {
            'total_models': len(self.model_performance),
            'total_calls': total_calls,
            'total_success': total_success,
            'total_failed': total_failed,
            'overall_success_rate': total_success / total_calls if total_calls > 0 else 0,
            'providers': list(self.models.keys()),
            'learning_data_saved': self.performance_db_path.exists()
        }


def main():
    """Main entry point for testing"""
    manager = AIModelManager()

    # Test model selection
    print("Testing model selection...")
    best_model = manager.select_best_model('vulnerability_analysis')
    print(f"Best model for vulnerability_analysis: {best_model}")

    # Show stats
    stats = manager.get_model_stats()
    print(json.dumps(stats, indent=2))

    # Start leaderboard monitor
    print("\nStarting leaderboard monitor (Ctrl+C to stop)...")
    manager.start_leaderboard_monitor(update_interval=5)


if __name__ == '__main__':
    main()
