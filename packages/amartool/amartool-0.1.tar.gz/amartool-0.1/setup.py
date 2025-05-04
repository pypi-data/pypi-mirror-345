
from setuptools import setup, find_packages
setup(
    name='amartool',
    version='0.1',
    description='A simple statistics tools package',
    Author='Sara',
    licence='MIT',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy"
    ],
    python_requires=">=3.6",
)