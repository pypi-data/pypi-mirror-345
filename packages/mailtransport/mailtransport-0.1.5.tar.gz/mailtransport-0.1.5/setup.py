from setuptools import setup, find_packages

setup(
    name="mailtransport",
    version="0.1.5",
    author="mailtransportai",
    author_email="support@mailtransportai.com",
    description="A Python package for managing email transport.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mailtransportai/mailtransport-py",
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