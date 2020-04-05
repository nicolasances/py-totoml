import setuptools 
from totoml.version import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="totoml", # Replace with your own username
    version=version(),
    author="nicolasances",
    author_email="nicolasances@gmail.com",
    description="TotoML SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolasances/py-totoml",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)