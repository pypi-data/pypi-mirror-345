from setuptools import setup, find_packages

setup(
    name="skala_lab_package",
    version="0.1.5",
    author="Manato Ogawa",
    author_email="maogawa@wisc.edu",
    description="A package for redox feature analysis, CSV generation, and SDT file handling.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/monatopotato",  
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

