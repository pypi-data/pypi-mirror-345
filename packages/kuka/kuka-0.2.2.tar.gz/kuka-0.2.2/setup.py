from setuptools import setup, find_packages

setup(
    name="kuka",
    version="0.2.2",
    author="tenoriolms",
    description="Personal library for EDA, data modeling, and ML modeling analysis/interpretation",
    long_description='',#open("README.md").read(),  # Descrição longa
    long_description_content_type="text/markdown",  # Para suportar Markdown
    url="https://github.com/tenoriolms/kuka_lib", # Repositório do projeto
    packages=find_packages(),  # Encontra automaticamente subpacotes
    install_requires=[
        'numpy', 
        'pandas', 
        'matplotlib',
        'scipy',
        'sklearn',
        'graphviz',
        'optuna',
        'pathlib',
        ],  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True, #For include text .txt files
)