from setuptools import setup, find_packages

setup(
    name="mean-median-mode",
    version="1.0.0b",
    author="Annoying-mous",
    description="Package to find the mean, median, and mode",
    long_description=open("DOCUMENTATION.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=2.5",
)
