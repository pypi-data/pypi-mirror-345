"""
Testes básicos para o Mangaba.AI
"""
import pytest
import mangaba

def test_import():
    """Testa se o pacote pode ser importado"""
    assert mangaba is not None

def test_version():
    """Testa se a versão está definida"""
    assert hasattr(mangaba, '__version__')
    assert isinstance(mangaba.__version__, str)
    assert len(mangaba.__version__) > 0 