from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="console-msg-jb",
    version="1.0.2",
    author="JBSILVA",
    author_email="jbsivla.dev@outlook.com",
    description="Imprime mensagens com cores personalizadas no terminal",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JBSilvaDev/console-msg",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)