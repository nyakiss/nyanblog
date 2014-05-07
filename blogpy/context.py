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

from math import log
from datetime import datetime
from flask import Markup, url_for, request, Markup
from flask.ext.babel import gettext as _, ngettext, format_datetime
from . import app, cache
from .models import Tag


@app.context_processor
def inject_context():
    context = cache.get('context')
    if context is None:
        tags_min = Tag.query.order_by(Tag.count.asc()).first()
        tags_max = Tag.query.order_by(Tag.count.desc()).first()
        tags_min = tags_min.count if tags_min else 0
        tags_max = tags_max.count if tags_max else 0
        tags_spread = log((tags_max - tags_min) or 1)
        context = dict(
            current_year=datetime.utcnow().year,
            tags=Tag.query.order_by(Tag.count.desc(), Tag.name.asc()).all(),
            tags_min=tags_min,
            tags_max=tags_max,
            tags_spread=tags_spread,
        )
        cache.set('context', context, 60*5)
    return context


@app.template_filter()
def render_tags(post, **kwargs):
    tags = cache.get('tags_%s' % post.id)
    if tags is None:
        delimiter = kwargs.pop('delimiter') if 'delimiter' in kwargs else ', '
        args = u' '.join(u'%s="%s"' % (k, kwargs[k]) for k in kwargs)
        format_str = (u'<a href="%s" ' + args).strip() +'>%s</a>'
        link = lambda x: format_str % (url_for('tag', id=x.name), x)
        tags = delimiter.join(link(tag) for tag in post.tags)
        cache.set('tags_%s' % post.id, tags, 60*5)
    return Markup(tags)


@app.template_filter()
def comment_filter(text):
    striptags = app.jinja_env.filters['striptags']
    lines = (striptags(line) for line in text.split('\n') if line)
    return Markup(' <br />\n'.join(lines))


@app.template_filter()
def timesince(dt, format='EEEE, d MMMM yyyy HH:mm UTC', default=None):
    now = datetime.utcnow()
    diff = now - dt
    periods = (
        (
            diff.days/3,
            format_datetime(dt, format)
        ),
        (
            diff.days,
            ngettext(u"%(num)s day ago", u"%(num)s days ago",
                diff.days)
        ),
        (
            diff.seconds/3600,
            ngettext(u"%(num)s hour ago", u"%(num)s hours ago",
                diff.seconds/3600)
        ),
        (
            diff.seconds/60,
            ngettext(u"%(num)s minute ago", u"%(num)s minutes ago",
                diff.seconds/60)
        ),
        (
            diff.seconds,
            ngettext(u"%(num)s second ago", u"%(num)s seconds ago",
                diff.seconds)
        ),
    )
    for period, result in periods:
        if period:
            return result
    return default or _(u"just now")


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


def calculate_tag_size(count, tags_min, tags_spread, min_size):
    try:
        size = log(count - (tags_min - 1)) / tags_spread + min_size
    except ZeroDivisionError:
        size = 1
    return size


app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.globals['url_for_other_page'] = url_for_other_page
app.jinja_env.globals['calculate_tag_size'] = calculate_tag_size
