from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="custom_package12345",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "custom_package=src:hello"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)