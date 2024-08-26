
from setuptools import setup, find_packages

setup(
    name="task_model",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.7",
)
