#!/usr/bin/env python3
"""
acceptance-bench - Main benchmark runner

Usage:
    python run_benchmark.py --models gpt-4 claude-3 --tasks all
    python run_benchmark.py --models local_model --categories technical_instruction
    python run_benchmark.py --config custom_config.yaml
"""

import asyncio
import argparse
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from acceptance_bench.core.runner import BenchmarkRunner
from acceptance_bench.models import load_model
from acceptance_bench.evaluation.judge import Judge
from acceptance_bench.analysis.report import ReportGenerator
from config.settings import Settings, load_judge_config


async def main():
    parser = argparse.ArgumentParser(description="Run acceptance-bench evaluation")
    parser.add_argument("--models", nargs="+", required=True, help="Models to evaluate")
    parser.add_argument("--tasks", nargs="+", default=["all"], help="Task IDs or 'all'")
    parser.add_argument("--categories", nargs="+", help="Task categories to run")
    parser.add_argument("--system-prompt", help="Override default system prompt")
    parser.add_argument(
        "--temperatures", nargs="+", type=float, help="Temperature values to sweep"
    )
    parser.add_argument("--output", default="./results", help="Output directory")
    parser.add_argument(
        "--parallel", type=int, default=1, help="Number of parallel tasks (default: 1 to avoid rate limiting)"
    )

    args = parser.parse_args()
    settings = Settings()

    # Load models
    models = [load_model(name) for name in args.models]

    # Initialize judge (from models.yaml - SINGLE SOURCE OF TRUTH)
    judge_config = load_judge_config()
    judge_model = load_model(judge_config["model"])
    judge = Judge(
        judge_model=judge_model,
        temperature_sweep=args.temperatures or settings.temperature_sweep,
    )

    # Create runner
    runner = BenchmarkRunner(
        models=models,
        judge=judge,
        parallel_tasks=args.parallel,
    )

    # Run benchmark
    print(f"Starting acceptance-bench evaluation...")
    print(f"Models: {', '.join(args.models)}")
    print(f"Temperature sweep: {judge.temperature_sweep}")
    # print(f"System prompt: {runner.system_prompt[:50]}...")
    print(f"Parallel tasks: {args.parallel}")

    results = await runner.run_benchmark(
        task_ids=None if args.tasks == ["all"] else args.tasks,
        categories=args.categories,
    )

    # Generate report
    if settings.generate_report:
        report_gen = ReportGenerator()
        report_path = report_gen.generate(results, args.output)
        print(f"Report saved to: {report_path}")

    print("Benchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())
