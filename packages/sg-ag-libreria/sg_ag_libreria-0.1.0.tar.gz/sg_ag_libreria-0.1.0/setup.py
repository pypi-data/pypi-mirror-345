from setuptools import setup, find_packages

setup(
    name="sg_ag_libreria",
    version="0.1.0",
    author="John Sebastian Galindo Hernandez",
    packages=find_packages(),
    description="Una libreria para algoritmos geneticos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="johnsgalindo@ucundinamarca.edu.co",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)