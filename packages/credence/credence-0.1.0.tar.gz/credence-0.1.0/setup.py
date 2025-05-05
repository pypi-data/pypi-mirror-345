from setuptools import setup, find_packages

setup(
    name="code_fetcher",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
    ],
    author="Tanmay",
    description="A simple package to fetch files by number from a GitHub repository",
    keywords="code, fetcher, github",
    url="https://github.com/Tanmay-24/CL3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
