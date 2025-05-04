import asyncio
import json
from pathlib import Path
from mangaba import MangabaAI

async def main():
    # Verifica se o arquivo de configuração existe
    config_path = Path("config.json")
    if not config_path.exists():
        print("Arquivo de configuração não encontrado!")
        print("Execute 'python setup.py' para configurar o sistema.")
        return

    # Carrega a configuração
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Inicializa o sistema
    print("Inicializando Mangaba.AI...")
    mangaba = MangabaAI()

    # Menu interativo
    while True:
        print("\n=== Menu Principal ===")
        print("1. Criar novo agente")
        print("2. Listar agentes existentes")
        print("3. Executar tarefa")
        print("4. Configurar integrações")
        print("5. Sair")

        choice = input("\nEscolha uma opção: ")

        if choice == "1":
            # Cria um novo agente
            nome = input("Nome do agente: ")
            papel = input("Papel do agente: ")
            objetivo = input("Objetivo do agente: ")
            
            agente = mangaba.criar_agente(
                nome=nome,
                papel=papel,
                objetivo=objetivo
            )
            print(f"Agente '{nome}' criado com sucesso!")

        elif choice == "2":
            # Lista agentes existentes
            agentes = mangaba.listar_agentes()
            if agentes:
                print("\nAgentes disponíveis:")
                for agente in agentes:
                    print(f"- {agente.nome}: {agente.papel}")
            else:
                print("Nenhum agente encontrado.")

        elif choice == "3":
            # Executa uma tarefa
            agentes = mangaba.listar_agentes()
            if not agentes:
                print("Nenhum agente disponível. Crie um agente primeiro.")
                continue

            print("\nAgentes disponíveis:")
            for i, agente in enumerate(agentes, 1):
                print(f"{i}. {agente.nome}")

            agente_idx = int(input("\nEscolha um agente (número): ")) - 1
            if agente_idx < 0 or agente_idx >= len(agentes):
                print("Opção inválida!")
                continue

            tarefa = input("Descrição da tarefa: ")
            resultado = await agentes[agente_idx].executar_tarefa(tarefa)
            print("\nResultado:")
            print(resultado)

        elif choice == "4":
            # Configura integrações
            print("\n=== Configuração de Integrações ===")
            print("1. Slack")
            print("2. GitHub")
            print("3. Jira")
            print("4. Discord")
            print("5. Voltar")

            integracao = input("\nEscolha uma integração: ")
            if integracao == "5":
                continue

            # Aqui você pode adicionar a lógica para configurar cada integração
            print("Funcionalidade em desenvolvimento...")

        elif choice == "5":
            print("Encerrando Mangaba.AI...")
            break

        else:
            print("Opção inválida!")

if __name__ == "__main__":
    asyncio.run(main()) 