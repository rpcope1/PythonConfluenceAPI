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

    NEW_CONTENT_REQUIRED_KEYS = {"type", "title", "space", "body"}
    ATTACHMENT_METADATA_KEYS = {"id", "type", "version", "title"}
    UPDATE_CONTENT_REQUIRED_KEYS = {"id", "version"}

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
                    expand=None, start=None, limit=None, callback=None):
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
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content", params=params, callback=callback)

    def get_content_by_id(self, content_id, status=None, version=None, expand=None, callback=None):
        params = {}
        if status:
            params["status"] = status
        if version is not None:
            params["version"] = int(version)
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_history_by_id(self, content_id, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}/history".format(id=content_id), params=params,
                                         callback=callback)

    def search_content(self, cql_str=None, cql_context=None, expand=None, start=0, limit=None, callback=None):
        params = {}
        if cql_str:
            params["cql"] = cql_str
        if cql_context:
            params["cqlcontext"] = cql_context
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/search", params=params, callback=callback)

    def get_content_children(self, content_id, expand=None, parent_version=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if parent_version:
            params["parentVersion"] = parent_version
        return self._service_get_request("rest/api/content/{id}/child".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_children_by_type(self, content_id, child_type, expand=None, parent_version=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if parent_version:
            params["parentVersion"] = parent_version
        return self._service_get_request("rest/api/content/{id}/child/{type}".format(id=content_id, type=child_type),
                                         params=params, callback=callback)

    def get_content_descendants(self, content_id, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}/descendant".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_descendants_by_type(self, content_id, child_type, expand=None, start=None, limit=None,
                                        callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/{id}/descendant/{type}"
                                         "".format(id=content_id, type=child_type), params=params, callback=callback)

    def get_content_labels(self, content_id, prefix=None, start=None, limit=None, callback=None):
        params = {}
        if prefix:
            params["prefix"] = prefix
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/{id}/label".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_comments(self, content_id, child_type, expand=None, parent_version=None, start=None, limit=None,
                             location=None, depth=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if parent_version:
            params["parentVersion"] = parent_version
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        if location:
            params["location"] = location
        if depth:
            params["depth"] = depth
        return self._service_get_request("rest/api/content/{id}/child/{type}".format(id=content_id, type=child_type),
                                         params=params, callback=callback)

    def get_content_attachments(self, content_id, expand=None, start=None, limit=None, filename=None, media_type=None,
                                callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        if filename is not None:
            params["filename"] = filename
        if media_type is not None:
            params["mediaType"] = media_type
        return self._service_get_request("rest/api/content/{id}/child/attachment".format(id=content_id),
                                         params=params, callback=callback)

    def get_content_properties(self, content_id, expand=None, start=None, limit=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/{id}/property".format(id=content_id),
                                         params=params, callback=callback)

    def create_new_content(self, content_data, callback=None):
        assert isinstance(content_data, dict) and set(content_data.keys()) >= self.NEW_CONTENT_REQUIRED_KEYS
        return self._service_post_request("rest/api/content", data=json.dumps(content_data),
                                          headers={"Content-Type": "application/json"}, callback=callback)

    def create_new_attachment_by_content_id(self, content_id, attachments, callback=None):
        if isinstance(attachments, list):
            assert all(isinstance(at, dict) and "file" in at.keys() for at in attachments)
        elif isinstance(attachments, dict):
            assert "file" in attachments.keys()
        else:
            assert False
        return self._service_post_request("rest/api/content/{id}/child/attachment".format(id=content_id),
                                          headers={"X-Atlassian-Token": "nocheck"}, files=attachments,
                                          callback=callback)

    def create_new_label_by_content_id(self, content_id, label_names, callback=None):
        assert isinstance(label_names, list)
        assert all(isinstance(ln, dict) and set(ln.keys) == {"prefix", "name"} for ln in label_names)
        return self._service_get_request("rest/api/content/{id}/label".format(id=content_id),
                                         data=json.dumps(label_names), headers={"Content-Type": "application/json"},
                                         callback=callback)

    def create_new_content_property(self, content_id, content_property, callback=None):
        assert isinstance(content_property, dict)
        assert {"key", "value"} <= set(content_property.keys())
        return self._service_post_request("rest/api/content/{id}/property".format(id=content_id),
                                          data=json.dumps(content_property),
                                          headers={"Content-Type": "application/json"}, callback=callback)

    def update_content_by_id(self, content_data, content_id, callback=None):
        assert isinstance(content_data, dict) and set(content_data.keys()) >= self.UPDATE_CONTENT_REQUIRED_KEYS
        return self._service_put_request("rest/api/content/{id}".format(content_id), data=json.dumps(content_data),
                                         headers={"Content-Type": "application/json"}, callback=callback)

    def update_attachment_metadata(self, content_id, attachment_id, new_metadata, callback=None):
        assert isinstance(new_metadata, dict) and set(new_metadata.keys()) >= self.ATTACHMENT_METADATA_KEYS
        return self._service_put_request("rest/api/content/{id}/child/attachment/{attachment_id}"
                                         "".format(id=content_id, attachment_id=attachment_id),
                                         data=json.dumps(new_metadata), headers={"Content-Type": "application/json"},
                                         callback=callback)

    def update_attachment(self, content_id, attachment_id, attachment, callback=None):
        if isinstance(attachment, dict):
            assert "file" in attachment.keys()
        else:
            assert False
        return self._service_post_request("rest/api/content/{content_id}/child/attachment/{attachment_id}/data"
                                          "".format(content_id=content_id, attachment_id=attachment_id),
                                          headers={"X-Atlassian-Token": "nocheck"}, files=attachment,
                                          callback=callback)

    def delete_content_by_id(self, content_id, status=None, callback=None):
        params = {}
        if status:
            params["status"] = status
        return self._service_delete_request("rest/api/content/{id}".format(content_id), params=params,
                                            callback=callback)

    def delete_label_by_id(self, content_id, label_name, callback=None):
        params = {"name": label_name}
        return self._service_delete_request("rest/api/content/{id}/label".format(id=content_id),
                                            params=params, callback=callback)