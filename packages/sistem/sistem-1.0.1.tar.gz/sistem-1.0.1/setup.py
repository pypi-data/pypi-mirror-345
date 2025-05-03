from setuptools import setup, find_packages

setup(
    name='sistem',
    version='1.0.1',
    author='Samson Weiner',
    author_email='samson.weiner@uconn.edu',
    description='CNAsim is a software package for simulation of single-cell CNA data from tumors.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/samsonweiner/CNAsim',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(),
    python_requires='>=3.12'
)