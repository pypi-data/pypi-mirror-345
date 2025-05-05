from setuptools import setup, find_packages

setup(
    name='referbook',
    version='0.1',
    packages=find_packages(),
    author='ANOS',
    description='A reference book with useful Python code examples',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
