from setuptools import find_packages, setup  # Correctly sorted imports

setup(
    name="pysubstitutor",  # Match the directory name
    version="1.0.2",  # Ensure this is a valid PEP 440 version
    description="A Python package for converting text substitution files between different formats.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Cory Siebler",
    author_email="cory.siebler@protonmail.com",
    url="https://github.com/crsiebler/pysubstitutor",  # Updated repository name
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=[
        "pytest==7.4.2",
        "coverage==7.8.0",
        "isort==5.12.0",
        "black==23.9.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "text-substitutions=pysubstitutor.__main__:main",
        ],
    },
)
