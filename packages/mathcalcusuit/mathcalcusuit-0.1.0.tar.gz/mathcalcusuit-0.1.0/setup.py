from setuptools import setup, find_packages

setup(
    name="mathcalcusuit", 
    version="0.1.0",  
    packages=find_packages(), 
    description="A simple package for basic math operations including prime checking, Fibonacci, GCD, LCM, and factorials",
    long_description=open('README.md').read(), 
    long_description_content_type="text/markdown",
    author="Md. Ismiel Hossen Abir", 
    author_email="ismielabir1971@gmail.com", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
