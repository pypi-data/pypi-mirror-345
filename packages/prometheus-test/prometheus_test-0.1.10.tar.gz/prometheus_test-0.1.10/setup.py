from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="prometheus-test",
    version="0.1.10",
    description="Test framework for Prometheus tasks",
    author="Laura Abro",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "pymongo>=4.0.0",
        "PyYAML>=6.0.0",
        "typing-extensions>=4.0.0",
    ],
    python_requires=">=3.8",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
