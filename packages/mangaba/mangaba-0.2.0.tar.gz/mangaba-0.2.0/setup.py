"""
Setup configuration for Mangaba.AI
"""
from setuptools import setup, find_packages
import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
# Removendo a importação problemática
# from mangaba.config.assistant import run_config_assistant

# Garantir que as dependências básicas de build estejam instaladas
try:
    import pip
    print("[-] pip está instalado")
except ImportError:
    print("[!] pip não está instalado corretamente")

# Instalando dependências antes da build
DEPENDENCIES = [
    "google-generativeai>=0.8.3",
    "googlesearch-python>=1.2.1",
    "requests>=2.32.3",
    "aiohttp>=3.10.5",
    "tenacity>=8.5.0",
]

print("[+] Instalando dependências necessárias para a build...")
for dep in DEPENDENCIES:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", dep],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"  [+] {dep}")
    except subprocess.CalledProcessError:
        print(f"  [!] Falha ao instalar {dep}")

# Carrega o README para a descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

if __name__ == "__main__":
    # Comentando a chamada ao assistente de configuração que causa o erro
    # run_config_assistant()
    pass

setup(
    name="mangaba",
    version="0.2.0",
    description="Framework avançado para orquestração de equipes de agentes de IA autônomos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dheiver Santos, Gabriel Azevedo, Luiz Filho",
    author_email="dheiver.santos@gmail.com",
    url="https://github.com/dheiver2/mangaba_ai",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "mangaba=mangaba.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mangaba": ["config/*.json", "config/*.yaml"],
    },
)
