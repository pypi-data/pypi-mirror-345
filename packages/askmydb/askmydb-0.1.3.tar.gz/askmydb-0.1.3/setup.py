from setuptools import setup, find_packages

setup(
    name='askmydb',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'openai',
        'ollama',
        'sqlalchemy',
        ],
    author='Shanthosh',
    author_email='shanthubolt@gmail.com',
    description='A natural language SQL generator with LLM integration',
    url='https://github.com/Msalways/Ask-My-DB',
    python_requires='>=3.7',
)
