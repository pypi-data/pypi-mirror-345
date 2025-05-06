import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_desc = fh.read()

setuptools.setup(
    name="python-logger-simple",
    version="0.1.0",
    author="Cut0x",
    author_email="contact@valloic.dev",
    description="A simple Python logger module with configurable options.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/Cut0x/python-logger-simple",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.20"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
