from setuptools import setup, find_packages

setup(
    name="meowmeowutils",
    version="0.1.0",
    description="",
    author="Yoshika Govender",
    author_email="yoshi.govender@gmail.com",
    url="https://github.com/JetpackYoshi/meowmeowutils",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="file tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)