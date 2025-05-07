from setuptools import setup, find_packages

setup(
    name="insy",
    version="0.1.0",
    packages=find_packages(),
    description="A library for computational methods, mathematical programming, and systems modeling",
    author="Gevorg Melqonyan",
    author_email="gevorgmelqonyan03@gmail.com",
    license="MIT",
    install_requires=[
        "numpy", "sympy", "matplotlib", "scipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
