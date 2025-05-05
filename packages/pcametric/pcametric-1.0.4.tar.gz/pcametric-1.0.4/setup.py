from setuptools import setup, find_packages

setup(
    name='pcametric',
    version='1.0.4',
    author='Muhammad Rajabinasab',
    author_email='muhammad.rajabinasab@outlook.com',
    description='Implementation of novel metrics for measuring inter-dataset similarity based on PCA.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mrajabinasab/Interdataset-Similarity-Metrics',
    packages=find_packages(),
    py_modules=['pcametric'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)