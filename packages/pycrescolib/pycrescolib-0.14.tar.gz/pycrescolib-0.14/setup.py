from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pycrescolib',
    version='0.14',
    packages=['pycrescolib'],
    url='http://cresco.io',
    license='Apache 2.0',
    author='Cresco Team',
    author_email='info@cresco.io',
    description='Python Cresco Client Library',
    install_requires=['websockets>=10.0', "cryptography==44.0.1", 'backoff>=2.0.0'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
