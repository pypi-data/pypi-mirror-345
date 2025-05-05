from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="helm-values",
    version="0.1.7",
    py_modules=["values"],
    install_requires=["pyyaml"],
    author="fluffyspike",
    description="Load and merge Helm values files for cdk8s",
    python_requires=">=3",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
