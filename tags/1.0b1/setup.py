from setuptools import setup, find_packages
import sys, os

setup(
    name='imageSTORE',
    version='1.0b1',
    description="Image metadata and storage system and web service",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='LGPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'grok',
        'lxml',
        'z3c.blobfile',
        ],
    )
