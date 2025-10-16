from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Task:
    """Defines a single evaluation task"""

    task_id: str
    category: str
    system_prompt: Optional[str] = None
    prompt_variations: List[str] = field(default_factory=list)  # Different phrasings
    evaluation_criteria: Dict[str, List[str]] = field(default_factory=dict)
    reference_answers: Optional[List[str]] = None
    required_elements: List[str] = field(default_factory=list)  # Must mention these
    bonus_elements: List[str] = field(default_factory=list)  # Bonus terms for extra points
    version: str = "v1"

    def generate_prompts(self) -> List[Dict[str, Any]]:
        """Generate all prompt variations with metadata"""
        prompts = []

        # Use all prompt variations from tasks.json
        for variation in self.prompt_variations:
            prompts.append(
                {"prompt": variation, "type": "paraphrase", "task_id": self.task_id}
            )

        # Format variations (spacing, punctuation, etc.)
        # Instruction style variations
        # Few-shot variations if applicable

        return prompts
