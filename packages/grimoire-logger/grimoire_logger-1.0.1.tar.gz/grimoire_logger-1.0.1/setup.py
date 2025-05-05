from setuptools import setup, find_packages

setup(
    name="grimoire_logger",
    version="1.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Lucas Signorelli",
    description="A simple Python logger, that prints in a JSON format",
    url="https://github.com/luquor/grimoire",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)