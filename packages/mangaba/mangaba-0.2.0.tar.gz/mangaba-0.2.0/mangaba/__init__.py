"""
Mangaba.AI - Framework de Automação com Agentes Inteligentes

Um framework Python para criação de equipes de agentes AI autônomos 
que colaboram para resolver tarefas complexas.
"""

__version__ = "0.1.0"

# Verificação e instalação automática de dependências
import importlib.util
import subprocess
import sys
import warnings

def _check_and_install_dependency(package_name, pip_name=None):
    """Verifica se um pacote está instalado e o instala se necessário."""
    if pip_name is None:
        pip_name = package_name
    
    if importlib.util.find_spec(package_name) is None:
        warnings.warn(
            f"Dependência '{package_name}' não encontrada. Instalando automaticamente...",
            ImportWarning
        )
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pip_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[+] {package_name} instalado com sucesso!")
        except subprocess.CalledProcessError:
            raise ImportError(
                f"Não foi possível instalar '{pip_name}' automaticamente. "
                f"Por favor, instale manualmente com 'pip install {pip_name}'"
            )

# Verificação de dependências principais
_check_and_install_dependency("google", "google-generativeai>=0.8.3")
_check_and_install_dependency("googlesearch", "googlesearch-python>=1.2.1")
_check_and_install_dependency("requests", "requests>=2.32.3")
_check_and_install_dependency("aiohttp", "aiohttp>=3.10.5")
_check_and_install_dependency("tenacity", "tenacity>=8.5.0")

# Importa as classes principais para facilitar o acesso direto
from mangaba.core.models import (
    ContextualMemory,
    GeminiModel,
    GoogleSearchTool,
    Agent,
    Task,
    Crew
) 