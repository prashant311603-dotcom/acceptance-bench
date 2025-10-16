"""
Task registry for loading and managing benchmark tasks.
"""

import json
from pathlib import Path
from typing import List, Optional
from acceptance_bench.core.task import Task


class TaskRegistry:
    """Registry for loading and managing benchmark tasks."""
    
    def __init__(self, task_set_version: str = "v1"):
        """
        Initialize task registry.
        
        Args:
            task_set_version: Version of task set to load (e.g., "v1", "v2")
        """
        self.task_set_version = task_set_version
        self.tasks_dir = Path(__file__).parent / "task_sets" / task_set_version
        self._tasks = None
    
    def load_tasks(
        self,
        task_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None
    ) -> List[Task]:
        """
        Load tasks from the registry.
        
        Args:
            task_ids: Specific task IDs to load (None = all)
            categories: Filter by categories (None = all)
            
        Returns:
            List of Task objects
        """
        if self._tasks is None:
            self._load_all_tasks()
        
        tasks = self._tasks
        
        # Filter by task IDs
        if task_ids:
            tasks = [t for t in tasks if t.task_id in task_ids]
        
        # Filter by categories
        if categories:
            tasks = [t for t in tasks if t.category in categories]
        
        return tasks
    
    def _load_all_tasks(self):
        """Load all tasks from the task set."""
        tasks_file = self.tasks_dir / "tasks.json"
        
        if not tasks_file.exists():
            # Return empty list if no tasks file exists yet
            self._tasks = []
            return
        
        with open(tasks_file, 'r') as f:
            tasks_data = json.load(f)
        
        self._tasks = []
        for task_data in tasks_data:
            category = task_data.get("category", "technical_instruction")
            
            task = Task(
                task_id=task_data["task_id"],
                category=category,
                system_prompt=task_data.get("system_prompt"),
                prompt_variations=task_data.get("prompt_variations", []),
                evaluation_criteria=task_data.get("evaluation_criteria", {}),
                reference_answers=task_data.get("reference_answers"),
                required_elements=task_data.get("required_elements", []),
                bonus_elements=task_data.get("bonus_elements", []),
                version=self.task_set_version
            )
            self._tasks.append(task)

