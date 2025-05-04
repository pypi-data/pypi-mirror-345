"""
Módulo principal do Mangaba.AI
"""
import asyncio
from typing import List, Dict, Any
import logging
from .core.models import Agent, Task, Crew, ModelFactory
from .core.protocols import A2AProtocol, MCPProtocol
from .config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MangabaAI:
    """Classe principal do Mangaba.AI."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa o sistema Mangaba.AI."""
        self.config = Config(config_path)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        self.agents: Dict[str, Agent] = {}
        
        # Inicializa modelos
        self.models = {}
        for model_type in self.config.MODELS:
            api_key = self.config.get_api_key(model_type)
            if api_key:
                model_config = self.config.get_model_config(model_type)
                self.models[model_type] = ModelFactory.create_model(
                    model_type,
                    api_key,
                    **model_config
                )
    
    async def validate_api_keys(self) -> bool:
        """Valida as chaves de API dos modelos."""
        for model_type, model in self.models.items():
            try:
                await model.generate("Teste de API")
                logger.info(f"API Key válida para {model_type}")
            except Exception as e:
                logger.error(f"Erro ao validar API Key para {model_type}: {e}")
                return False
        return True
    
    def create_agent(self, name: str, role: str, goal: str, model_type: str = "gemini") -> Agent:
        """Cria um novo agente."""
        if model_type not in self.models:
            raise ValueError(f"Modelo {model_type} não encontrado")
        
        agent = Agent(
            name=name,
            role=role,
            goal=goal,
            model=self.models[model_type],
            protocol=self.a2a_protocol
        )
        self.agents[name] = agent
        self.mcp_protocol.add_agent(agent)
        return agent
    
    def create_task(self, description: str, agent: Agent) -> Task:
        """Cria uma nova tarefa."""
        return Task(
            description=description,
            agent=agent
        )
    
    async def execute(self, tasks: List[Task]) -> Dict[str, str]:
        """Executa um conjunto de tarefas."""
        results = {}
        
        # Fusão de contexto inicial
        await self.mcp_protocol.fuse_context(
            prompt="Iniciando execução de tarefas"
        )
        
        # Executa tarefas
        for task in tasks:
            try:
                result = await task.agent.execute(task)
                results[task.description] = result
                
                # Fusão de contexto com resultado
                await self.mcp_protocol.fuse_context(
                    prompt=result,
                    agent=task.agent
                )
            except Exception as e:
                logger.error(f"Erro ao executar tarefa: {e}")
                results[task.description] = f"Erro: {e}"
        
        return results
    
    async def cleanup(self) -> None:
        """Limpa recursos do sistema."""
        await self.mcp_protocol.clear_context()
        self.agents.clear()
        for model in self.models.values():
            if hasattr(model, 'cleanup'):
                await model.cleanup()

async def main():
    """Função principal de execução."""
    try:
        # Inicializa o Mangaba.AI
        mangaba = MangabaAI()
        
        # Valida API Keys
        if not await mangaba.validate_api_keys():
            logger.error("Erro: API Keys inválidas")
            return
        
        # Cria agentes com diferentes modelos
        researcher = mangaba.create_agent(
            name="pesquisador",
            role="Pesquisador",
            goal="Realizar pesquisas",
            model_type="gemini"
        )
        
        analyst = mangaba.create_agent(
            name="analista",
            role="Analista",
            goal="Analisar dados",
            model_type="openai"
        )
        
        writer = mangaba.create_agent(
            name="escritor",
            role="Escritor",
            goal="Escrever resumos",
            model_type="anthropic"
        )
        
        # Cria tarefas
        task1 = mangaba.create_task(
            description="Pesquisar sobre IA generativa",
            agent=researcher
        )
        
        task2 = mangaba.create_task(
            description="Analisar os resultados da pesquisa",
            agent=analyst,
            dependencies=[task1]
        )
        
        task3 = mangaba.create_task(
            description="Escrever um resumo dos resultados",
            agent=writer,
            dependencies=[task2]
        )
        
        # Executa tarefas
        results = await mangaba.execute([task1, task2, task3])
        
        # Exibe resultados
        for task, result in results.items():
            logger.info(f"Tarefa: {task}")
            logger.info(f"Resultado: {result}\n")
            
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise
    finally:
        await mangaba.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 