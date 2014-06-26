# -*- coding: utf-8 -*-
"""
Copyright (c) 2011 by Christoph Heer

Some rights reserved.

Redistribution and use in source and binary forms of the software as well
as documentation, with or without modification, are permitted provided
that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.

* The names of the contributors may not be used to endorse or
  promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""
from __future__ import absolute_import
from jinja2 import Markup
from docutils.core import publish_parts

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from hashlib import sha1
from flask import url_for, make_response, request, abort

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

import re

config_parser_re = re.compile(r"^:(\w+): ?(.*?)$", re.M)

formatter = HtmlFormatter()


class Pygments(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            lexer = TextLexer()
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]


class Youtube(Directive):
    required_arguments = 1
    optional_arguments = 2
    final_argument_whitespace = True
    content = True

    def run(self):
        if not self.arguments:
            return None
        result = ('<div id="%(yid)s" class="youtube-preview" ' +
                'style="background: url(http://img.youtube.com/vi/%(yid)s/0.jpg) no-repeat scroll 0 -55px"><span class="y-play" data-icon="&#xe608;"></span></div>'
                ) % dict(yid=self.arguments[0])
        return [nodes.raw('', result, format='html')]


def setup(app, cfg):
    global formatter
    formatter = HtmlFormatter(style=cfg.get('style', 'tango'))
    directives.register_directive('sourcecode', Pygments)
    directives.register_directive('code-block', Pygments)
    directives.register_directive('youtube', Youtube)
    
    @app.route(cfg.get('css_file_route', "/static/pygments.css"))
    def pygments_css():
        etag = sha1(str(formatter.style)).hexdigest()
        if request.headers.get('If-None-Match') == etag:
            return "", 304
        else:
            res = make_response(formatter.get_style_defs())
            res.mimetype = "text/css"
            res.headers['ETag'] = etag
            return res


class rstDocument:
    def __init__(self, text):
        self.raw = text
        self._config = None
        self._rst = None

    @property
    def config(self):
        if not isinstance(self._config, dict):
            self._config = {}
            for m in config_parser_re.finditer(self.raw):
                self._config[m.group(1)] = eval(m.group(2))
            self._config.setdefault('public', False)
        return self._config

    @property
    def rst(self):
        if not isinstance(self._rst, dict):
            settings = {
                'initial_header_level': 2
            }
            self._rst = publish_parts(source=self.raw, \
                                      writer_name='html4css1',
                                      settings_overrides=settings)
        return self._rst

    @property
    def title(self):
        return Markup(self.rst['title']).striptags()

    @property
    def body(self):
        return Markup(self.rst['fragment'])

    def __repr__(self):
        return "<rstDocument %s>" % (self.raw)
