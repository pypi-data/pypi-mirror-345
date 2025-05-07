from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codeanalyze",
    version="0.5",
    author="snowpie",
    author_email="davin0706@gmail.com",
    description="AI 기반 코드 보안 분석기 CLI",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    packages=["codeanalyze"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "codeanalyze = codeanalyze.cli:main"
        ]
    },
)