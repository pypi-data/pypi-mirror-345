from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ag_lib_base",  # Replace with your library name
    version="0.1.0",  # Initial version
    author="Miguel Moreno",  # Replace with your name
    author_email="moorenomiguel03@gmail.com",  # Replace with your email
    description="A test library",  # Short description
    long_description=long_description,  # Long description from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/Mo3oDev/ag_lib_base",  # Replace with your GitHub repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "random"
    ],
)