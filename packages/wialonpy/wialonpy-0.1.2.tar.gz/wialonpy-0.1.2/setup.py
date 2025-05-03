from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wialonpy",
    version="0.1.2",
    author="Viacheslav Shambazov",
    author_email="shambazov@gmail.com",
    description="A lightweight Python wrapper for the Wialon API by Gurtam",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slv177/wialonpy",
    packages=find_packages(),
    install_requires=["requests", "pytest",],
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.13',
)