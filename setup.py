from setuptools import setup, find_packages

setup(
    name='fyers_auth',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/jishnujp/fyers_auth',
    author='Jishnu Jayaprakash',
    description='A Python package for Fyers API authentication, generating access token.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
        'redis',
        'pyotp'
    ],
)