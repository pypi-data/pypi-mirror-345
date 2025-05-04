"""
Exemplo completo do sistema Mangaba.AI
"""
import asyncio
import json
from mangaba import MangabaAI

async def main():
    # Cria configuração
    config = {
        "api_keys": {
            "gemini": "sua_chave_api"
        },
        "models": {
            "gemini": {
                "temperature": 0.7,
                "top_k": 40,
                "top_p": 0.95
            },
            "secondary": {
                "model_name": "modelo_secundario",
                "temperature": 0.5,
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

    # Salva configuração
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    # Inicializa o sistema
    mangaba = MangabaAI("config.json")

    # Valida API Key
    if not await mangaba.validate_api_key():
        print("Erro: API Key inválida")
        return

    # Cria agentes
    researcher = mangaba.create_agent(
        name="pesquisador",
        role="Pesquisador",
        goal="Realizar pesquisas"
    )

    analyst = mangaba.create_agent(
        name="analista",
        role="Analista",
        goal="Analisar dados"
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

    # Executa tarefas
    results = await mangaba.execute([task1, task2])

    # Exibe resultados
    for task, result in results.items():
        print(f"Tarefa: {task}")
        print(f"Resultado: {result}\n")

    # Limpa recursos
    await mangaba.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 