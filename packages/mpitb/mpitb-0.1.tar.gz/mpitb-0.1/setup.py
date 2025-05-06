from setuptools import find_packages, setup

setup(
    name="mpitb",
    version="0.1",
    description="A toolbox for multidimensional poverty index (MPI) estimation and analysis",
    author="Joseph Lam",
    packages=find_packages(),
    install_requires=[
        "pandas", "numpy", "scipy"
    ],
    python_requires=">=3.7"
)
