from setuptools import setup,find_packages


with open("README.md","r") as file:
    description = file.read()

setup(
    name="grpc_orchestrator",
    version="0.0.4",
    author="Ron Saroeun",
    author_email="ronsaroeun668@gmail.com",
    url="https://github.com/bunrongGithub/grpc_orchestrator/tree/backup/simple_python_sdk",
    long_description=description,
    long_description_content_type="text/markdown"

)