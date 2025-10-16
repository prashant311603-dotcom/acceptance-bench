"""
Report generation for benchmark results.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """Generate reports from benchmark results."""
    
    def generate(self, results: Dict[str, Any], output_dir: str) -> str:
        """
        Generate a report from benchmark results.
        
        Args:
            results: Benchmark results dictionary
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON results
        timestamp = results.get("metadata", {}).get("timestamp", datetime.now().isoformat())
        json_file = output_path / f"results_{timestamp.replace(':', '-')}.json"
        
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate Markdown report
        md_file = output_path / f"report_{timestamp.replace(':', '-')}.md"
        
        with open(md_file, 'w') as f:
            self._write_markdown_report(f, results)
        
        return str(md_file)
    
    def _write_markdown_report(self, f, results: Dict[str, Any]):
        """Write markdown format report."""
        metadata = results.get("metadata", {})
        
        # Header
        f.write("# acceptance-bench Results\n\n")
        f.write(f"**Generated:** {metadata.get('timestamp', 'N/A')}\n\n")
        f.write(f"**Task Set Version:** {metadata.get('task_set_version', 'N/A')}\n\n")
        f.write(f"**Number of Tasks:** {metadata.get('num_tasks', 0)}\n\n")
        f.write(f"**Number of Models:** {metadata.get('num_models', 0)}\n\n")
        f.write(f"**Temperature Sweep:** {metadata.get('temperature_sweep', [])}\n\n")
        
        # Rankings (if multiple models)
        comparative = results.get("comparative", {})
        if comparative and "rankings" in comparative:
            f.write("## 🏆 Model Rankings\n\n")
            f.write("| Rank | Model | Overall Score |\n")
            f.write("|------|-------|---------------|\n")
            for i, ranking in enumerate(comparative["rankings"], 1):
                f.write(f"| {i} | {ranking['model']} | {ranking['overall_score']:.2f} |\n")
            f.write("\n")
        
        # Model Results
        f.write("## Model Results\n\n")
        
        model_results = results.get("model_results", {})
        for model_name, model_data in model_results.items():
            f.write(f"### {model_name}\n\n")
            
            aggregate = model_data.get("aggregate", {})
            if aggregate:
                f.write("**Aggregate Metrics:**\n\n")
                
                # Highlight key metrics first
                f.write(f"- **Overall Mean Score**: {aggregate.get('overall_mean', 0):.2f}\n")
                f.write(f"- **Overall Median Score**: {aggregate.get('overall_median', 0):.2f}\n")
                f.write(f"- **Standard Deviation**: {aggregate.get('overall_stdev', 0):.2f}\n")
                
                # Per-criterion breakdowns
                f.write("\n**By Evaluation Criterion:**\n\n")
                criterion_metrics = {}
                for key, value in aggregate.items():
                    if key.endswith('_mean') and not key.startswith('overall'):
                        criterion = key.replace('_mean', '')
                        criterion_metrics[criterion] = {
                            'mean': value,
                            'median': aggregate.get(f"{criterion}_median", value)
                        }
                
                for criterion, metrics in sorted(criterion_metrics.items()):
                    f.write(f"- **{criterion.replace('_', ' ').title()}**: {metrics['mean']:.2f} (median: {metrics['median']:.2f})\n")
                
                f.write(f"\n- **Best Temperature Mode**: {aggregate.get('best_temperature_mode', 'N/A')}\n\n")
            
            # Task-by-task breakdown
            task_results = model_data.get("task_results", [])
            if task_results:
                f.write(f"**Task-by-Task Results ({len(task_results)} tasks):**\n\n")
                f.write("| Task ID | Category | Best Score | Best Temp | Compliance | Soft Refusal Avoidance |\n")
                f.write("|---------|----------|------------|-----------|------------|------------------------|\n")
                
                for result in task_results:
                    scores = result.get("scores", {})
                    avg_score = sum(v for k, v in scores.items() if k not in ['required_elements', 'bonus_elements']) / max(1, len([k for k in scores.keys() if k not in ['required_elements', 'bonus_elements']]))
                    compliance = scores.get("compliance", 0)
                    soft_refusal = scores.get("soft_refusal_avoidance", 0)
                    category = result.get("category", "N/A")
                    
                    f.write(f"| {result.get('task_id', 'N/A')} | {category} | {avg_score:.2f} | {result.get('best_temperature', 'N/A')} | {compliance:.1f} | {soft_refusal:.1f} |\n")
                f.write("\n")
        
        # Comparative Analysis
        if comparative:
            f.write("## 📊 Comparative Analysis\n\n")
            
            if "rankings" in comparative:
                winner = comparative.get("winner", "N/A")
                f.write(f"**Winner**: {winner}\n\n")
                
                # Calculate interesting comparisons
                if len(comparative["rankings"]) >= 2:
                    best = comparative["rankings"][0]
                    worst = comparative["rankings"][-1]
                    gap = best["overall_score"] - worst["overall_score"]
                    f.write(f"**Score Gap**: {gap:.2f} points between best and worst performing models\n\n")
            
            f.write("See detailed results in the JSON file for full attempt-by-attempt data.\n\n")
        
        f.write("---\n")
        f.write("*Generated by acceptance-bench*\n")

