from setuptools import setup, find_packages

setup(
    name='super_sparql',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],  # list dependencies here
    author='Vicky Vicky',
    description='This package is for parsing the SPARQL Queries in order to save the world',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
