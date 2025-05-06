import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PySerialNumbers",
    version="1.0.1",
    author="Fabrice Voillat",
    author_email="dev@dassym.com",
    keywords = ['Dassym', 'motor', 'api', 'dapi'],
    description="The PySerialNumbers library offers functionalities for manipulating serial numbers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires = [],
    url="https://github.com/dassym/PySerialNumbers",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.4",
    include_package_data=True
)