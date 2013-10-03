import os
import sys
import re
import random
import urllib2
import time
from pprint import pprint
#import gzip
import zlib
from cookielib import CookieJar

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)",
    "Opera/9.20 (Windows NT 6.0; U; en)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.0",
    "Opera/9.00 (Windows NT 5.1; U; en)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
]

def get(
    url,
    user_agent=None,
    verbose=False,
    max_retries=10,
    initial_delay_seconds=2,
    retry_delay_multiplier=2,
    ignore_404=True,
    ignore_410=True,
    ignore_500=True,
    ignore_400=True,
    ignore_403=True,
    timeout=10,
    allow_cookies=False,
    max_delay_seconds=30):
    """
    Retreives the content of a URL, applying a customizable user-agent and
    intelligentally waiting when network errors are encountered.
    """
    
    opener = None
    if allow_cookies:
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    
    _user_agent = user_agent
    for retry in xrange(max_retries):
        try:
            if _user_agent is None:
                user_agent = random.choice(USER_AGENTS)
            if verbose:
                print url
            
            if opener:
                opener.addheaders = [('User-agent', user_agent), ('Accept', '*/*')]
                response = opener.open(url, timeout=timeout)
            else:
                request = urllib2.Request(
                    url=url,
                    headers={'User-agent': user_agent, 'Accept': '*/*'})
                response = urllib2.urlopen(request, timeout=timeout)
                
            break
        except urllib2.HTTPError, e:
            if ignore_400 and '400' in str(e):
                return
            if ignore_410 and '410' in str(e):
                return
            if ignore_403 and '403' in str(e):
                return
            if ignore_404 and '404' in str(e):
                return
            if ignore_500 and '500' in str(e):
                return
            if 'not found' in str(e).lower() and not ignore_404:
                raise
            if verbose:
                print 'scrapper.get.error: %s' % (e,)
            if retry == max_retries-1:
                raise
            # Wait a short while, in case the error is due to a temporary
            # networking problem.
            time.sleep(min(
                max_delay_seconds,
                initial_delay_seconds + retry*retry_delay_multiplier))
    html = response.read()
    if response.headers.get('Content-Encoding', '').lower().strip() == 'gzip':
        html = zlib.decompress(html, 15 + 32)
    return html
