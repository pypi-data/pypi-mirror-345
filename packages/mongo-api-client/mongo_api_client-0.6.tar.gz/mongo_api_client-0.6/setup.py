from setuptools import setup, find_packages

setup(
    name="mongo-api-client",
    version="0.6",
    packages=find_packages(),
    install_requires=["requests"],
    author="alexanderthegreat96",
    author_email="alexanderdth96@gmail.com",
    description="Provides a fluent syntax for interacting with a MongoDB API Instance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alexanderthegreat96/mongo-api-python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
