from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="instinct_py_nodes",
    version="0.1.4",
    author="Nexstem",
    author_email="developers@nexstem.ai",
    description="A Python package for creating distributed nodes using ZeroMQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sw-instinct-py-nodes",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyzmq>=0.0.0",
    ],
) 