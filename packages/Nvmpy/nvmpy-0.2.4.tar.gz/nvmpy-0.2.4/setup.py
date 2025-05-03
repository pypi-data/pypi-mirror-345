from setuptools import setup, find_packages

setup(
    name="Nvmpy",
    version="0.2.4",
    author="A",
    description="A library to fetch categorized code snippets.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_library",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
