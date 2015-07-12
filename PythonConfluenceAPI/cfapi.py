__author__ = 'Robert Cope'

from requests.auth import HTTPBasicAuth
from api import ConfluenceAPI, api_logger, json
from requests_futures.sessions import FuturesSession
from urlparse import urljoin


# By default requests-futures request method returns the response object instead of the results of the callback;
# this is undesirable here, since the callback result is really the expected end result. This patches the module
# to get that expected behavior.
def request_patch(self, *args, **kwargs):
    """Maintains the existing api for Session.request.
    Used by all of the higher level methods, e.g. Session.get.
    The background_callback param allows you to do some processing on the
    response in the background, e.g. call resp.json() so that json parsing
    happens in the background thread.
    """
    func = sup = super(FuturesSession, self).request

    background_callback = kwargs.pop('background_callback', None)
    if background_callback:
        def wrap(*args_, **kwargs_):
            resp = sup(*args_, **kwargs_)
            # Patch the closure to return the callback.
            return background_callback(self, resp)

        func = wrap
    return self.executor.submit(func, *args, **kwargs)

FuturesSession.request = request_patch


class ConfluenceFuturesAPI(ConfluenceAPI):
    def __init__(self, username, password, uri_base, user_agent=ConfluenceAPI.DEFAULT_USER_AGENT,
                 executor=None, max_workers=10):
        """
        Initialize the async concurrent.futures API object.
        :param username: Your Confluence username.
        :param password: Your Confluence password.
        :param uri_base: The base url for your Confluence wiki (e.g. myorg.atlassian.com/wiki)
        :param user_agent: (Optional): The user-agent you wish to send on requests to the API.
                           DEFAULT: PythonConfluenceAPI.
        :param executor: (Optional): The concurrent.futures executor to power the API calls. Default: None, create a
                         new ThreadPoolExecutor.
        :param max_workers: (Optional): If the executor is not specified and the default ThreadPoolExecutor is spawned,
                            this specifies the number of worker threads to create.
        """
        super(ConfluenceFuturesAPI, self).__init__(username, password, uri_base, user_agent)
        self.executor = executor
        self.max_workers = max_workers

    def _start_http_session(self):
        """
        Start a new requests HTTP session, clearing cookies and session data.
        :return: None
        """
        api_logger.debug("Starting new HTTP session...")
        self.session = FuturesSession(executor=self.executor, max_workers=self.max_workers)
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
        :return: The concurrent.futures object that holds the future for the API method call.
        """
        api_logger.debug("Sending request: {} ({})".format(sub_uri, request_type))
        if not self.session:
            self._start_http_session()
        uri = urljoin(self.uri_base, sub_uri)
        if params:
            kwargs.update(params=params)
        if callback:
            def base_callback(_, response):
                if raise_for_status:
                    response.raise_for_status()
                return callback(response)
        else:
            def base_callback(_, response):
                if raise_for_status:
                    response.raise_for_status()
                return response.content if raw else json.loads(response.text)
        response_future = self.session.request(request_type, uri, background_callback=base_callback, **kwargs)
        return response_future