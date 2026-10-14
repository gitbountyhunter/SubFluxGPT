"""
Model evaluation and continuous learning system.
Tracks model performance over time and provides metrics for improvement.
"""

import os
import logging
import yaml
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import torch

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluates model performance and tracks improvement over time."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize model evaluator.
        
        Args:
            config_path: Path to configuration file
        """
        # Handle relative path
        if not os.path.isabs(config_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, config_path)
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Evaluation metrics storage
        self.metrics_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'metrics'
        )
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Metrics file
        self.metrics_file = os.path.join(self.metrics_dir, 'model_metrics.json')
        
        # Load existing metrics
        self.metrics = self._load_metrics()
        
        logger.info("Initialized ModelEvaluator")
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                return {}
        return {}
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Saved metrics to {self.metrics_file}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def evaluate_model(
        self,
        model_name: str,
        model_type: str,
        test_prompts: List[str],
        expected_outputs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a model on test prompts.
        
        Args:
            model_name: Name of the model
            model_type: Type of model (llama2c, nanogpt, gpt2, llmc)
            test_prompts: List of test prompts
            expected_outputs: Optional list of expected outputs for comparison
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating model: {model_name} ({model_type})")
        
        results = {
            'model_name': model_name,
            'model_type': model_type,
            'timestamp': datetime.utcnow().isoformat(),
            'num_test_prompts': len(test_prompts),
            'metrics': {}
        }
        
        # For now, this is a placeholder
        # In a real implementation, you would:
        # 1. Load the model
        # 2. Generate responses for each prompt
        # 3. Calculate metrics (perplexity, BLEU, ROUGE, etc.)
        # 4. Compare with expected outputs if provided
        
        # Placeholder metrics
        results['metrics'] = {
            'avg_loss': np.random.uniform(2.0, 4.0),
            'perplexity': np.random.uniform(7.0, 50.0),
            'avg_generation_time_ms': np.random.uniform(100, 500),
            'success_rate': np.random.uniform(0.8, 1.0)
        }
        
        # Store metrics
        if model_name not in self.metrics:
            self.metrics[model_name] = []
        
        self.metrics[model_name].append(results)
        self._save_metrics()
        
        logger.info(f"Evaluation complete for {model_name}")
        return results
    
    def compare_models(self, model_names: List[str]) -> Dict[str, Any]:
        """
        Compare multiple models based on their evaluation metrics.
        
        Args:
            model_names: List of model names to compare
            
        Returns:
            Comparison results
        """
        logger.info(f"Comparing models: {model_names}")
        
        comparison = {
            'timestamp': datetime.utcnow().isoformat(),
            'models': {},
            'ranking': []
        }
        
        for model_name in model_names:
            if model_name in self.metrics and self.metrics[model_name]:
                latest_eval = self.metrics[model_name][-1]
                comparison['models'][model_name] = latest_eval['metrics']
            else:
                logger.warning(f"No metrics found for {model_name}")
                comparison['models'][model_name] = None
        
        # Simple ranking by perplexity (lower is better)
        ranked = sorted(
            [(name, metrics['perplexity']) for name, metrics in comparison['models'].items() if metrics],
            key=lambda x: x[1]
        )
        comparison['ranking'] = [item[0] for item in ranked]
        
        logger.info(f"Model ranking: {comparison['ranking']}")
        return comparison
    
    def get_improvement_trend(self, model_name: str) -> Dict[str, Any]:
        """
        Get improvement trend for a model over time.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Trend analysis
        """
        if model_name not in self.metrics or len(self.metrics[model_name]) < 2:
            logger.warning(f"Insufficient data for trend analysis: {model_name}")
            return {'error': 'Insufficient data'}
        
        evaluations = self.metrics[model_name]
        
        # Calculate trends
        perplexities = [e['metrics']['perplexity'] for e in evaluations]
        losses = [e['metrics']['avg_loss'] for e in evaluations]
        
        trend = {
            'model_name': model_name,
            'num_evaluations': len(evaluations),
            'perplexity_trend': {
                'start': perplexities[0],
                'end': perplexities[-1],
                'improvement': perplexities[0] - perplexities[-1],
                'improvement_percent': ((perplexities[0] - perplexities[-1]) / perplexities[0]) * 100
            },
            'loss_trend': {
                'start': losses[0],
                'end': losses[-1],
                'improvement': losses[0] - losses[-1],
                'improvement_percent': ((losses[0] - losses[-1]) / losses[0]) * 100
            }
        }
        
        logger.info(f"Trend analysis for {model_name}: {trend}")
        return trend
    
    def should_retrain(self, model_name: str, threshold: float = 0.1) -> bool:
        """
        Determine if a model should be retrained based on performance degradation.
        
        Args:
            model_name: Name of the model
            threshold: Performance degradation threshold (default 10%)
            
        Returns:
            True if retraining is recommended
        """
        if model_name not in self.metrics or len(self.metrics[model_name]) < 2:
            return False
        
        trend = self.get_improvement_trend(model_name)
        
        # Check if perplexity has increased (performance degraded)
        if trend['perplexity_trend']['improvement'] < 0:
            degradation_percent = abs(trend['perplexity_trend']['improvement_percent'])
            if degradation_percent > threshold * 100:
                logger.warning(f"Model {model_name} performance degraded by {degradation_percent:.2f}%")
                return True
        
        return False
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Returns:
            Report text
        """
        report_lines = [
            "# Model Evaluation Report",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "## Model Summary"
        ]
        
        for model_name, evaluations in self.metrics.items():
            if not evaluations:
                continue
            
            latest = evaluations[-1]
            report_lines.append(f"\n### {model_name}")
            report_lines.append(f"- Type: {latest['model_type']}")
            report_lines.append(f"- Evaluations: {len(evaluations)}")
            report_lines.append(f"- Latest Perplexity: {latest['metrics']['perplexity']:.2f}")
            report_lines.append(f"- Latest Loss: {latest['metrics']['avg_loss']:.2f}")
            
            if len(evaluations) >= 2:
                trend = self.get_improvement_trend(model_name)
                report_lines.append(f"- Perplexity Change: {trend['perplexity_trend']['improvement_percent']:.2f}%")
        
        report_text = '\n'.join(report_lines)
        
        # Save report
        report_file = os.path.join(self.metrics_dir, 'evaluation_report.md')
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Generated evaluation report: {report_file}")
        return report_text


def main():
    """Test model evaluator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate model performance")
    parser.add_argument('--model', type=str, required=True, help='Model name to evaluate')
    parser.add_argument('--type', type=str, required=True, 
                        choices=['llama2c', 'nanogpt', 'gpt2', 'llmc'],
                        help='Model type')
    parser.add_argument('--compare', type=str, nargs='+', help='Models to compare')
    parser.add_argument('--report', action='store_true', help='Generate evaluation report')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    evaluator = ModelEvaluator()
    
    if args.report:
        report = evaluator.generate_report()
        print(report)
    elif args.compare:
        comparison = evaluator.compare_models(args.compare)
        print(json.dumps(comparison, indent=2))
    else:
        # Placeholder evaluation
        test_prompts = [
            "Program: example.com\nReport title: XSS vulnerability",
            "Analyze the domain: test.com"
        ]
        results = evaluator.evaluate_model(args.model, args.type, test_prompts)
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
