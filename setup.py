from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name = "Insurance_Claims_Engine",
    version="0.1",
    author="Dev Mangukiya",
    packages=find_packages(),
    install_requires=requirements
)