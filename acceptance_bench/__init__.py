"""
acceptance-bench: A Robust LLM Evaluation Framework

A comprehensive benchmarking framework for evaluating LLMs with:
- Multi-prompt variation testing
- Temperature sweeping
- Multi-metric evaluation
- Provider-based architecture for easy model integration
"""

__version__ = "0.1.0"

from acceptance_bench.core.base_model import BaseModel, ModelResponse
from acceptance_bench.core.task import Task
from acceptance_bench.core.runner import BenchmarkRunner
from acceptance_bench.evaluation.judge import Judge, EvaluationResult
from acceptance_bench.models import load_model

__all__ = [
    "BaseModel",
    "ModelResponse",
    "Task",
    "BenchmarkRunner",
    "Judge",
    "EvaluationResult",
    "load_model",
]

