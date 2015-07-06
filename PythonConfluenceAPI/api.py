__author__ = "Robert Cope"

import requests
from requests.auth import HTTPBasicAuth
from urlparse import urljoin
import logging
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
        """
        Initialize the API object.
        :param username: Your Confluence username.
        :param password: Your Confluence password.
        :param uri_base: The base url for your Confluence wiki (e.g. myorg.atlassian.com/wiki)
        :param user_agent: (Optional): The user-agent you wish to send on requests to the API.
                           DEFAULT: PythonConfluenceAPI.
        """
        self.username = username
        self.password = password
        self.uri_base = uri_base if uri_base.endswith('/') else uri_base + "/"
        self.user_agent = user_agent
        self.session = None

    def _start_http_session(self):
        """
        Start a new requests HTTP session, clearing cookies and session data.
        :return: None
        """
        api_logger.debug("Starting new HTTP session...")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        if self.username and self.password:
            api_logger.debug("Requests will use authorization.")
            self.session.auth = HTTPBasicAuth(self.username, self.password)

    def _service_request(self, request_type, sub_uri, params=None, callback=None,
                         raise_for_status=True, raw=False, **kwargs):
        """
        Base method for handling HTTP requests via the current requests session.
        :param request_type: The request type as a string (e.g. "POST", "GET", "PUT", etc.)
        :param sub_uri: The REST end point (sub-uri) to communicate with.
        :param params: (Optional) HTTP Request parameters. Default: none
        :param callback: (Optional) A callback function to be excuted on the resulting requests response.
                         This synchronous implementation will return the results of the callback.
                         Default: None. This method returns either the decoded JSON or the raw request content.
        :param raise_for_status: (Optional) When set True, we raise requests.HTTPError on 4xx or 5xx status. When
                                 set False, non-2xx/3xx status code is ignored. Default: True
        :param raw: (Optional) If no callback is set, return the raw content from the request if this is set True.
                    If False, the method attempts to parse the request as JSON data and return the resutls.
                    Default: False
        :param kwargs: Additional parameters to pass to the session request call.
        :return: The JSON decoded results or raw results, or the results of the passed in callback, if applicable.
                 May raise exceptions including requests.HTTPError on fault.
        """
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
        """
        GET request wrapper
        :param args: Positional arguments for _service_request method.
        :param kwargs: Keyword Arguments for _service_request method.
        :return: The results of the corresponding _service_request method.
        """
        return self._service_request("GET", *args, **kwargs)

    def _service_post_request(self, *args, **kwargs):
        """
        POST request wrapper
        :param args: Positional arguments for _service_request method.
        :param kwargs: Keyword Arguments for _service_request method.
        :return: The results of the corresponding _service_request method.
        """
        return self._service_request("POST", *args, **kwargs)

    def _service_delete_request(self, *args, **kwargs):
        """
        DELETE request wrapper
        :param args: Positional arguments for _service_request method.
        :param kwargs: Keyword Arguments for _service_request method.
        :return: The results of the corresponding _service_request method.
        """
        return self._service_request("DELETE", *args, **kwargs)

    def _service_put_request(self, *args, **kwargs):
        """
        PUT request wrapper
        :param args: Positional arguments for _service_request method.
        :param kwargs: Keyword Arguments for _service_request method.
        :return: The results of the corresponding _service_request method.
        """
        return self._service_request("PUT", *args, **kwargs)

    def get_content(self, content_type=None, space_key=None, title=None, status=None, posting_day=None,
                    expand=None, start=None, limit=None, callback=None):
        """
        Returns a paginated list of Content.
        :param content_type (string): OPTIONAL: The content type to return. Default value: "page".
                                      Valid values: "page","blogpost".
        :param space_key (string): OPTIONAL: The space key to find content under.
        :param title (string): OPTIONAL: The title of the page to find. Required for page type.
        :param status (string): OPTIONAL: List of statuses the content to be found is in. Defaults to current
                                is not specified. If set to 'any', content in 'current' and 'trashed' status
                                will be fetched. Does not support 'historical' status for now.
        :param posting_day (string): OPTIONAL: The posting day of the blog post. Required for blogpost type.
                                     Format: yyyy-mm-dd. Example: 2013-02-13
        :param expand (string): OPTIONAL: A comma separated list of properties to expand on the content.
                                Default value: history,space,version
        :param start (int): OPTIONAL: The start point of the collection to return.
        :param limit (int): OPTIONAL: The limit of the number of items to return,
                            this may be restricted by fixed system limits.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
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
        """
        Returns a piece of Content.
        :param content_id (string): The id of the content.
        :param status (string): OPTIONAL: List of Content statuses to filter results on. Default value: [current]
        :param version (int): OPTIONAL: The content version to retrieve. Default: Latest.
        :param expand (string): OPTIONAL: A comma separated list of properties to expand on the content.
                                Default value: history,space,version We can also specify some extensions such as
                                extensions.inlineProperties (for getting inline comment-specific properties) or
                                extensions.resolution for the resolution status of each comment in the results.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/{id} endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
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
        """
        Returns the history of a particular piece of content
        :param content_id (string): The id of the content.
        :param expand (string): OPTIONAL: The properties on content history to expand.
                                Default: previousVersion,nextVersion,lastUpdated
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/{id}/history endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}/history".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_macro_by_hash(self, content_id, version, macro_hash, callback=None):
        """
        Returns the body of a macro (in storage format) with the given hash.
        This resource is primarily used by connect applications that require the body of macro to perform their work.

        The hash is generated by connect during render time of the local macro holder and
        is usually only relevant during the scope of one request. For optimisation purposes, this hash will usually
        live for multiple requests.

        Collecting a macro by its hash should now be considered deprecated and will be replaced,
        transparently with macroIds. This resource is currently only called from connect addons
        which will eventually all use the
        {@link #getContentById(com.atlassian.confluence.api.model.content.id.ContentId,
        java.util.List, Integer, String)} resource.

        To make the migration as seamless as possible, this resource will match macros against a generated hash or a
        stored macroId. This will allow add ons to work during the migration period.
        :param content_id (string): A string containing the id of the content.
        :param version (int): The version of the content which the hash belongs.
        :param macro_hash (string): The macroId to find the correct macro
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        return self._service_get_request("rest/api/content/{id}/history/{version}/macro/hash/{hash}"
                                         "".format(id=content_id, version=version, hash=macro_hash), callback=callback)

    def get_content_macro_by_macro_id(self, content_id, version, macro_id, callback=None):
        """
        Returns the body of a macro (in storage format) with the given id.
        This resource is primarily used by connect applications that require the body of macro to perform their work.

        When content is created, if no macroId is specified, then Confluence will generate a random id.
        The id is persisted as the content is saved and only modified by Confluence if there are conflicting IDs.

        To preserve backwards compatibility this resource will also match on the hash of the macro body, even if a
        macroId is found. This check will become redundant as pages get macroId's generated for them and transparently
        propagate out to all instances.
        :param content_id (string): A string containing the id of the content.
        :param version (int): The version of the content to search.
        :param macro_id (string): The macroID to find the corresponding macro.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        return self._service_get_request("rest/api/content/{id}/history/{version}/macro/id/{macro_id}"
                                         "".format(id=content_id, version=int(version), macro_id=macro_id),
                                         callback=callback)

    def search_content(self, cql_str=None, cql_context=None, expand=None, start=0, limit=None, callback=None):
        """
        Fetch a list of content using the Confluence Query Language (CQL).
        See: Advanced searching using CQL (https://developer.atlassian.com/display/CONFDEV/Advanced+Searching+using+CQL)
        :param cql_str (string): OPTIONAL: A cql query string to use to locate content.
        :param cql_context (string): OPTIONAL: The context to execute a cql search in,
                                     this is the json serialized form of SearchContext
        :param expand (string): OPTIONAL: A comma separated list of properties to expand on the content. Default: Empty.
        :param start (int): OPTIONAL: The start point of the collection to return. Default: 0
        :param limit (int): OPTIONAL: The limit of the number of items to return,
                                      this may be restricted by fixed system limits. Default: 25.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/search endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        params = {}
        if cql_str:
            params["cql"] = cql_str
        if cql_context:
            params["cqlcontext"] = json.dumps(cql_context)
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/search", params=params, callback=callback)

    def get_content_children(self, content_id, expand=None, parent_version=None, callback=None):
        """
        Returns a map of the direct children of a piece of Content. Content can have multiple types of children -
        for example a Page can have children that are also Pages, but it can also have Comments and Attachments.

        The {@link ContentType}(s) of the children returned is specified by the "expand" query parameter in the request
        - this parameter can include expands for multiple child types.
        If no types are included in the expand parameter, the map returned will just list the child types that
        are available to be expanded for the {@link Content} referenced by the "content_id" parameter.
        :param content_id (string): A string containing the id of the content to retrieve children for.
        :param expand (string): OPTIONAL :A comma separated list of properties to expand on the children.
                                Default: None.
        :param parent_version (int): OPTIONAL: An integer representing the version of the content to retrieve
                                     children for. Default: 0 (Latest)

        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/{id}/child endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        params = {}
        if expand:
            params["expand"] = expand
        if parent_version:
            params["parentVersion"] = parent_version
        return self._service_get_request("rest/api/content/{id}/child".format(id=content_id), params=params,
                                         callback=callback)

    def get_content_children_by_type(self, content_id, child_type, expand=None, parent_version=None,
                                     start=None, limit=None, callback=None):
        """
        Returns the direct children of a piece of Content, limited to a single child type.

        The {@link ContentType}(s) of the children returned is specified by the "type" path parameter in the request.
        :param content_id (string): The ID of the content to retrieve children for.
        :param child_type (string): A {@link ContentType} to filter children on.
        :param expand (string): OPTIONAL: A comma separated list of properties to expand on the children.
                                Default: None.
        :param parent_version (int): OPTIONAL: An int representing the version of the content to retrieve children for.
                               Default: 0 (latest).
        :param start (int): OPTIONAL: The start point of the collection to return. Default: 0
        :param limit (int): OPTIONAL: The limit of the number of items to return,
                                      this may be restricted by fixed system limits. Default: 25.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/{id}/child/{type} endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
        params = {}
        if expand:
            params["expand"] = expand
        if parent_version:
            params["parentVersion"] = parent_version
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/{id}/child/{type}".format(id=content_id, type=child_type),
                                         params=params, callback=callback)

    def get_content_descendants(self, content_id, expand=None, callback=None):
        """
        Returns a map of the descendants of a piece of Content. Content can have multiple types of descendants -
        for example a Page can have descendants that are also Pages, but it can also have Comments and Attachments.

        The {@link ContentType}(s) of the descendants returned is specified by the "expand" query parameter in the
        request - this parameter can include expands for multiple descendant types.
        If no types are included in the expand parameter, the map returned will just list the descendant types that
        are available to be expanded for the {@link Content} referenced by the "content_id" parameter.
        :param content_id (string): A string containing the id of the content to retrieve descendants for.
        :param expand (string): OPTIONAL: A comma separated list of properties to expand on the descendants.
                                Default: None.
        :param callback: OPTIONAL: The callback to execute on the resulting data, before the method returns.
                         Default: None (no callback, raw data returned).
        :return: The JSON data returned from the content/{id}/child/{type} endpoint, or the results of the callback.
                 Will raise requests.HTTPError on bad input, potentially.
        """
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

    def get_content_comments(self, content_id, expand=None, parent_version=None, start=None, limit=None,
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
            assert depth in {"", "all"}
            params["depth"] = depth
        return self._service_get_request("rest/api/content/{id}/child/comment".format(id=content_id),
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

    def get_property_by_content_id(self, content_id, property_key, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}/property/{key}".format(id=content_id, key=property_key),
                                         params=params, callback=callback)

    def get_op_restrictions_for_content_id(self, content_id, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/content/{id}/restriction/byOperation".format(id=content_id),
                                         params=params, callback=callback)

    def get_op_restrictions_by_content_operation(self, content_id, operation_key, expand=None, start=None, limit=None,
                                                 callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/content/{id}/restriction/byOperation/{opkey}"
                                         "".format(id=content_id, opkey=operation_key),
                                         params=params, callback=callback)

    def get_long_tasks(self, expand=None, start=None, limit=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/longtask", params=params, callback=callback)

    def get_long_task_info(self, long_task_id, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/longtask/{id}".format(id=long_task_id), params=params,
                                         callback=callback)

    def get_spaces(self, space_key=None, expand=None, start=None, limit=None, callback=None):
        params = {}
        if space_key:
            params["spaceKey"] = space_key
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/space", params=params, callback=callback)

    def get_space_information(self, space_key, expand=None, callback=None):
        params = {}
        if expand:
            params["expand"] = expand
        return self._service_get_request("rest/api/space/{key}".format(key=space_key),
                                         params=params, callback=callback)

    def get_space_content(self, space_key, depth=None, expand=None, start=None, limit=None, callback=None):
        params = {}
        if depth:
            assert depth in {"all", "root"}
            params["depth"] = depth
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/space/{key}/content".format(key=space_key),
                                         params=params, callback=callback)

    def get_space_content_by_type(self, space_key, content_type, depth=None, expand=None, start=None, limit=None,
                                  callback=None):
        params = {}
        if depth:
            assert depth in {"all", "root"}
            params["depth"] = depth
        if expand:
            params["expand"] = expand
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)
        return self._service_get_request("rest/api/space/{key}/content/{type}".format(key=space_key, type=content_type),
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

    def create_new_property(self, content_id, property_key, new_property_data, callback=None):
        assert isinstance(new_property_data, dict) and {"key", "value"} <= set(new_property_data.keys())
        return self._service_post_request("rest/api/content/{id}/property/{key}".format(id=content_id,
                                                                                        key=property_key),
                                          data=json.dumps(new_property_data),
                                          headers={"Content-Type": "application/json"}, callback=callback)

    def create_new_content_property(self, content_id, content_property, callback=None):
        assert isinstance(content_property, dict)
        assert {"key", "value"} <= set(content_property.keys())
        return self._service_post_request("rest/api/content/{id}/property".format(id=content_id),
                                          data=json.dumps(content_property),
                                          headers={"Content-Type": "application/json"}, callback=callback)

    def create_new_space(self, space_definition, callback=None):
        assert isinstance(space_definition, dict) and {"key", "name", "description"} <= set(space_definition.keys())
        return self._service_post_request("rest/api/space", data=json.dumps(space_definition),
                                          headers={"Content-Type": "application/json"}, callback=callback)

    def create_new_private_space(self, space_definition, callback=None):
        assert isinstance(space_definition, dict) and {"key", "name", "description"} <= set(space_definition.keys())
        return self._service_post_request("rest/api/space/_private", data=json.dumps(space_definition),
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

    def update_property(self, content_id, property_key, new_property_data, callback=None):
        assert isinstance(new_property_data, dict) and {"key", "value", "version"} <= set(new_property_data.keys())
        return self._service_put_request("rest/api/content/{id}/property/{key}".format(id=content_id, key=property_key),
                                         data=json.dumps(new_property_data),
                                         headers={"Content-Type": "application/json"}, callback=callback)

    def update_space(self, space_key, space_definition, callback=None):
        assert isinstance(space_definition, dict) and {"key", "name", "description"} <= set(space_definition.keys())
        return self._service_put_request("rest/api/space/{key}".format(key=space_key),
                                         data=json.dumps(space_definition),
                                         headers={"Content-Type": "application/json"}, callback=callback)

    def convert_contentbody_to_new_type(self, content_data, old_representation, new_representation, callback=None):
        assert {old_representation, new_representation} < {"storage", "editor", "view", "export_view"}
        # TODO: Enforce conversion rules better here.
        request_data = {"value": str(content_data), "representation": old_representation}
        return self._service_put_request("rest/api/contentbody/convert/{to}".format(to=new_representation),
                                         data=json.dumps(request_data),
                                         headers={"Content-Type": "application/json"}, callback=callback)

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

    def delete_property(self, content_id, property_key, callback=None):
        return self._service_delete_request("rest/api/content/{id}/property/{key}"
                                            "".format(id=content_id, key=property_key), callback=callback)

    def delete_space(self, space_key, callback=None):
        return self._service_delete_request("rest/api/space/{key}".format(key=space_key),
                                            callback=callback)