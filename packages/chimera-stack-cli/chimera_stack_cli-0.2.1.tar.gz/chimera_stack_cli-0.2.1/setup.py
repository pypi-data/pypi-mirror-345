from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chimera-stack-cli",
    version="0.2.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
        "pyyaml>=6.0.0",
        "colorama>=0.4.4",
        "docker>=6.0.0",
        "rich>=13.0.0",
        "questionary>=2.0.0",
        "jsonschema>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chimera=chimera.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Amir",
    author_email="amirofcodes@github.com",
    description="A template-based development environment manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Amirofcodes/ChimeraStack_CLI",
    project_urls={
        "Bug Tracker": "https://github.com/Amirofcodes/ChimeraStack_CLI/issues",
        "Documentation": "https://github.com/Amirofcodes/ChimeraStack_CLI#readme",
        "Source Code": "https://github.com/Amirofcodes/ChimeraStack_CLI",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
