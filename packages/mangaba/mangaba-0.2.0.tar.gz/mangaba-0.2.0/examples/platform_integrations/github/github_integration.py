"""
Exemplo de integração com GitHub usando A2A e MCP
"""
import os
import asyncio
from typing import Dict, Any, List
import logging
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest

from mangaba.core.models import Agent, Task
from mangaba.core.protocols import A2AProtocol, MCPProtocol
from mangaba.config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubIntegration:
    """Integração com GitHub usando A2A e MCP."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa a integração com GitHub."""
        self.config = Config(config_path)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        
        # Inicializa cliente GitHub
        self.github_client = Github(os.getenv("GITHUB_TOKEN"))
        
        # Inicializa agentes
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa os agentes para integração com GitHub."""
        # Agente de análise de código
        self.agents["code_reviewer"] = Agent(
            name="code_reviewer",
            role="Revisor de Código",
            goal="Analisar e revisar código",
            model=self.config.get_model("gemini"),
            protocol=self.a2a_protocol
        )
        
        # Agente de documentação
        self.agents["documenter"] = Agent(
            name="documenter",
            role="Documentador",
            goal="Gerar documentação",
            model=self.config.get_model("openai"),
            protocol=self.a2a_protocol
        )
        
        # Registra agentes no MCP
        for agent in self.agents.values():
            self.mcp_protocol.add_agent(agent)
    
    async def analyze_pull_request(self, repo_name: str, pr_number: int):
        """Analisa um Pull Request."""
        try:
            # Obtém o repositório e o PR
            repo = self.github_client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Cria contexto para o MCP
            context = {
                "platform": "github",
                "repository": repo_name,
                "pr_number": pr_number,
                "title": pr.title,
                "author": pr.user.login
            }
            
            # Fusão de contexto inicial
            await self.mcp_protocol.fuse_context(
                prompt=f"Análise do PR #{pr_number}: {pr.title}",
                context=context
            )
            
            # Obtém as mudanças do PR
            files = pr.get_files()
            changes = []
            for file in files:
                changes.append(f"{file.filename}: {file.patch}")
            
            # Cria tarefa para o revisor de código
            review_task = Task(
                description=f"Revisar código do PR #{pr_number}",
                agent=self.agents["code_reviewer"]
            )
            
            # Executa a revisão
            review = await review_task.agent.execute(review_task)
            
            # Cria tarefa para o documentador
            doc_task = Task(
                description=f"Gerar documentação para as mudanças do PR #{pr_number}",
                agent=self.agents["documenter"]
            )
            
            # Executa a documentação
            documentation = await doc_task.agent.execute(doc_task)
            
            # Fusão de contexto com resultados
            await self.mcp_protocol.fuse_context(
                prompt=f"Revisão: {review}\nDocumentação: {documentation}",
                context=context
            )
            
            # Cria comentário no PR
            comment = f"""
### Análise do Código
{review}

### Documentação das Mudanças
{documentation}
            """
            
            pr.create_issue_comment(comment)
            
            logger.info(f"Análise do PR #{pr_number} concluída")
            
        except Exception as e:
            logger.error(f"Erro ao analisar PR: {e}")
            raise
    
    async def monitor_repository(self, repo_name: str):
        """Monitora um repositório para novos PRs."""
        try:
            repo = self.github_client.get_repo(repo_name)
            
            while True:
                # Obtém PRs abertos
                prs = repo.get_pulls(state='open')
                
                for pr in prs:
                    # Verifica se já foi analisado
                    context = await self.mcp_protocol.get_context(
                        f"github:pr:{pr.number}"
                    )
                    
                    if not context:
                        # Analisa o PR
                        await self.analyze_pull_request(repo_name, pr.number)
                
                # Aguarda antes da próxima verificação
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"Erro ao monitorar repositório: {e}")
            raise
    
    async def cleanup(self):
        """Limpa recursos da integração."""
        await self.mcp_protocol.clear_context()
        self.agents.clear()

async def main():
    """Função principal de execução."""
    try:
        # Inicializa a integração
        integration = GitHubIntegration()
        
        # Monitora o repositório
        await integration.monitor_repository("seu-usuario/seu-repositorio")
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise
    finally:
        await integration.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 