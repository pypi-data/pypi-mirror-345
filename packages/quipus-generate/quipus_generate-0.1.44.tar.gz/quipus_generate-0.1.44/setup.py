from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quipus-generate",
    version="0.1.44",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "quipus-generate=amautta_project.cli:main",
        ],
    },
    install_requires=[
        "inflection",
        "ruamel.yaml",
    ],
    description="Generador de proyectos FastAPI con arquitectura Hexagonal.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Juan David Corrales Saldarriaga",
    author_email="sistemas@amauttasistems.com",
    license="Proprietary",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
