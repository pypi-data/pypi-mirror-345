from setuptools import setup, find_packages

setup(
    name="riscvlib",
    version="0.7.4",
    author="Mike Harris",
    author_email="mike.harris451@gmail.com",
    description="Resources for working with RISC-V in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mike451/riscvlib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
)