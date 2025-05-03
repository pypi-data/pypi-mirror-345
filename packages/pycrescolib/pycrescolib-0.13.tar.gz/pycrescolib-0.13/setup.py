from setuptools import setup

setup(
    name='pycrescolib',
    version='0.13',
    packages=['pycrescolib'],
    url='http://cresco.io',
    license='Apache 2.0',
    author='Cresco Team',
    author_email='info@cresco.io',
    description='Python Cresco Client Library',
    install_requires=['websockets>=10.0', "cryptography==44.0.1", 'backoff>=2.0.0'],

)
