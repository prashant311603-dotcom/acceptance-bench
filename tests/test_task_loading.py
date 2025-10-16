"""Tests for task loading and registry."""

import pytest
from acceptance_bench.tasks.task_registry import TaskRegistry
from acceptance_bench.core.task import Task


def test_task_registry_initialization():
    """Test that TaskRegistry can be initialized."""
    registry = TaskRegistry(task_set_version="v1")
    assert registry.task_set_version == "v1"


def test_load_tasks():
    """Test loading tasks from registry."""
    registry = TaskRegistry(task_set_version="v1")
    tasks = registry.load_tasks()
    
    assert isinstance(tasks, list)
    # Should have at least the example task
    assert len(tasks) >= 1
    
    # First task should be a Task object
    if tasks:
        assert isinstance(tasks[0], Task)
        assert hasattr(tasks[0], 'task_id')
        # assert hasattr(tasks[0], 'base_prompt')


def test_task_has_required_fields():
    """Test that loaded tasks have required fields."""
    registry = TaskRegistry(task_set_version="v1")
    tasks = registry.load_tasks()
    
    if tasks:
        task = tasks[0]
        assert task.task_id is not None
        assert task.category is not None
        # assert task.base_prompt is not None
        assert isinstance(task.prompt_variations, list)
        assert isinstance(task.required_elements, list)
        assert isinstance(task.bonus_elements, list)


def test_task_generate_prompts():
    """Test that tasks can generate prompt variations."""
    registry = TaskRegistry(task_set_version="v1")
    tasks = registry.load_tasks()
    
    if tasks:
        task = tasks[0]
        prompts = task.generate_prompts()
        
        assert isinstance(prompts, list)
        assert len(prompts) > 0
        
        # Each prompt should have required fields
        for prompt_data in prompts:
            assert 'prompt' in prompt_data
            assert 'type' in prompt_data
            assert 'task_id' in prompt_data


def test_filter_tasks_by_category():
    """Test filtering tasks by category."""
    registry = TaskRegistry(task_set_version="v1")
    
    # Load all tasks
    all_tasks = registry.load_tasks()
    
    # Load only technical_instruction tasks
    tech_tasks = registry.load_tasks(
        categories=["technical_instruction"]
    )
    
    assert isinstance(tech_tasks, list)
    # All filtered tasks should be technical_instruction
    for task in tech_tasks:
        assert task.category == "technical_instruction"

