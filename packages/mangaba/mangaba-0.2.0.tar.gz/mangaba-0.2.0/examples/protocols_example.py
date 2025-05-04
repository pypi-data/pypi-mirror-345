"""
Exemplo de uso dos protocolos A2A e MCP
"""
import asyncio
from mangaba.core.protocols import A2AProtocol, MCPProtocol
from mangaba.core.models import Agent, Task
from mangaba.config import Config

async def example_protocols():
    """Exemplo de uso dos protocolos A2A e MCP."""
    
    # Cria instâncias dos protocolos
    a2a_protocol = A2AProtocol()
    mcp_protocol = MCPProtocol()
    
    # Cria agentes
    agent1 = Agent(
        name="agente1",
        role="Pesquisador",
        goal="Realizar pesquisas sobre IA",
        protocol=a2a_protocol
    )
    
    agent2 = Agent(
        name="agente2",
        role="Analista",
        goal="Analisar resultados de pesquisas",
        protocol=a2a_protocol
    )
    
    # Registra agentes no MCP
    mcp_protocol.add_agent(agent1)
    mcp_protocol.add_agent(agent2)
    
    # Cria tarefas
    task1 = Task(
        description="Pesquisar sobre aprendizado por reforço",
        agent=agent1
    )
    
    task2 = Task(
        description="Analisar resultados da pesquisa sobre aprendizado por reforço",
        agent=agent2
    )
    
    # Adiciona contexto ao MCP
    await mcp_protocol.fuse_context(
        prompt="Aprendizado por reforço é uma técnica de IA",
        agent=agent1
    )
    
    # Envia mensagem entre agentes
    await a2a_protocol.send_message(
        sender="agente1",
        receiver="agente2",
        content="Encontrei informações relevantes sobre aprendizado por reforço",
        priority=2
    )
    
    # Executa tarefas
    result1 = await agent1.execute(task1)
    result2 = await agent2.execute(task2)
    
    # Fusão de contexto com resultados
    await mcp_protocol.fuse_context(
        prompt=result1,
        agent=agent1
    )
    
    await mcp_protocol.fuse_context(
        prompt=result2,
        agent=agent2
    )
    
    # Recupera contexto combinado
    combined_context = await mcp_protocol.get_context()
    print("Contexto combinado:", combined_context)
    
    # Limpa contexto
    await mcp_protocol.clear_context()

if __name__ == "__main__":
    asyncio.run(example_protocols()) 