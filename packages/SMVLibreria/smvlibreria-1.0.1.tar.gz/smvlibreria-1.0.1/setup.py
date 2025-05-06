import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Información de los autores
author_names = "@may, @juan"
author_email = "may@example.com, juan@example.com"

setuptools.setup(
    name="SMVLibreria",  # nombre de la librería (como se instalará)
    version="1.0.1",
    author=author_names,
    author_email=author_email,
    description="Librería para analizar datos de seguridad vial de SEMOVI: conteo por periodos y tasas de crecimiento",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/greenmay99/semovi_libreria",
    project_urls={
        "Repositorio": "https://github.com/greenmay99/semovi_libreria",
        "Documentación": "https://github.com/greenmay99/semovi_libreria#readme",
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "pandas",
        "requests"
    ],
)
