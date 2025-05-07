from setuptools import setup, find_packages

setup(
    name="Higwind0-sys-bank",
    version="3.0.0",
    description="Sistema bancário simples em Python usando POO",
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
