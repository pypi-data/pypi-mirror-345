from setuptools import setup, find_packages

setup(
    name="PyCleanText",
    version="0.1.0",
    author="Md. Ismiel Hossen Abir",
    author_email="ismielabir1971@gmail.com",
    description="A Python package for cleaning text data by removing noise, stopwords, duplicates, and more.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
