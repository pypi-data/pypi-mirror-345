import pytest
import time
import asyncio
from typing import List, Dict, Any
from mangaba.core import Agent, Memory, Workflow
from mangaba.utils.logging import logger

class TestPerformance:
    @pytest.fixture
    def agent(self):
        return Agent(
            name="test_agent",
            memory_size=1000,
            max_retries=3
        )
    
    @pytest.fixture
    def memory(self):
        return Memory(
            max_size=10000,
            ttl=3600,
            cleanup_interval=300,
            cache_size=1000
        )
    
    @pytest.fixture
    def workflow(self):
        return Workflow(
            max_agents=10,
            max_tasks=100,
            timeout=3600,
            retry_attempts=3
        )
    
    @pytest.mark.asyncio
    async def test_agent_performance(self, agent):
        """Testa o desempenho do agente em processamento de tarefas."""
        start_time = time.time()
        
        # Teste de processamento sequencial
        tasks = [f"Task {i}" for i in range(100)]
        results = []
        
        for task in tasks:
            result = await agent.process_task(task)
            results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Agent sequential processing: {len(tasks)} tasks in {duration:.2f}s")
        assert duration < 10.0  # Espera-se que 100 tarefas sejam processadas em menos de 10 segundos
    
    @pytest.mark.asyncio
    async def test_memory_performance(self, memory):
        """Testa o desempenho do sistema de memória."""
        start_time = time.time()
        
        # Teste de escrita e leitura
        items = [f"Item {i}" for i in range(1000)]
        
        # Escrita
        for item in items:
            await memory.store(item, f"key_{item}")
        
        # Leitura
        for item in items:
            result = await memory.retrieve(f"key_{item}")
            assert result == item
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Memory operations: {len(items)*2} operations in {duration:.2f}s")
        assert duration < 5.0  # Espera-se que 2000 operações sejam realizadas em menos de 5 segundos
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, workflow):
        """Testa o desempenho do workflow com múltiplos agentes."""
        start_time = time.time()
        
        # Criação de agentes
        agents = [Agent(f"agent_{i}") for i in range(10)]
        
        # Distribuição de tarefas
        tasks = [f"Task {i}" for i in range(100)]
        results = []
        
        for task in tasks:
            result = await workflow.execute_task(task, agents)
            results.append(result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Workflow execution: {len(tasks)} tasks with {len(agents)} agents in {duration:.2f}s")
        assert duration < 15.0  # Espera-se que 100 tarefas com 10 agentes sejam processadas em menos de 15 segundos
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, agent, memory, workflow):
        """Testa operações concorrentes no sistema."""
        start_time = time.time()
        
        async def process_task(task: str):
            await agent.process_task(task)
            await memory.store(task, f"key_{task}")
            return await workflow.execute_task(task, [agent])
        
        tasks = [f"Task {i}" for i in range(50)]
        results = await asyncio.gather(*[process_task(task) for task in tasks])
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Concurrent operations: {len(tasks)} tasks in {duration:.2f}s")
        assert duration < 8.0  # Espera-se que 50 tarefas concorrentes sejam processadas em menos de 8 segundos 