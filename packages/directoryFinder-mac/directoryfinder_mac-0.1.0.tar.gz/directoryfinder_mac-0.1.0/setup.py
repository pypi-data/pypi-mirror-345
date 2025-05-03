from setuptools import setup, find_packages

setup(
    name="directoryFinder-mac",
    version="0.1.0",
    description="Find files/folders in specific macOS directories using fuzzy search.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Polisetty Naga Ajay",
    author_email="polisettynagaajay5103@gmail.com.com",
    url="https://github.com/nagaajau/directoryFinder-mac",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
