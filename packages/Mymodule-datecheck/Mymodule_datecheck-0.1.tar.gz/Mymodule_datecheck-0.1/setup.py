from setuptools import setup, find_packages

setup(
    name='Mymodule_datecheck',        # must be unique on PyPI
    version='0.1',
    packages=find_packages(),
    author='Chintan',
    author_email='chintan.suthar@xbyte.io',
    description='A module to check date format',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)