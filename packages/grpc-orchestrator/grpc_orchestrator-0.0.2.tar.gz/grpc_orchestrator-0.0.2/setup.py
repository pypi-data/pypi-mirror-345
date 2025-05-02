from setuptools import setup,find_packages


with open("README.md","r") as file:
    description = file.read()

setup(
    name="grpc_orchestrator",
    version="0.0.2",
    long_description=description,
    long_description_content_type="text/markdown"

)