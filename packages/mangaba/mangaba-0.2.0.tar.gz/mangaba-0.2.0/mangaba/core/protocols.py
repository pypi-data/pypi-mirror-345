"""
Protocolos de comunicação e fusão de contexto do Mangaba.AI.
"""
from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass
from .models import Agent, GeminiModel, SecondaryModel

@dataclass
class Message:
    """Mensagem entre agentes."""
    sender: str
    receiver: str
    content: Any
    priority: int = 1
    ttl: int = 3600  # segundos
    timestamp: float = 0.0

class A2AProtocol:
    """Protocolo de comunicação entre agentes."""
    
    def __init__(self):
        self.messages: Dict[str, List[Message]] = {}
        self.handlers: Dict[str, List[callable]] = {}
    
    async def send(self, sender: str, receiver: str, content: Any, priority: int = 1, ttl: int = 3600):
        """Envia uma mensagem entre agentes."""
        if receiver not in self.messages:
            self.messages[receiver] = []
        
        message = Message(
            sender=sender,
            receiver=receiver,
            content=content,
            priority=priority,
            ttl=ttl,
            timestamp=asyncio.get_event_loop().time()
        )
        
        self.messages[receiver].append(message)
        self.messages[receiver].sort(key=lambda m: m.priority, reverse=True)
        
        # Notifica handlers
        if receiver in self.handlers:
            for handler in self.handlers[receiver]:
                await handler(message)
    
    async def receive(self, agent: str) -> List[Message]:
        """Recebe mensagens para um agente."""
        current_time = asyncio.get_event_loop().time()
        
        if agent not in self.messages:
            return []
        
        # Remove mensagens expiradas
        self.messages[agent] = [
            msg for msg in self.messages[agent]
            if current_time - msg.timestamp < msg.ttl
        ]
        
        return self.messages[agent]
    
    def register_handler(self, agent: str, handler: callable):
        """Registra um handler para mensagens de um agente."""
        if agent not in self.handlers:
            self.handlers[agent] = []
        self.handlers[agent].append(handler)
    
    def unregister_handler(self, agent: str, handler: callable):
        """Remove um handler de um agente."""
        if agent in self.handlers:
            self.handlers[agent] = [
                h for h in self.handlers[agent]
                if h != handler
            ]

class MCPProtocol:
    """Protocolo de fusão de contexto entre modelos."""
    
    def __init__(self):
        self.models: List[GeminiModel] = []
        self.agents: List[Agent] = []
        self.context: Dict[str, Any] = {}
    
    def add_model(self, model: GeminiModel):
        """Adiciona um modelo ao protocolo."""
        if model not in self.models:
            self.models.append(model)
    
    def add_agent(self, agent: Agent):
        """Adiciona um agente ao protocolo."""
        if agent not in self.agents:
            self.agents.append(agent)
    
    async def fuse_context(self, prompt: str) -> str:
        """Funde o contexto dos modelos para um prompt."""
        if not self.models:
            return prompt
        
        # Obtém respostas de todos os modelos
        responses = await asyncio.gather(*[
            model.generate(prompt)
            for model in self.models
        ])
        
        # Combina as respostas
        combined_context = "\n\n".join(responses)
        
        # Atualiza o contexto
        self.context["ultima_fusao"] = {
            "prompt": prompt,
            "contexto": combined_context,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return combined_context
    
    async def get_context(self, key: Optional[str] = None) -> Any:
        """Obtém o contexto armazenado."""
        if key is None:
            return self.context
        return self.context.get(key)
    
    def clear_context(self):
        """Limpa o contexto armazenado."""
        self.context.clear()
    
    async def update_agents(self):
        """Atualiza o contexto de todos os agentes."""
        for agent in self.agents:
            if hasattr(agent, "memory"):
                agent.memory.add("contexto_combinado", self.context) 