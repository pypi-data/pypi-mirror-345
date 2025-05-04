<p align="center">
  <img src="assets/img2.png" width="400" alt="Mangaba.AI logo">
</p>

<h1 align="center">Mangaba.AI</h1>
<p align="center"><i>Framework avançado para orquestração de equipes de agentes de IA autônomos.</i></p>

---

## Características

- Suporte a múltiplos modelos de IA (Gemini, OpenAI, Anthropic)
- Sistema de agentes autônomos
- Protocolos de comunicação A2A e MCP
- Sistema de memória contextual
- Integrações com plataformas externas (Slack, GitHub, Jira, Discord)
- Configuração flexível
- Interface interativa
- Documentação completa

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mangaba_ai.git
cd mangaba_ai
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o assistente de configuração:
```bash
python setup.py
```

O assistente irá guiá-lo através de:
- Configuração de APIs (Gemini, OpenAI, Anthropic)
  - Guia passo a passo para obter chaves de API
  - Links diretos para páginas de configuração
  - Validação de chaves
- Configuração de Modelos
  - Configurações padrão otimizadas
  - Opção para configuração personalizada
  - Ajustes de parâmetros
- Configuração de Integrações
  - Slack, GitHub, Jira, Discord
  - Guias específicos para cada plataforma
  - Validação de configurações

## Uso

### Interface Interativa

Para iniciar a interface interativa:
```bash
python -m mangaba_ai
```

A interface oferece:
- Criação de agentes
- Listagem de agentes existentes
- Execução de tarefas
- Configuração de integrações

### Uso Programático

```python
from mangaba_ai import MangabaAI

# Inicialize o sistema
mangaba = MangabaAI()

# Crie um agente
agente = mangaba.criar_agente(
    nome="pesquisador",
    papel="Pesquisador de informações",
    objetivo="Encontrar e analisar informações relevantes"
)

# Execute uma tarefa
resultado = await agente.executar_tarefa(
    "Pesquisar sobre inteligência artificial"
)

print(resultado)
```

## Documentação

A documentação completa está disponível em `docs/`:

- [Agentes](docs/agents.md)
- [Tarefas](docs/tasks.md)
- [Comunicação](docs/communication.md)
- [Memória](docs/memory.md)
- [Modelos](docs/models.md)
- [Fluxo de Trabalho](docs/workflow.md)
- [Configuração](docs/configuration.md)

## Exemplos

Exemplos de uso estão disponíveis em `examples/`:

- [Sistema Completo](examples/full_system_example.py)
- [Integrações](examples/platform_integrations/)

## Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição em `CONTRIBUTING.md`.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo `LICENSE` para detalhes.
