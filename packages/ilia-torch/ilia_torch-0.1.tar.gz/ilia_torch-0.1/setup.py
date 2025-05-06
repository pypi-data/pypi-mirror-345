from setuptools import setup, find_packages

setup(
    name="ilia-torch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "torchprofile",
        "codecarbon"
    ],
    author="Maxime Gloesener",
    author_email="max.gleu@gmail.com",
    description="torch benchmarking tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaximeGloesener/torch-benchmark",
)
