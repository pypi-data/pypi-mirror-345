from setuptools import setup, find_packages

setup(
    name='pumpdotfun',
    version='0.2',
    packages=find_packages(),
    description='A simple bundler Python library for pumpfun',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Melvin Luis',
    author_email='whappiness183@gmail.com ',
    url='https://github.com/izzulafifteam/py-python.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        # Any dependencies your library needs
    ],
    python_requires='>=3.6',
)