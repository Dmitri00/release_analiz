import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="article_search_dmitri314",
    version="0.0.1",
    author="Toichkin Dmitri",
    author_email="dima.toichki@gmail.com",
    description="This package allows to search copies of the given text in google",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://xxx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
