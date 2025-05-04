from setuptools import setup, find_packages

setup(
    name="pygamerui",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0",
    ],
    python_requires=">=3.6",
)