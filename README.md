[![PyPI version](https://badge.fury.io/py/PythonConfluenceAPI.svg)](http://badge.fury.io/py/PythonConfluenceAPI)

# PythonConfluenceAPI
PythonConfluenceAPI is a Pythonic API wrapper over the Confluence REST API, which cleanly wraps *all* of the
methods present in the current Confluence API spec, and is easily adapter to be used with minimal effort in other
frameworks such as concurrent futures, greenlets, and other concurrency schemes.

Read the latest PythonConfluenceAPI docs [here.](http://htmlpreview.github.io/?https://github.com/pushrodtechnology/PythonConfluenceAPI/blob/master/doc/html/index.html) 

# How To Use

    # Load API wrapper from library
    from PythonConfluenceAPI import ConfluenceAPI

    # Create API object.
    api = ConfluenceAPI('username', 'password', 'https://my.atlassian.site.com/wiki')

    # Get latest visible content from confluence instance.
    confluence_recent_data = api.get_content()

    # Create a new confluence space
    api.create_new_space({'key': 'TEST', 'name': 'My Test Space', 'description': 'This is a test confluence space'})

All of the API methods have docstrings attached which mirror the official Atlassian documentation, as the API
currently is a rather thin wrapper over top of the Confluence API. Users are advised to consult the source code or
look at the Atlassian API documentation for further info. Examples are also provided in the Examples directory of
the repository.

# License
This repository was written for Pushrod Technology by Robert Cope, and is licensed as LGPLv3.
