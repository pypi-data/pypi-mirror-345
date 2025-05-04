"""
Configuração de logging para o Mangaba.AI
"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """
    Configura o logging básico para o projeto
    
    Args:
        log_level: Nível de logging (default: INFO)
    """
    # Cria o diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configura o formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configura o handler para arquivo
    file_handler = logging.FileHandler(log_dir / "mangaba.log")
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Configura o handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configura o logger específico do projeto
    logger = logging.getLogger("mangaba")
    logger.setLevel(log_level)
    
    return logger 