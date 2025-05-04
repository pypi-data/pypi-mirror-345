"""
Exemplo de integração com Jira usando A2A e MCP
"""
import os
import asyncio
from typing import Dict, Any, List
import logging
from jira import JIRA
from jira.resources import Issue

from mangaba.core.models import Agent, Task
from mangaba.core.protocols import A2AProtocol, MCPProtocol
from mangaba.config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JiraIntegration:
    """Integração com Jira usando A2A e MCP."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa a integração com Jira."""
        self.config = Config(config_path)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        
        # Inicializa cliente Jira
        self.jira_client = JIRA(
            server=os.getenv("JIRA_SERVER"),
            basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN"))
        )
        
        # Inicializa agentes
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa os agentes para integração com Jira."""
        # Agente de análise de tarefas
        self.agents["task_analyzer"] = Agent(
            name="task_analyzer",
            role="Analista de Tarefas",
            goal="Analisar e priorizar tarefas",
            model=self.config.get_model("gemini"),
            protocol=self.a2a_protocol
        )
        
        # Agente de sugestões
        self.agents["suggester"] = Agent(
            name="suggester",
            role="Sugestor",
            goal="Sugerir melhorias e próximos passos",
            model=self.config.get_model("openai"),
            protocol=self.a2a_protocol
        )
        
        # Registra agentes no MCP
        for agent in self.agents.values():
            self.mcp_protocol.add_agent(agent)
    
    async def analyze_issue(self, issue_key: str):
        """Analisa uma issue do Jira."""
        try:
            # Obtém a issue
            issue = self.jira_client.issue(issue_key)
            
            # Cria contexto para o MCP
            context = {
                "platform": "jira",
                "issue_key": issue_key,
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
            }
            
            # Fusão de contexto inicial
            await self.mcp_protocol.fuse_context(
                prompt=f"Análise da issue {issue_key}: {issue.fields.summary}",
                context=context
            )
            
            # Cria tarefa para o analista
            analysis_task = Task(
                description=f"Analisar issue {issue_key}",
                agent=self.agents["task_analyzer"]
            )
            
            # Executa a análise
            analysis = await analysis_task.agent.execute(analysis_task)
            
            # Cria tarefa para o sugestor
            suggestion_task = Task(
                description=f"Sugerir melhorias para a issue {issue_key}",
                agent=self.agents["suggester"]
            )
            
            # Executa as sugestões
            suggestions = await suggestion_task.agent.execute(suggestion_task)
            
            # Fusão de contexto com resultados
            await self.mcp_protocol.fuse_context(
                prompt=f"Análise: {analysis}\nSugestões: {suggestions}",
                context=context
            )
            
            # Cria comentário na issue
            comment = f"""
### Análise da Issue
{analysis}

### Sugestões de Melhorias
{suggestions}
            """
            
            self.jira_client.add_comment(issue_key, comment)
            
            logger.info(f"Análise da issue {issue_key} concluída")
            
        except Exception as e:
            logger.error(f"Erro ao analisar issue: {e}")
            raise
    
    async def monitor_project(self, project_key: str):
        """Monitora um projeto para novas issues."""
        try:
            while True:
                # Obtém issues recentes
                issues = self.jira_client.search_issues(
                    f'project = {project_key} AND updated >= -1d'
                )
                
                for issue in issues:
                    # Verifica se já foi analisada
                    context = await self.mcp_protocol.get_context(
                        f"jira:issue:{issue.key}"
                    )
                    
                    if not context:
                        # Analisa a issue
                        await self.analyze_issue(issue.key)
                
                # Aguarda antes da próxima verificação
                await asyncio.sleep(300)  # 5 minutos
                
        except Exception as e:
            logger.error(f"Erro ao monitorar projeto: {e}")
            raise
    
    async def cleanup(self):
        """Limpa recursos da integração."""
        await self.mcp_protocol.clear_context()
        self.agents.clear()

async def main():
    """Função principal de execução."""
    try:
        # Inicializa a integração
        integration = JiraIntegration()
        
        # Monitora o projeto
        await integration.monitor_project("PROJ")
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 