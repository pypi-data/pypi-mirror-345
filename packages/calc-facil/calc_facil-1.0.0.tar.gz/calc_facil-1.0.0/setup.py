from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    descricao_longa = f.read()

setup(
    name='calc-facil',
    version='1.0.0',
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
    install_requires=[],
    entry_points={
        'console_scripts': [
            'calc-facil=calc_facil.cli:main'
        ]
    }
)
