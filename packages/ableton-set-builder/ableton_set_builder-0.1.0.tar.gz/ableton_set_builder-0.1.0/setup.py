from setuptools import setup, find_packages

setup(
    name="ableton_set_builder",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "xmltodict",
    ],
    author="Lars & Manuel",
    author_email="me@manuelmol.nl",
    description="A package to build Ableton Live sets programmatically.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PCO-Ableton/ableton_set_builder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
