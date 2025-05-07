from setuptools import setup, find_packages

setup(
    name="aitronos-logger",
    version="0.1.13",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    python_requires=">=3.7",
) 