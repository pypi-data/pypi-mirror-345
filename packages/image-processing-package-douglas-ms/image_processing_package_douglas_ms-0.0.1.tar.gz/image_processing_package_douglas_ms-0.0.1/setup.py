from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_package_douglas-ms",
    version="0.0.1",
    author="Douglas",
    author_email="stockbroker.dgs@gmail.com",
    description="A small package",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/douglas-ms/image-processing-package",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)