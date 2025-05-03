from setuptools import setup, find_packages

setup(
    name="dupln",
    version="0.1.0",
    author="JetLogic",
    description="Hard link files with same content",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jet-logic/dupln",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["dupln=dupln.__main__:main"],
    },
    install_requires=[],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
