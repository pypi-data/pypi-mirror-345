from setuptools import setup, find_packages
import os

# Get long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Handle requirements.txt - read if exists, otherwise define core requirements directly
# This makes the build process more robust and adaptable
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = fh.read().splitlines()
else:
    # Define core requirements directly if requirements.txt isn't available
    # This ensures the build doesn't fail when requirements.txt is missing
    requirements = [
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "numpy>=1.22.0",
        "click>=8.0.0",
        "pathlib>=1.0.1",
        "tqdm>=4.65.0",
        "sentence-transformers>=2.2.2"
    ]

setup(
    name="seekly",
    version="1.1.2",
    author="Dhodraj Sundaram",
    author_email="dhodrajsdr192@gmail.com",
    description="Natural language search for files using all-MiniLM-L6-v2 model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dhodraj/seekly",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "seekly=seekly:cli",  # This will use the cli function from seekly.py in the root directory
        ],
    },
    py_modules=["seekly"],  # This includes the root seekly.py file in the package
    package_data={
        "": ["assets/*.jpg", "assets/*.png"],  # Include all image files in the assets directory
    },
    include_package_data=True,  # This tells setuptools to include package_data
)