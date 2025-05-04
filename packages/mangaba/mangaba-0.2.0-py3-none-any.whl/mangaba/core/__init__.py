"""
Módulo core do Mangaba.AI

Contém as classes principais para criação e gerenciamento de agentes AI.
"""

from mangaba.core.models import (
    ContextualMemory,
    GeminiModel,
    GoogleSearchTool,
    Agent,
    Task,
    Crew
)

__all__ = [
    'ContextualMemory',
    'GeminiModel',
    'GoogleSearchTool',
    'Agent',
    'Task',
    'Crew'
] 