"""
Testes para os componentes principais do Mangaba.AI
"""
import pytest
import asyncio
from mangaba.core.agent import Agent
from mangaba.core.memory import ContextualMemory
from mangaba.core.model import GeminiModel
from mangaba.core.tools import GoogleSearchTool
from mangaba.core.task import Task
from mangaba.core.crew import Crew

@pytest.fixture
def memory():
    return ContextualMemory()

@pytest.fixture
def model():
    return GeminiModel()

@pytest.fixture
def search_tool():
    return GoogleSearchTool()

@pytest.fixture
def agent(memory, model, search_tool):
    return Agent(
        name="TestAgent",
        role="Test Role",
        model=model,
        tools=[search_tool],
        memory=memory
    )

@pytest.fixture
def task(agent):
    return Task(
        description="Test task description",
        agent=agent
    )

@pytest.fixture
def crew(agent, task):
    return Crew(agents=[agent], tasks=[task])

def test_agent_initialization(agent):
    """Testa a inicialização correta de um agente"""
    assert agent.name == "TestAgent"
    assert agent.role == "Test Role"
    assert len(agent.tools) == 1
    assert isinstance(agent.memory, ContextualMemory)

def test_task_initialization(task):
    """Testa a inicialização correta de uma tarefa"""
    assert task.description == "Test task description"
    assert task.agent is not None

def test_crew_initialization(crew):
    """Testa a inicialização correta de uma equipe"""
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1

@pytest.mark.asyncio
async def test_crew_execution(crew):
    """Testa a execução de uma equipe"""
    result = await crew.run()
    assert result is not None

def test_memory_operations(memory):
    """Testa as operações básicas de memória"""
    memory.add("test_key", "test_value")
    assert memory.get("test_key") == "test_value"
    memory.clear()
    assert memory.get("test_key") is None

@pytest.mark.asyncio
async def test_model_generation(model):
    """Testa a geração de texto do modelo"""
    response = await model.generate("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_search_tool(search_tool):
    """Testa a funcionalidade de busca"""
    results = await search_tool.search("test query")
    assert isinstance(results, list)
    assert len(results) > 0 