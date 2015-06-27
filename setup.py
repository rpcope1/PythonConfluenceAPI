__author__ = 'Robert Cope', 'Pushrod Technology'
__author_email__ = 'robert.cope@pushrodtechnology.com'
__version__ = '0.0.1'

from setuptools import setup

setup(name='PythonConfluenceAPI',
      author=__author__,
      author_email=__author_email__,
      version=__version__,
      packages=['PythonConfluenceAPI'],
      install_requires=['requests>=2.3.0', 'anyjson'])