from setuptools import setup

setup(
    name="codeanalyze",
    version="0.1",
    py_modules=["cli"],
    install_requires=[
        "click",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "codeanalyze=cli:cli",
        ],
    },
)