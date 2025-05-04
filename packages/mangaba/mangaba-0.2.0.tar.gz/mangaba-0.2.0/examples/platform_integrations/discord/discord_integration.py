"""
Exemplo de integração com Discord usando A2A e MCP
"""
import os
import asyncio
from typing import Dict, Any, List
import logging
import discord
from discord.ext import commands

from mangaba.core.models import Agent, Task
from mangaba.core.protocols import A2AProtocol, MCPProtocol
from mangaba.config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Bot do Discord com integração A2A e MCP."""
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa o bot do Discord."""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        
        self.config = Config(config_path)
        self.a2a_protocol = A2AProtocol()
        self.mcp_protocol = MCPProtocol()
        
        # Inicializa agentes
        self.agents: Dict[str, Agent] = {}
        self._initialize_agents()
        
        # Registra eventos
        self.add_listener(self.on_ready)
        self.add_listener(self.on_message)
    
    def _initialize_agents(self):
        """Inicializa os agentes para integração com Discord."""
        # Agente de moderação
        self.agents["moderator"] = Agent(
            name="moderator",
            role="Moderador",
            goal="Moderar conversas e manter a ordem",
            model=self.config.get_model("gemini"),
            protocol=self.a2a_protocol
        )
        
        # Agente de assistência
        self.agents["assistant"] = Agent(
            name="assistant",
            role="Assistente",
            goal="Ajudar usuários e responder perguntas",
            model=self.config.get_model("openai"),
            protocol=self.a2a_protocol
        )
        
        # Registra agentes no MCP
        for agent in self.agents.values():
            self.mcp_protocol.add_agent(agent)
    
    async def on_ready(self):
        """Evento disparado quando o bot está pronto."""
        logger.info(f"Bot conectado como {self.user}")
    
    async def on_message(self, message: discord.Message):
        """Evento disparado quando uma mensagem é recebida."""
        if message.author == self.user:
            return
        
        try:
            # Cria contexto para o MCP
            context = {
                "platform": "discord",
                "channel": message.channel.name,
                "user": message.author.name,
                "message": message.content
            }
            
            # Fusão de contexto inicial
            await self.mcp_protocol.fuse_context(
                prompt=f"Mensagem do Discord: {message.content}",
                context=context
            )
            
            # Cria tarefa para o moderador
            moderation_task = Task(
                description=f"Moderar mensagem de {message.author.name}",
                agent=self.agents["moderator"]
            )
            
            # Executa a moderação
            moderation = await moderation_task.agent.execute(moderation_task)
            
            # Se a mensagem for inapropriada
            if "inappropriate" in moderation.lower():
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, sua mensagem foi removida por violar as regras."
                )
                return
            
            # Cria tarefa para o assistente
            assistance_task = Task(
                description=f"Responder mensagem de {message.author.name}",
                agent=self.agents["assistant"]
            )
            
            # Executa a assistência
            response = await assistance_task.agent.execute(assistance_task)
            
            # Fusão de contexto com resultados
            await self.mcp_protocol.fuse_context(
                prompt=f"Moderação: {moderation}\nResposta: {response}",
                context=context
            )
            
            # Envia a resposta
            await message.channel.send(response)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
    
    async def cleanup(self):
        """Limpa recursos da integração."""
        await self.mcp_protocol.clear_context()
        self.agents.clear()
        await self.close()

async def main():
    """Função principal de execução."""
    try:
        # Inicializa o bot
        bot = DiscordBot()
        
        # Executa o bot
        await bot.start(os.getenv("DISCORD_TOKEN"))
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        raise
    finally:
        await bot.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 