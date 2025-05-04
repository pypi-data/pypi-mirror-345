
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='relativePathImport',
    version='0.2.8',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''The `relativePathImport` class provides various utilities to handle paths in a project and allows you to work with relative paths, navigate backwards in the directory structure, and import modules from relative file locations. It works for both windows and linux.''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 

    url="https://github.com/brighamturner12/relativePathImport.git",
    project_urls={"Documentation": "https://github.com/brighamturner12/relativePathImport/blob/main/readme.md","Source Code": "https://github.com/brighamturner12/relativePathImport/blob/main/importRelative_source.py",},

    packages=find_packages(),
    install_requires=[""], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)