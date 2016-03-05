__author__ = 'Robert Cope, Pushrod Technology'
__author_email__ = 'robert.cope@pushrodtechnology.com'
__version__ = '0.0.1rc6'

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

setup(name='PythonConfluenceAPI',
      author=__author__,
      author_email=__author_email__,
      version=__version__,
      description="PythonConfluenceAPI is a Pythonic API wrapper over the Confluence REST API,"
                  " which cleanly wraps all of the methods present in the current Confluence API spec, "
                  "and is easily adapter to be used with minimal effort in other frameworks such as concurrent "
                  "futures, greenlets, and other concurrency schemes.",
      packages=['PythonConfluenceAPI'],
      scripts=['ez_setup.py', 'setup.py'],
      license="LGPLv3",
      keywords="atlassian confluence api",
      url="https://github.com/pushrodtechnology/PythonConfluenceAPI",
      install_requires=['requests>=2.3.0', 'anyjson', 'futures', 'requests-futures'],
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Environment :: Other Environment",
                   "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
                   "Operating System :: OS Independent",
                   "Intended Audience :: Developers",
                   "Intended Audience :: System Administrators",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules"])
