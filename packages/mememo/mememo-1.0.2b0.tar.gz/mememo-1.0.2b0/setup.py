from setuptools import setup, find_packages

setup(
    name='mememo',
    version='1.0.2b0',
    description='Package to find the mean, median, and mode.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='I.P Freely',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.5',
)
