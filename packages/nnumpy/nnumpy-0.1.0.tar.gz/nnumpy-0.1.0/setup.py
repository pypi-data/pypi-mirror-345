from setuptools import setup, find_packages

setup(
    name="nnumpy",                      # Your package name
    version="0.1.0",                        # Version
    description="Nnumpy package",       # Short description
    # long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    install_requires=[],                    # Optional dependencies
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
