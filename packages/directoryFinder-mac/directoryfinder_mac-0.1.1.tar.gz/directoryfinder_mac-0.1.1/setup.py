from setuptools import setup, find_packages

setup(
    name="directoryFinder-mac",  # This is the PyPI name (dash)
    version="0.1.1",
    description="Find files/folders in specific macOS directories using fuzzy search.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Polisetty Naga Ajay",
    author_email="polisettynagaajay5103@gmail.com",
    url="https://github.com/nagaajau/directoryFinder-mac",
    packages=find_packages(include=["directoryFinder_mac", "directoryFinder_mac.*"]),  # <- critical fix
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
