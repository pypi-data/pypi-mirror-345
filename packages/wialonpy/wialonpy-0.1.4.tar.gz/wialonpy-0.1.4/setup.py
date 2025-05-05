from setuptools import find_packages, setup

setup(
    name="wialonpy",
    version="0.1.3",
    description="A lightweight Python wrapper for the Wialon API by Gurtam",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Viacheslav Shambazov",
    author_email="shambazov@gmail.com",
    url="https://github.com/slv177/wialonpy",
    license="MIT",
    packages=find_packages(include=["wialonpy"]),
    install_requires=[
        "requests",
        "pytest"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
