import asyncio
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
from pathlib import Path

# Ensure we use absolute imports to avoid module issues
from acceptance_bench.core.base_model import BaseModel
from acceptance_bench.core.task import Task
from acceptance_bench.evaluation.judge import Judge, EvaluationResult


class BenchmarkRunner:
    """Main benchmark orchestrator"""

    def __init__(
        self,
        models: List[BaseModel],
        judge: Judge,
        task_set_version: str = "v1",
        parallel_tasks: int = 1,  # Default to 1 to avoid rate limiting
    ):
        self.models = models
        self.judge = judge
        self.task_set_version = task_set_version
        self.parallel_tasks = parallel_tasks

    async def run_benchmark(
        self,
        task_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run full benchmark suite"""

        # Load tasks
        tasks = self._load_tasks(task_ids, categories)

        # Initialize results storage
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "task_set_version": self.task_set_version,
                "num_tasks": len(tasks),
                "num_models": len(self.models),
                "temperature_sweep": self.judge.temperature_sweep,
            },
            "model_results": {},
        }

        # Run evaluation for each model
        for model_idx, model in enumerate(self.models, 1):
            print(f"\n{'='*70}")
            print(f"Evaluating model {model_idx}/{len(self.models)}: {model.name}")
            print(f"{'='*70}")

            model_results = await self._evaluate_model(model, tasks)

            # Calculate aggregate metrics
            print(f"\nCalculating aggregate metrics for {model.name}...")
            aggregate = self._calculate_model_aggregate(model_results)
            print(f"  Overall mean score: {aggregate.get('overall_mean', 0):.2f}")

            # Convert EvaluationResult objects to dicts for JSON serialization
            serializable_results = []
            for result in model_results:
                serializable_results.append({
                    "task_id": result.task_id,
                    "model_name": result.model_name,
                    "category": result.category,
                    "scores": result.scores,
                    "best_temperature": result.best_temperature,
                    "best_response": result.best_response,
                    "all_attempts": result.all_attempts,
                    "prompt_variation_scores": result.prompt_variation_scores,
                    "aggregate_stats": result.aggregate_stats,
                })
            
            results["model_results"][model.name] = {
                "task_results": serializable_results,
                "aggregate": aggregate,
            }
            
            # Save intermediate results after each model (safety backup)
            print(f"\nSaving intermediate results for {model.name}...")
            self._save_results(results, suffix=f"_{model.name.replace('/', '_')}")

        # Generate comparative analysis
        print(f"\n{'='*70}")
        print("Generating comparative analysis...")
        results["comparative"] = self._comparative_analysis(results)

        # Save results
        print(f"\nSaving results...")
        self._save_results(results)
        
        print(f"\n{'='*70}")
        print("✓ Benchmark complete!")
        print(f"{'='*70}\n")

        return results

    async def _evaluate_model(
        self, model: BaseModel, tasks: List[Task]
    ) -> List[EvaluationResult]:
        """Evaluate a model on all tasks"""

        # Create semaphore for parallel task limiting
        semaphore = asyncio.Semaphore(self.parallel_tasks)

        async def eval_task(task_idx, task):
            async with semaphore:
                print(f"\nTask {task_idx}/{len(tasks)}: {task.task_id}")
                result = await self.judge.evaluate_with_sweep(
                    task, model, task.system_prompt
                )
                print(f"  ✓ Best score: {sum(result.scores.values()) / len(result.scores):.2f} at temp={result.best_temperature}")
                return result

        # Run tasks in parallel with limit
        results = await asyncio.gather(*[eval_task(i+1, task) for i, task in enumerate(tasks)])

        return results
    
    def _load_tasks(
        self,
        task_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None
    ) -> List[Task]:
        """Load tasks from task registry."""
        from acceptance_bench.tasks.task_registry import TaskRegistry
        
        registry = TaskRegistry(task_set_version=self.task_set_version)
        return registry.load_tasks(task_ids=task_ids, categories=categories)
    
    def _calculate_model_aggregate(
        self, results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        """Calculate aggregate metrics for a model."""
        import statistics
        
        if not results:
            return {}
        
        # Collect all scores
        all_scores = []
        all_temps = []
        metric_scores = {}
        
        for result in results:
            for metric, score in result.scores.items():
                if metric not in metric_scores:
                    metric_scores[metric] = []
                metric_scores[metric].append(score)
            
            avg_score = Judge.effective_score(result.scores)
            all_scores.append(avg_score)
            all_temps.append(result.best_temperature)
        
        # Calculate aggregates
        aggregate = {
            "overall_mean": statistics.mean(all_scores),
            "overall_median": statistics.median(all_scores),
            "overall_stdev": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "best_temperature_mode": statistics.mode(all_temps) if all_temps else None,
        }
        
        # Per-metric aggregates
        for metric, scores in metric_scores.items():
            aggregate[f"{metric}_mean"] = statistics.mean(scores)
            aggregate[f"{metric}_median"] = statistics.median(scores)
        
        return aggregate
    
    def _comparative_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative analysis across models."""
        model_results = results.get("model_results", {})
        
        if len(model_results) < 2:
            return {"note": "Comparative analysis requires at least 2 models"}
        
        # Compare overall means
        rankings = []
        for model_name, data in model_results.items():
            aggregate = data.get("aggregate", {})
            overall_mean = aggregate.get("overall_mean", 0)
            rankings.append({
                "model": model_name,
                "overall_score": overall_mean
            })
        
        rankings.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return {
            "rankings": rankings,
            "winner": rankings[0]["model"] if rankings else None
        }
    
    def _save_results(self, results: Dict[str, Any], suffix: str = "") -> str:
        """Save results to disk."""
        from config.settings import Settings
        
        settings = Settings()
        output_dir = Path(settings.results_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = results["metadata"]["timestamp"].replace(":", "-")
        output_file = output_dir / f"results_{timestamp}{suffix}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to: {output_file}")
        return str(output_file)
