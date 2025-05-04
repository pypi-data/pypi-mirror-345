"""
Configurações do Mangaba.AI
"""
import json
import os
from typing import Dict, Any
from pathlib import Path

class Config:
    """Configurações principais do sistema."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa as configurações a partir de um arquivo JSON."""
        self.config_path = config_path
        self.config = self._load_config()
        
        # Configurações de API
        self.API_KEYS = self.config["api_keys"]
        
        # Configurações de modelos
        self.MODELS = self.config["models"]
        
        # Configurações de agentes
        self.AGENT_CONFIG = {
            "max_concurrent_tasks": self.config["agents"]["max_concurrent_tasks"],
            "task_timeout": self.config["agents"]["task_timeout"],
            "memory_size": self.config["agents"]["memory_size"],
            "max_retries": self.config["agents"]["max_retries"]
        }
        
        # Configurações de memória
        self.MEMORY_CONFIG = {
            "max_size": self.config["memory"]["max_size"],
            "ttl": self.config["memory"]["ttl"],
            "cleanup_interval": self.config["memory"]["cleanup_interval"],
            "cache_size": self.config["memory"]["cache_size"]
        }
        
        # Configurações de comunicação
        self.COMMUNICATION_CONFIG = {
            "max_messages": self.config["communication"]["max_messages"],
            "message_ttl": self.config["communication"]["message_ttl"],
            "priority_levels": self.config["communication"]["priority_levels"]
        }
        
        # Configurações de fusão de contexto
        self.CONTEXT_FUSION_CONFIG = {
            "max_contexts": self.config["context_fusion"]["max_contexts"],
            "context_ttl": self.config["context_fusion"]["context_ttl"]
        }
        
        # Configurações de workflow
        self.WORKFLOW_CONFIG = {
            "max_agents": self.config["workflow"]["max_agents"],
            "max_tasks": self.config["workflow"]["max_tasks"],
            "timeout": self.config["workflow"]["timeout"],
            "retry_attempts": self.config["workflow"]["retry_attempts"]
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega as configurações do arquivo JSON."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão
            return {
                "api_keys": {
                    "gemini": os.getenv("GEMINI_API_KEY", ""),
                    "openai": os.getenv("OPENAI_API_KEY", ""),
                    "anthropic": os.getenv("ANTHROPIC_API_KEY", "")
                },
                "models": {
                    "gemini": {
                        "model_name": "gemini-pro",
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.95
                    },
                    "openai": {
                        "model_name": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    "anthropic": {
                        "model_name": "claude-3-opus-20240229",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                "agents": {
                    "max_concurrent_tasks": 5,
                    "task_timeout": 300,
                    "memory_size": 1000,
                    "max_retries": 3
                },
                "memory": {
                    "max_size": 1000,
                    "ttl": 3600,
                    "cleanup_interval": 300,
                    "cache_size": 100
                },
                "communication": {
                    "max_messages": 1000,
                    "message_ttl": 3600,
                    "priority_levels": 5
                },
                "context_fusion": {
                    "max_contexts": 10,
                    "context_ttl": 1800
                },
                "workflow": {
                    "max_agents": 10,
                    "max_tasks": 100,
                    "timeout": 3600,
                    "retry_attempts": 3
                }
            }
    
    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Retorna as configurações do modelo especificado."""
        return self.MODELS.get(model_type, {})
    
    def get_api_key(self, model_type: str) -> str:
        """Retorna a chave de API do modelo especificado."""
        return self.API_KEYS.get(model_type, "")
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Retorna as configurações de agentes."""
        return self.AGENT_CONFIG
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Retorna as configurações de memória."""
        return self.MEMORY_CONFIG
    
    def get_communication_config(self) -> Dict[str, Any]:
        """Retorna as configurações de comunicação."""
        return self.COMMUNICATION_CONFIG
    
    def get_context_fusion_config(self) -> Dict[str, Any]:
        """Retorna as configurações de fusão de contexto."""
        return self.CONTEXT_FUSION_CONFIG
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Retorna as configurações de workflow."""
        return self.WORKFLOW_CONFIG 