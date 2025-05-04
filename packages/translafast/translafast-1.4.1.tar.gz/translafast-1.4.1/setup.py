from setuptools import setup, find_packages

setup(
    name="translafast",
    version="1.4.1",
    author="PozStudio",
    author_email="support@translafast.xyz",
    description="A blazing-fast Python translation library with 178-language support and intelligent caching.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://translafast.xyz",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "translafast": ["languages.json"]
    },
    install_requires=[
        "googletrans==4.0.0-rc1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
