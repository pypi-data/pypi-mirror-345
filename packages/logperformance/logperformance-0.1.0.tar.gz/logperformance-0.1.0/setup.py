from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(
    name="wrapper-panda-video",
    version="0.0.1",
    license="MIT License",
    author="Gregorio Honorato",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="greghono@gmail.com",
    keywords="logger",
    description="Classe que implementa um logger com funções de log performance, log error, log warning, log info, log debug, log critical, log alert, log emergency, log warning, log error, log critical, log alert, log emergency",
    packages=["src"],
    install_requires=["colorlog"],
)
