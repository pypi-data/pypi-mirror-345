from setuptools import setup, find_packages

setup(
    name="persistent_bm25_v2",
    version="1.0.1",  
    author="Mohammed Orabi",
    author_email="mahmedorabi297@gmail.com",
    description="A persistent implementation of BM25 retrieval.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mohammed-orabi2/persistent-bm25",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "rank_bm25"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)