from setuptools import find_packages, setup

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="custom_package12345",
    version="0.4",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here, e.g.:
        # "numpy>=1.18.0",
    ],
    entry_points={
        "console_scripts": [
            "custom_package = custom_package1234:hello",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)