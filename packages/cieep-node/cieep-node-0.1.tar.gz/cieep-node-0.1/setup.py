from setuptools import setup, find_packages

setup(
    name="cieep-node",  # must be unique on PyPI
    version="0.1",  # bump version on every upload
    packages=find_packages(),
    install_requires=[],
    author="Your Name",
    description="A practical code library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
