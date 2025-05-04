# mangaba_ai/core/models.py
# Definições das classes principais do Mangaba.AI

import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import google.generativeai as genai
from googlesearch import search
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from .protocols import A2AProtocol, MCPProtocol
from abc import ABC, abstractmethod
from openai import AsyncOpenAI
import anthropic

# ContextualMemory (com memória global)
@dataclass
class ContextualMemory:
    """Sistema de memória contextual para agentes."""
    memory: Dict[str, Any] = None

    def __post_init__(self):
        self.memory = self.memory or {}

    def add(self, key: str, value: Any) -> None:
        """Adiciona um item à memória."""
        self.memory[key] = value

    def get(self, key: str) -> Any:
        """Recupera um item da memória."""
        return self.memory.get(key)

    def clear(self) -> None:
        """Limpa a memória."""
        self.memory.clear()

class AIModel(ABC):
    """Interface base para modelos de IA."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Gera texto com base no prompt."""
        pass

class GeminiModel(AIModel):
    """Implementação do modelo Gemini."""
    
    def __init__(self, api_key: str, **kwargs):
        self.model = genai.GenerativeModel('gemini-pro')
        genai.configure(api_key=api_key)
        self.config = kwargs

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await asyncio.to_thread(
            self.model.generate_content,
                prompt,
            **{**self.config, **kwargs}
            )
            return response.text

class OpenAIModel(AIModel):
    """Implementação do modelo OpenAI."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4", **kwargs):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name
        self.config = kwargs

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            **{**self.config, **kwargs}
        )
        return response.choices[0].message.content

class AnthropicModel(AIModel):
    """Implementação do modelo Claude."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-opus-20240229", **kwargs):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model_name = model_name
        self.config = kwargs

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
            **{**self.config, **kwargs}
        )
        return response.content[0].text

class ModelFactory:
    """Fábrica para criação de modelos de IA."""
    
    @staticmethod
    def create_model(model_type: str, api_key: str, **kwargs) -> AIModel:
        """Cria uma instância do modelo especificado."""
        models = {
            "gemini": GeminiModel,
            "openai": OpenAIModel,
            "anthropic": AnthropicModel
        }
        
        if model_type not in models:
            raise ValueError(f"Modelo {model_type} não suportado")
        
        return models[model_type](api_key, **kwargs)

# GoogleSearchTool (busca real)
class GoogleSearchTool:
    """Ferramenta de busca no Google."""
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search(self, query: str, num_results: int = 5) -> List[str]:
        """Realiza uma busca no Google."""
        results = await asyncio.to_thread(
            search,
            query,
            num_results=num_results,
            stop=num_results
        )
        return list(results)

# Agent
class Agent:
    """Agente autônomo para execução de tarefas."""
    def __init__(
        self,
        name: str,
        role: str,
        model: GeminiModel,
        secondary_model: Optional[SecondaryModel] = None,
        tools: List[GoogleSearchTool] = None,
        memory: ContextualMemory = None,
        protocol: A2AProtocol = None
    ):
        self.name = name
        self.role = role
        self.model = model
        self.secondary_model = secondary_model
        self.tools = tools or []
        self.memory = memory or ContextualMemory()
        self.protocol = protocol or A2AProtocol()
        
        # Registra handlers de mensagens
        self.protocol.register_handler(self.name, self.handle_message)

    async def handle_message(self, message):
        """Processa mensagens recebidas."""
        # Implementa a lógica de processamento de mensagens
        if "task" in message.content:
            await self.execute(message.content["task"])

    async def execute(self, task: str) -> str:
        """Executa uma tarefa."""
        # Usa o modelo principal
        response = await self.model.generate(task)
        
        # Se necessário, usa o modelo secundário
        if self.secondary_model and "complex" in task.lower():
            secondary_response = await self.secondary_model.generate(task)
            response = f"{response}\n\nSecondary Analysis:\n{secondary_response}"
        
        # Usa as ferramentas se necessário
        for tool in self.tools:
            if "search" in task.lower():
                results = await tool.search(task)
                response += f"\n\nSearch Results:\n{results}"
        
        # Armazena o resultado na memória
        self.memory.add("ultima_execucao", response)

        return response

# Task
@dataclass
class Task:
    """Representa uma tarefa a ser executada."""
    description: str
    agent: "Agent"
    priority: int = 0
    dependencies: Optional[List["Task"]] = None
    result: Optional[str] = None
    executed: bool = False  # Controle para evitar reexecução

    def get_dependencies_results(self) -> List[str]:
        if not self.dependencies:
            return []
        return [task.result for task in self.dependencies if task.result]

# SecondaryModel (modelo secundário)
class SecondaryModel:
    """Modelo secundário para tarefas específicas."""
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel('gemini-pro')
        genai.configure(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(self, prompt: str) -> str:
        """Gera texto com base no prompt."""
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt
        )
        return response.text

# Crew (com controle de execução)
class Crew:
    """Equipe de agentes trabalhando em conjunto."""
    def __init__(self, agents: List[Agent], tasks: List[Task]):
        self.agents = agents
        self.tasks = tasks
        self.protocol = A2AProtocol()

    async def run(self) -> Dict[str, Any]:
        """Executa todas as tarefas da equipe."""
        results = {}
        
        # Configura comunicação entre agentes
        for agent in self.agents:
            agent.protocol = self.protocol
        
        # Executa tarefas em paralelo
        task_coroutines = [task.execute() for task in self.tasks]
        await asyncio.gather(*task_coroutines)
        
        # Coleta resultados
        for task in self.tasks:
            results[task.description] = task.result
        
        return results
