from setuptools import setup, find_packages

setup(
    name='sistem',
    version='1.0.2',
    author='Samson Weiner',
    author_email='samson.weiner@uconn.edu',
    description='SISTEM (SImulation of Single-cell Tumor Evolution and Metastasis) is a software package and mathematical model for simulating tumor evolution, cell migrations, and DNA-seq data at single-cell resolution.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/samsonweiner/sistem',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(),
    python_requires='>=3.12'
)