# PythonConfluenceAPI
A Pythonic API wrapper over the Confluence REST API.

# How To Use

    from PythonConfluenceAPI import ConfluenceAPI
    api = ConfluenceAPI('username', 'password', 'https://my.atlassian.site.com/wiki')
    confluence_recent_data = api.get_content()
