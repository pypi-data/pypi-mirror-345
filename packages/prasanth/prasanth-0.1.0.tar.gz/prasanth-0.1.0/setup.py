from setuptools import setup, find_packages

setup(
    name="prasanth",
    version="0.1.0",
    packages=find_packages(),
    author="Your Name",
    author_email="your@email.com",
    description="My first Python library!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/prasanth",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
