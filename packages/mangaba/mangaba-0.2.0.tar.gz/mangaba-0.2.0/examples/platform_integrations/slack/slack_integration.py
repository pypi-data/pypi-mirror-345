"""
Exemplo de integração com Slack usando A2A e MCP
"""
import os
import asyncio
from typing import Dict, Any
import logging
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest

from mangaba.core.models import Agent, Task
from mangaba.core.protocols import A2AProtocol, MCPProtocol
from mangaba.config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SlackIntegration:
    """Integração com Slack usando A2A e MCP."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa a integração com Slack."""
        self.config = Config(config_path)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        
        # Inicializa cliente Slack
        self.slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.socket_client = SocketModeClient(
            app_token=os.getenv("SLACK_APP_TOKEN"),
            web_client=self.slack_client
        )
        
        # Registra handlers
        self.socket_client.socket_mode_request_listeners.append(self.handle_slack_message)
        
        # Inicializa agentes
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Inicializa os agentes para integração com Slack."""
        # Agente de suporte
        self.agents["support"] = Agent(
            name="support",
            role="Suporte",
            goal="Responder perguntas de usuários no Slack",
            model=self.config.get_model("gemini"),
            protocol=self.a2a_protocol
        )
        
        # Agente de análise
        self.agents["analyst"] = Agent(
            name="analyst",
            role="Analista",
            goal="Analisar conversas e gerar insights",
            model=self.config.get_model("openai"),
            protocol=self.a2a_protocol
        )
        
        # Registra agentes no MCP
        for agent in self.agents.values():
            self.mcp_protocol.add_agent(agent)
    
    async def handle_slack_message(self, client: SocketModeClient, req: SocketModeRequest):
        """Processa mensagens recebidas do Slack."""
        try:
            # Extrai informações da mensagem
            event = req.payload["event"]
            channel = event["channel"]
            text = event["text"]
            user = event["user"]
            
            # Cria contexto para o MCP
            context = {
                "platform": "slack",
                "channel": channel,
                "user": user,
                "message": text
            }
            
            # Fusão de contexto
            await self.mcp_protocol.fuse_context(
                prompt=f"Mensagem do Slack: {text}",
                context=context
            )
            
            # Cria tarefa para o agente de suporte
            task = Task(
                description=f"Responder mensagem do usuário {user}: {text}",
                agent=self.agents["support"]
            )
            
            # Executa a tarefa
            response = await task.agent.execute(task)
            
            # Envia resposta para o Slack
            await self.slack_client.chat_postMessage(
                channel=channel,
                text=response
            )
            
            # Cria tarefa para o agente de análise
            analysis_task = Task(
                description=f"Analisar conversa com usuário {user}",
                agent=self.agents["analyst"]
            )
            
            # Executa análise
            analysis = await analysis_task.agent.execute(analysis_task)
            
            # Armazena análise no contexto
            await self.mcp_protocol.fuse_context(
                prompt=f"Análise da conversa: {analysis}",
                context=context
            )
            
            # Responde ao Slack
            client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do Slack: {e}")
            client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
    
    async def start(self):
        """Inicia a integração com Slack."""
        try:
            # Conecta ao Slack
            await self.socket_client.connect()
            logger.info("Conectado ao Slack")
            
            # Mantém a conexão ativa
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Erro na integração com Slack: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Limpa recursos da integração."""
        await self.mcp_protocol.clear_context()
        self.agents.clear()
        await self.socket_client.disconnect()

async def main():
    """Função principal de execução."""
    try:
        # Inicializa a integração
        integration = SlackIntegration()
        
        # Inicia a integração
        await integration.start()
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 