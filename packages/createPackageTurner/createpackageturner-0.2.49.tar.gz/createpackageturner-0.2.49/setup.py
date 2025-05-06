
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='createPackageTurner',
    version='0.2.49',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''**createPackageTurner** is an automated Python package creation tool designed to quickly turn a Python class into a fully functional Python package. It generates the required package structure, metadata, setup files, and optionally publishes the package to PyPI. By providing an input class or function, you can automatically generate a Python package and optionally upload it to PyPI for distribution.

## Features
- Automatically generates a package structure based on the given input class or function.
- This supports publishing functions as packages as well.
- Users can specify the path to packages files. Afterwards, for greater customization, users can alter the generated `setup.py` file and upon running this module again, this module is smart enough to preserve the changes they made to the `setup.py` when regenerating the package.
- Supports adding custom metadata (author, email, description, readme, etc.). It will still work without providing this information however (even `packageName` will default to be identical to the name of `inputClassOrFunction` if not provided). The only argument it always needs is `inputClassOrFunction`.
- Can upload the generated package to PyPI.
- Automatically increments the version number. If there already are package files in the path specified, it chooses the version from those files and adds one. If one has already published a prior version of this package to pypi, it will take the version from that and add one. If both, then it chooses the max version, and if neither then by default the first version is `0.2.2`.
- Flexible options for including or excluding package requirements.''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 

    url="https://github.com/brighamturner12/packageMakerTurner.git",
    project_urls={"Documentation": "https://github.com/brighamturner12/packageMakerTurner/blob/main/readme.md","Source Code": "https://github.com/brighamturner12/packageMakerTurner/blob/main/packageMaker_source.py",},

    packages=find_packages(),
    install_requires=["pip","twine"], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)