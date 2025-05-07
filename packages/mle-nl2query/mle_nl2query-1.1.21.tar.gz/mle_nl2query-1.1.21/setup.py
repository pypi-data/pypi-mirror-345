from setuptools import setup, find_packages

setup(
    name="mle-nl2query",
    version="1.1.21",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",  # Supported Python versions
        "License :: OSI Approved :: MIT License",  # License for your package
        "Operating System :: OS Independent",  # Specifies that your package works across different operating systems
    ],
    python_requires=">=3.6",
    author="Palistha Deshar",
    author_email="palisthadeshar@gmail.com",
    description="nl2query package",
    url="https://github.com/RamailoTech/mle_nl2query",
    license="MIT",  # License of your package
)
