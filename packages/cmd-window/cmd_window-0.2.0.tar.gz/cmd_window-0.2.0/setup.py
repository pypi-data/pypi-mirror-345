# setup.py
from setuptools import setup, find_packages

setup(
    name="cmd_window",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pynput"],
    author="Czeglédy Péter",
    author_email="czegledyp2@gmail.com",
    description="This python module makes it easy to create text-based, graphical interfaces.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/peterczegledy/Python-modules/tree/main/cmd_window",  # ha van
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
