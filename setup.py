from setuptools import setup

setup(name='Lunchbox',
      version='0.1',
      description='Packager for chef-solo',
      author='Cosmin Stejerean',
      author_email='cosmin@offbytwo.com',
      license='Apache License 2.0',
      url='http://github.com/SimpleFinance/launchbox',
      packages=['launchbox'],
      scripts=['bin/launchbox', 'bin/publish-cookbook'],
      tests_require=open('test-requirements.txt').readlines(),
      install_requires=open('requirements.txt').readlines()
     )
