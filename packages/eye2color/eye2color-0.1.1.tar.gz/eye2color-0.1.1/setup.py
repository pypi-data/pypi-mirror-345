from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="eye2color",
    version="0.1.1",
    description="CLI for Wuhan Jingce EYE2-400 Color Analyzer (MES,1)",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/ughstudios/eye2color",
    packages=find_packages(),
    install_requires=[
        "pyserial",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "eye2color=eye2color.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/markdown"
)
