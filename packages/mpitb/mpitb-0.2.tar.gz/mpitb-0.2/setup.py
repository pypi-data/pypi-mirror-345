from pathlib import Path

from setuptools import find_packages, setup

# Read README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")


setup(
    name="mpitb",
    version="0.2",
    description="A toolbox for multidimensional poverty index (MPI) estimation and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Joseph Lam",
    packages=find_packages(),
    install_requires=[
        "pandas", "numpy", "scipy"
    ],
    python_requires=">=3.7"
)
