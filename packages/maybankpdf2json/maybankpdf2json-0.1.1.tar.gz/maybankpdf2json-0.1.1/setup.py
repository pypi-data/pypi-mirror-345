from setuptools import setup, find_packages

setup(
    name="maybankpdf2json",
    version="0.1.1",
    author="Nordin",
    author_email="vipnordin@gmail.com",
    description="A package for extracting JSON data from Maybank account statements(PDF format).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nordinz7/maybankpdf2json",
    packages=find_packages(),
    install_requires=[
        "pdfplumber",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
