from setuptools import setup, find_packages
from pathlib import Path

# Lê o conteúdo do README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="Higwind0-sys-bank",
    version="3.0.1",
    description="Sistema bancário simples em Python usando POO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fernando Mafaciolli",
    author_email="mafaciolli@outlook.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'sistemabank=sistema_bancario.main:main'
        ]
    },
)
