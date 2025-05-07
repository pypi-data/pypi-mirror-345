from setuptools import setup, find_packages

setup(
    name="vidlib",
    version="1.0.0",
    author="MSDIGITAL",
    author_email="sunibamidoan6@gmail.com",
    description="Vidio Lib Checker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)