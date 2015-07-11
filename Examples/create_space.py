__author__ = 'Robert Cope'

from PythonConfluenceAPI import ConfluenceAPI

USERNAME = ''
PASSWORD = ''
WIKI_SITE = 'https://my-awesome-organization.atlassian.net/wiki'

api = ConfluenceAPI(USERNAME, PASSWORD, WIKI_SITE)
api.create_new_space({
    'key': 'LOL',
    'name': 'My testing space',
    'description': {
        'plain': {'value': 'This is my new testing space', 'representation': 'plain'}
    }
})
# Generate a page for our space
api.create_new_content({
    'type': 'page',
    'title': 'My landing page for TESTSPACE!',
    'space': {'key': 'LOL'},
    'body': {
        'storage': {'value': '<h1>Welcome to the landing page!</h1><p>Lorem Ipsum</p>',
                    'representation': 'storage'
                    }
    }
})
