from setuptools import setup, find_packages

setup(
    name='kafka-tool-kit',
    version='1.0.0',
    description='A simple Kafka utility library using confluent-kafka',
    author='Triton Tech Labs.,',
    packages=find_packages(),
    install_requires=[
        'confluent-kafka>=2.3.0'
    ],
    python_requires='>=3.7',
)