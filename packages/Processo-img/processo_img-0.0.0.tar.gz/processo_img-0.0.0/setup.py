from setuptools import setup, find_packages

with open("README.md", "r") as f:
    pag_description = f.read()
    
with open("requirements.txt") as f:
    requeriments = f.read().splitlines()
    
setup(
    name="Processo_img",
    vesion="0.0.1",
    author="Amanda",
    author_email="amandascp11@gmail.com",
    description="Sei lá",
    long_description=pag_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MadixSZ",
    packages=find_packages(),
    install_requires= requeriments,
    python_requies= ">=3.8",
)