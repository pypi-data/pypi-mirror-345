from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-pixi",
    version="0.0.0",
    author="Joyen Benitto",
    author_email="joyen.benitto12@gmail.com",
    description="A Python package for program analysis and custom instruction generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoyenBenitto/Pixi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pixi=pixi.main:cli",  # Command name remains 'pixi' for user convenience
        ],
    },
)