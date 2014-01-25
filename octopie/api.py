import requests, urllib
import collections
import json

_HTTP_GET = 0
_HTTP_POST = 1
SAFE_URL_CARS = ':+'
TIMEOUT_SEC = 30

class APIError(StandardError):
    """
    APIError contains json message indicating failure
    """
    def __init__(self, error_id, error_message, error_name, request,  *args, **kwargs):
        self.error_id = error_id
        self.error_message = error_message
        self.error_name = error_name
        self.request = request
        super(StandardError, self).__init__(*args, **kwargs)

    def __str__(self):
        return super(StandardError, self).__str__() + '\n' \
        'APIError: %s: %s\n%s\nURL: %s' % \
        (self.error_id, self.error_name, self.error_message, self.request)


def _encode_params(**kwargs):
    """
    Do url-encode parameters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    >>> _encode_params(a=u'\u4e2d\u6587', b=['A', 'B', 123])
    'a=%E4%B8%AD%E6%96%87&b=A&b=B&b=123'
    """

    args = []
    for k, v in kwargs.iteritems():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib.quote(qv, SAFE_URL_CARS)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(i, unicode) else str(i)
                args.append('%s=%s' % (k, urllib.quote(qv, SAFE_URL_CARS)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib.quote(qv, SAFE_URL_CARS)))
    return '&'.join(args)

def _encode_ids(*args):
    """
    Do url-encode resource ids
    """

    ids = []
    for v in args:
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            ids.append(urllib.quote(qv))
        else:
            qv = str(v)
            ids.append(urllib.quote(qv))

    return ';'.join(ids)

def _http_call(url, method, auth, client, *args, **kwargs):
    params = _encode_params(**kwargs)
    ids = ''
    credentials = ''
    url_format_str = '%s%s?%s'

    if args:
        ids = _encode_ids(*args)
        url_format_str = '%s/%s?%s'

    if auth:
        credentials = _encode_params(**auth)
        url_format_str += '&%s'

    http_url = url_format_str % (url, ids, params, credentials) \
               if method == _HTTP_GET else url

    try:
        result = requests.get(http_url,
                headers={'accept': 'application/vnd.github.preview'}, timeout=TIMEOUT_SEC)
    except requests.exceptions.ConnectionError as e:
        raise APIError('ConnectionError', 'ConnectionError', 'ConnectionError',
                       http_url, e)
    except requests.exceptions.Timeout as te:
        raise APIError('Timeout', 'Timeout', 'Timeout', http_url, te)
    except requests.exceptions.RequestException as re:
        raise APIError('RequestException', 'RequestException', 'RequestException', http_url, re)


    try:
        rv = json.loads(result.text)
        client._headers = result.headers

    except ValueError as e:
        raise APIError('ValueError', result.text, 'ValueError', http_url, e)

    if 'error_id' in result:
        raise APIError(result['error_id'], result['error_message'],
            result['error_name'], http_url)
    if 'message' in result:
        if 'rate limit exceeded' in result['message']:
            raise APIError('Rate limit exceeded' , result['message'],
                'Rate limit exceeded', http_url)

    return rv

class GitHubAPI(object):

    def __init__(self, client_id=None, client_secret=None, domain='api.github.com'):
        self.client_id = str(client_id)
        self.client_secret = str(client_secret)
        self.api_url = 'https://%s/' % domain
        self._headers = None

    def getHeaders(self):
        return self._headers

    def __getattr__(self, attr):
        if '__' in attr:
            return getattr(self.get, attr)
        return _Callable(self, attr)

class _Executable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._auth = None if client.client_id is None or client.client_secret is None \
                     else {'client_id': client.client_id, 'client_secret': client.client_secret}
        self._method = method
        self._path = path

    def __call__(self, *args, **kwargs):
        return _http_call('%s%s' % (self._client.api_url, self._path), \
            self._method, self._auth, self._client, *args, **kwargs)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%s(%s)" % (self.__class__, self.__dict__)

class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr == 'get':
            return _Executable(self._client, _HTTP_GET, self._name)
        if attr == 'post':
            return _Executable(self._client, _HTTP_POST, self._name)

        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __str__(self):
        return "%s(%s)" % (self.__class__, self.__dict__)
