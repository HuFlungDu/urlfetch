#coding: utf8

import httplib
import socket
import urllib
import urlparse
import Cookie
from uas import randua as _randua

__all__ = ['sc2cs', 'fetch', 'fetch2'] 

def sc2cs(sc):
    '''convert response.getheader('set-cookie') to cookie string'''
    c = Cookie.SimpleCookie(sc)
    sc = ['%s=%s' % (i.key, i.value) for i in c.itervalues()]
    return '; '.join(sc)

def fetch(url, data=None, headers={}, timeout=None, randua=True):
    if data is not None and isinstance(data, (basestring, dict)):
        return fetch2(url, method="POST", data=data, headers=headers, timeout=timeout, randua=randua) 
    return fetch2(url, method="GET", data=data, headers=headers, timeout=timeout, randua=randua)

def fetch2(url, method="GET", data=None, headers={}, timeout=None, randua=True):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    method = method.upper()
    if method not in ("GET", "PUT", "DELETE", "POST", "HEAD"):
        method = "GET"
    
    if ':' in netloc:
        host, port = netloc.rsplit(':', 1)
        port = int(port)
    else:
        host, port = netloc, None
    
    if scheme == 'https':
        h = httplib.HTTPSConnection(host, port)
    elif scheme == 'http':
        h = httplib.HTTPConnection(host, port)
    else:
        raise Exception('Unsupported protocol %s' % scheme)
        
    if timeout is not None:
        h.connect()
        h.sock.settimeout(timeout)
    
    reqheaders = {
        'Accept' : '*/*',
        'User-Agent': _randua() if randua else 'Python urlfetch by lyxint',
    }

    if isinstance(data, dict):
        data = urllib.urlencode(data)
    
    if isinstance(data, basestring):
        if method == "POST":
            # httplib will set 'Content-Length', also you can set it by yourself
            reqheaders["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            url += "&%s" % data if "?" in url else "?%s" % data
            data = None

    reqheaders.update(headers)
    
    h.request(method, url, data, reqheaders)
    response = h.getresponse()
    setattr(response, 'reqheaders', reqheaders)
    setattr(response, 'body', response.read())
    h.close()
    
    return response


if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    
    response = fetch(url)
    print 'request headers', response.reqheaders
    print 'response headers', response.getheaders()
    print 'body length', len(response.body)
