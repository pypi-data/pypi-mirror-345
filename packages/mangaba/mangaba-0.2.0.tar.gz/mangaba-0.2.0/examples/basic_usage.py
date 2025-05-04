#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemplo básico de uso do Mangaba.AI
"""
import asyncio
import os
from dotenv import load_dotenv
from mangaba.main import MangabaAI

# Carrega as variáveis de ambiente
load_dotenv()

async def main():
    """Função principal do exemplo."""
    try:
        # Verifica se as chaves de API estão configuradas
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY não configurada no arquivo .env")
        
        # Inicializa o Mangaba.AI
        mangaba = MangabaAI()
        
        # Define as tarefas a serem executadas
        tasks = [
            {
                "type": "researcher",
                "description": "Pesquisar sobre os últimos avanços em IA generativa"
            },
            {
                "type": "analyzer",
                "description": "Analisar os impactos desses avanços na indústria"
            },
            {
                "type": "writer",
                "description": "Escrever um relatório sobre os resultados da análise"
            }
        ]
        
        # Executa as tarefas
        print("Iniciando execução das tarefas...")
        results = await mangaba.execute(tasks)
        
        # Exibe os resultados
        print("\nResultados:")
        for task, result in results.items():
            print(f"\nTarefa: {task}")
            print(f"Resultado: {result}")
            
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 