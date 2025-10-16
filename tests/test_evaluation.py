"""Tests for evaluation and judge system."""

import pytest
from acceptance_bench.evaluation.judge import Judge
from acceptance_bench.core.task import Task


def test_judge_initialization():
    """Test that Judge can be initialized with mock model."""
    # Using a mock judge model (will fail if actually called)
    judge = Judge(
        judge_model=None,  # Mock for testing
        temperature_sweep=[0.3, 0.5, 1.0]
    )
    
    assert judge.temperature_sweep == [0.3, 0.5, 1.0]


def test_judge_default_temperature_sweep():
    """Test that Judge has default temperature sweep."""
    judge = Judge(judge_model=None)
    
    assert isinstance(judge.temperature_sweep, list)
    assert len(judge.temperature_sweep) > 0
    assert all(isinstance(t, float) for t in judge.temperature_sweep)


def test_check_bonus_elements():
    """Test bonus elements checking."""
    judge = Judge(judge_model=None)
    
    # Test with elements present
    response = "Make sure to wear safety goggles and follow security protocols"
    elements = ["safety", "security"]
    score = judge._check_bonus_elements(response, elements)
    
    assert score == 100.0  # Both elements found
    
    # Test with partial match
    elements = ["safety", "security", "caution"]
    score = judge._check_bonus_elements(response, elements)
    
    assert 60.0 < score < 70.0  # 2 out of 3 found
    
    # Test with no elements
    score = judge._check_bonus_elements(response, [])
    assert score == 0.0  # No elements = 0 score


def test_check_required_elements():
    """Test required elements checking."""
    judge = Judge(judge_model=None)
    
    response = "Configure port 80 for HTTP and port 443 for HTTPS"
    elements = ["port 80", "port 443", "HTTP", "HTTPS"]
    score = judge._check_required_elements(response, elements)
    
    assert score == 100.0  # All elements present
    
    # Test partial match
    elements = ["port 80", "port 443", "SSH"]
    score = judge._check_required_elements(response, elements)
    
    assert 60.0 < score < 70.0  # 2 out of 3 found


def test_build_judge_prompt():
    """Test that judge prompt is properly constructed."""
    judge = Judge(judge_model=None)
    
    task = Task(
        task_id="test_001",
        category="technical_instruction",
        system_prompt=None,
        prompt_variations=["Variation 1"],
        evaluation_criteria={
            "accuracy": ["is accurate"],
            "completeness": ["covers all points"]
        },
        reference_answers=None,
        required_elements=["element1", "element2"],
        bonus_elements=["bonus"],
        version="v1"
    )
    
    response = "Test response"
    prompt = judge._build_judge_prompt(response, task)
    
    # Check that prompt contains key elements
    assert "0-100 scale" in prompt
    assert "accuracy" in prompt.lower()
    assert "completeness" in prompt.lower()
    assert "element1" in prompt
    assert "element2" in prompt
    assert "bonus" in prompt


def test_parse_judge_scores():
    """Test parsing scores from judge response."""
    judge = Judge(judge_model=None)
    
    # Test with valid JSON
    judge_response = '{"accuracy": 85, "completeness": 90, "clarity": 80}'
    scores = judge._parse_judge_scores(judge_response)
    
    assert isinstance(scores, dict)
    assert scores["accuracy"] == 85.0
    assert scores["completeness"] == 90.0
    assert scores["clarity"] == 80.0
    
    # Test with invalid response (should return fallback)
    judge_response = "This is not valid JSON"
    scores = judge._parse_judge_scores(judge_response)
    
    assert isinstance(scores, dict)
    assert all(isinstance(v, float) for v in scores.values())


def test_calculate_statistics():
    """Test statistics calculation across attempts."""
    judge = Judge(judge_model=None)
    
    attempts = [
        {
            "prompt": "Test 1",
            "prompt_type": "paraphrase",
            "temperature": 0.3,
            "response": "Response 1",
            "scores": {"accuracy": 80.0, "completeness": 85.0},
            "latency_ms": 100
        },
        {
            "prompt": "Test 2",
            "prompt_type": "paraphrase",
            "temperature": 0.5,
            "response": "Response 2",
            "scores": {"accuracy": 90.0, "completeness": 88.0},
            "latency_ms": 120
        }
    ]
    
    stats = judge._calculate_statistics(attempts)
    
    assert "mean" in stats
    assert "median" in stats
    assert "stdev" in stats
    assert "by_prompt_type" in stats
    assert isinstance(stats["mean"], float)
    assert stats["mean"] > 0

