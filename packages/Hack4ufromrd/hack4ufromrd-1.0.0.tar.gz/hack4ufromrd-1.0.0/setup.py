from setuptools import setup, find_packages

#Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "Hack4ufromrd",
    version = "1.0.0",
    package=find_packages(),
    install_requires=[],
    author = "Cedric Santana",
    description = "Una biblioteca para consultar los cursos de hack4u de S4vitar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://hack4u.io/",
)
