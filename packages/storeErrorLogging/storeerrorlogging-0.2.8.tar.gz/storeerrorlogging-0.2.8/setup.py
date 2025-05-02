
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='storeErrorLogging',
    version='0.2.8',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''
This module makes flask error reporting and normal error reporting get reported inside an sql database. It also provides a printt function that also saves statements to the database.
''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 
    packages=find_packages(),
    install_requires=["sqlalchemy","sqlalchemy","sqlalchemy","relativePathImport"], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)