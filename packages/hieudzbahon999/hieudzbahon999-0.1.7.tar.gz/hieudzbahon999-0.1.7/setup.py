from setuptools import setup, find_packages

setup(
    name="hieudzbahon999",
    version="0.1.7",
    packages=find_packages(),
    install_requires=["regex>=2023.10.3", "requests>=2.31.0"],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library with mathematical and string utilities",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hieudz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)