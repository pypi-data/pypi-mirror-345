from setuptools import setup, find_packages

setup(
    name='pumpdotfun',
    version='0.3.4',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    license='MIT',
    description='pump.fun frontend API Wrapper for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Melvin Luis',
    author_email='whappiness183@gmail.com',
    url='https://github.com/izzulafifteam/py-python.git',
    project_urls={
        "Source": "https://github.com/izzulafifteam/pumpdotfun",
        "Documentation": "https://frontend-api.pump.fun/api"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)