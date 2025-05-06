from setuptools import setup, find_packages

setup(
    name="agensight",
    version="0.1.0",
    author="Deepesh Agrawal",
    packages=find_packages(),
    install_requires=[
        "openai",  
        "requests",
        "flask",  
    ],
    entry_points={
        "console_scripts": [
            "agensight=agensight.cli:main",
        ],
    },
    python_requires=">=3.7",
)