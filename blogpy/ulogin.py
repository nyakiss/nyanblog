# Copyright (C) 2011 Bohdan Kanskyj
#
# blogpy - blog engine written in Python using Flask
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from urllib import urlencode, urlopen
from flask import request, json_available
from . import app, cache

if not json_available:
    raise RuntimeError('simplejson not installed')

from flask import json


def ulogin_response():

    def get_host(url):
        url = url[url.find(':')+3:]
        index = url.find('/')
        if index+1:
            url = url[:index]
        return url

    args = {
        'token': request.form['token'],
        'host': get_host(request.url),
    }
    response = urlopen('%s?%s' % (
        app.config['ULOGIN_TOKEN_URL'],
        urlencode(args),
    ))
    if response.getcode() != 200:
        return {'error': u'invalid response'}
    return json.load(response)


@cache.cached(timeout=60*5)
def ulogin_url():
    data = {
        'fields': ','.join(app.config['ULOGIN_FIELDS']),
        'optional': ','.join(app.config['ULOGIN_OPTIONAL']),
        'providers': ','.join(app.config['ULOGIN_PROVIDERS']),
        'hidden': ','.join(app.config['ULOGIN_HIDDEN']),
    }
    url = '%s?%s&%s' % (
        app.config['ULOGIN_WIDGET_URL'],
        urlencode({
            'display': app.config['ULOGIN_DISPLAY'],
            'redirect_uri': request.url,
        }),
        '&'.join('%s=%s' % (i, data[i]) for i in data.keys()),
    )
    return url

