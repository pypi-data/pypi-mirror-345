from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="desafio_poo",
    version="0.0.1",
    author="Diego Alves",
    author_email="diegoalvesds@outlook.com",
    description="desafio poo",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Diego-Alvesds",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
