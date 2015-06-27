__author__ = "Robert Cope"

import requests
from urlparse import urljoin
import logging
import base64
try:
    import anyjson as json
except ImportError:
    import json

api_logger = logging.getLogger(__name__)
nh = logging.NullHandler()
api_logger.addHandler(nh)


class ConfluenceAPI(object):
    DEFAULT_USER_AGENT = "PythonConfluenceAPI"

    def __init__(self, username, password, uri_base, user_agent=DEFAULT_USER_AGENT):
        self.username = username
        self.password = password
        self.uri_base = uri_base
        self.user_agent = user_agent
        self.session = None

    def _start_http_session(self):
        api_logger.debug("Starting new HTTP session...")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        if self.username and self.password:
            api_logger.debug("Requests will use authorization.")
            auth_str = "Basic "
            auth_str += base64.standard_b64encode(":".join([self.username, self.password]))
            self.session.headers.update({"Authorization": auth_str})

    def _service_request(self, request_type, sub_uri, params=None, callback=None,
                         raise_for_status=True, raw=False, **kwargs):
        api_logger.debug("Sending request: {} ({})".format(sub_uri, request_type))
        if not self.session:
            self._start_http_session()
        uri = urljoin(self.uri_base, sub_uri)
        if params:
            kwargs.update(params=params)
        response = self.session.request(request_type, uri, **kwargs)
        if raise_for_status:
            response.raise_for_status()
        if callback:
            return callback(response)
        else:
            return response.content if raw else json.loads(response.text)

    def _service_get_request(self, *args, **kwargs):
        return self._service_request("GET", *args, **kwargs)

    def _service_post_request(self, *args, **kwargs):
        return self._service_request("POST", *args, **kwargs)

    def _service_delete_request(self, *args, **kwargs):
        return self._service_request("DELETE", *args, **kwargs)

    def _service_put_request(self, *args, **kwargs):
        return self._service_request("PUT", *args, **kwargs)

    def get_content(self, content_type=None, space_key=None, title=None, status=None, posting_day=None,
                    expand=None, start=None, limit=25, callback=None):
        params = {}
        if content_type:
            params["type"] = content_type
        if space_key:
            params["spaceKey"] = space_key
        if title:
            params["title"] = title
        if status:
            params["status"] = status
        if posting_day:
            params["postingDay"] = posting_day
        if expand:
            params["expand"] = expand
        if start:
            params["start"] = start
        if limit:
            params["limit"] = limit
        return self._service_get_request("rest/api/content", params=params, callback=callback)

    def get_content_by_id(self, content_id, status=None, version=None, expand=None, callback=None):
        params = {}
        if status:
            params["status"] = str(status)
        if version:
            params["version"] = int(version)
        if expand:
            params["expand"] = str(expand)
        return self._service_get_request("rest/api/content/{id}".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_history_by_id(self, content_id, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = str(expand)
        return self._service_get_request("rest/api/content/{id}/history".format(id=content_id), params=params,
                                         callback=callback)