from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sms-pilot-py',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Python SMSPilot API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['requests'],
    url='https://github.com/migelbd/SmsPilotPy',
    author='Mikhail Badrazhan',
    author_email='migel.bd@gmail.com'
)