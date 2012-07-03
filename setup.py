import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='launchbox',
      version='0.1',
      description='Packaging and dependency resolution for chef-solo cookbooks',
      long_description=read('README.rst'),
      keywords="chef chef-solo dependency package bundle",
      url='http://github.com/SimpleFinance/launchbox',
      author='Cosmin Stejerean',
      author_email='cosmin@offbytwo.com',
      license='Apache License 2.0',
      packages=['launchbox'],
      scripts=['bin/launchbox'],
      tests_require=open('test-requirements.txt').readlines(),
      install_requires=open('requirements.txt').readlines(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities'
        ]
     )
