from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    descricao_longa = f.read()

# Lê as dependências dos arquivos
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requerimentos = [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]

setup(
    name='calc-facil',
    version='0.2.0',
    author='Luiz Elias',
    author_email='luizelias8@gmail.com',
    description='Uma calculadora simples para operações básicas',
    long_description=descricao_longa,
    long_description_content_type='text/markdown',
    url='https://github.com/luizelias8/calc-facil',
    classifiers=[
        'Topic :: Education',
        'Natural Language :: Portuguese (Brazilian)',
        'Development Status :: 5 - Production/Stable'
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=requerimentos,
    entry_points={
        'console_scripts': [
            'calc-facil=calc_facil.cli:main'
        ]
    }
)
