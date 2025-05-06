from setuptools import setup
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="pyinitpro",
    version="0.1.4",
    py_modules=["pyinit"],
    packages=["pyinit"],
    install_requires=[
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "pyinitpro=pyinit.__main__:main",
        ],
    },
    author="Martins O Jojolola",
    description="A CLI tool to scaffold Python projects with venv and folder structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Martins-O/pyinit.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.1",
    license="MIT",
    keywords="python cli scaffold virtualenv project setup",
)