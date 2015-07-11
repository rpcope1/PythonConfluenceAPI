__author__ = 'Robert Cope'

from PythonConfluenceAPI import ConfluenceAPI
import sys


def compatible_print(msg):
    sys.stdout.write("{}\n".format(msg))
    sys.stdout.flush()

USERNAME = ''
PASSWORD = ''
WIKI_SITE = 'https://my-awesome-organization.atlassian.net/wiki'

api = ConfluenceAPI(USERNAME, PASSWORD, WIKI_SITE)
new_pages = api.get_content('')
compatible_print("Newest pages:")
for page in new_pages:
    compatible_print("{} - {} ({})".format(page.get("space", {}).get("key", "???"),
                                                  page.get("title", "(No title)"),
                                                  page.get("id", "(No ID!?)")))
    content = page.get("body", {}).get("view", {}).get("value", "No content.")
    content = content[:37] + "..." if len(content) > 40 else content
    compatible_print("Preview: {}".format(content))