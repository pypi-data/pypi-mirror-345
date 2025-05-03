# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools import setup
from setuptools import find_packages

from mapafiscal import __version__
    
def parse_requirements(filename):
    with open(filename, encoding='utf-16') as f:
        return f.read().splitlines()

setup(name='mapafiscal',
    version=__version__,
    license='MIT',
    author='Ismael Nascimento',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author_email='ismaelnjr@icloud.com',
    keywords='mapa fiscal tributario receita federal',
    description=u'Gerador de mapa fiscal com base em regras fiscais',
    url='https://github.com/ismaelnjr/mapafiscal-project.git',
    packages=find_packages(),
    include_package_data=True,  # Incluir dados definidos no MANIFEST.in
    package_data={
        '': ['*.json', '*.xlsx'],  # Inclui arquivos JSON e XLSX em todos os diretórios
    },
    install_requires=[
        # Adicione as dependências aqui
        "openpyxl"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'mapafiscal=build_cenario:main',  # Substitua pelo comando principal
        ],
    }
)



