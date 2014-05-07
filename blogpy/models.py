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

import hashlib
from urllib import urlencode
from datetime import datetime
from os import makedirs
from os.path import join, isdir
from werkzeug import secure_filename
from werkzeug.utils import cached_property
from flask import url_for
from flask.ext.sqlalchemy import Pagination
from parsers import rstDocument
from . import app, cache, db


posts_tags = db.Table('posts_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('posts_id', db.Integer, db.ForeignKey('posts.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255), nullable=False)
    email = db.Column(db.Unicode(255), nullable=False)
    access = db.Column(db.Enum(u'read', u'comment', u'write', name='access'))

    def __init__(self, name, email, access=u'comment'):
        self.name = name
        self.email = email
        self.access = access

    def __repr__(self):
        return '<User %r>' % self.email

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')

    def avatar(self, size=96, default='identicon'):
        email = self.email.strip().lower().encode('utf-8')
        data = (hashlib.md5(email).hexdigest(), urlencode({'d': default, 's': size}))
        return (u'http://www.gravatar.com/avatar/%s?%s' % data)

    @property
    def can_write(self):
        return self.access in (u'write', )

    @property
    def can_comment(self):
        return self.access in (u'comment', u'write')


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    published = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', lazy='joined', innerjoin=True,
        backref=db.backref('posts'))
    tags = db.relationship('Tag', secondary=posts_tags, lazy='joined',
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, author, text, tags=None):
        self.author = author
        self.text = text
        if not tags:
            tags = []
        self.tags.extend(tags)

    def __repr__(self):
        return '<Post %r>' % self.title

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')
    
    @property
    def _rendered(self):
        self._rst = (getattr(self, '_rst', None) or
                     cache.get('post_%s_rendered' % self.id))
        if self._rst is None:
            self._rst = rstDocument(self.text)
            cache.set('post_%s_rendered' % self.id, self._rst)
        return self._rst

    @property
    def title(self):
        return self._rendered.title
    
    @property
    def body(self):
        return self._rendered.body
    
    @property
    def summary(self):
        return self._rendered.config.get('summary')

    @property
    def comment_count(self):
        count = cache.get('post_%s_comment_count' % self.id)
        if count is None:
            count = len(self.comments)
            cache.set('post_%s_comment_count' % self.id, count)
        return count

    @property
    def similar(self):
        result = cache.get('post_%s_similar' % self.id)
        if result is None:
            q = Post.query.join(Post.tags)
            q = q.filter(Tag.id.in_([t.id for t in self.tags[:3]]))
            q = q.filter(Post.id!=self.id)
            q = q.distinct(Post.id)
            q = q.order_by(Post.published.desc())
            result = q.limit(5).all()
            cache.set('post_%s_similar' % self.id, result)
        return result


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255), unique=True, nullable=False)
    count = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name
        self.count = 0

    def __repr__(self):
        return '<Tag %r>' % self.name

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,
        db.ForeignKey('posts.id', ondelete='CASCADE'))
    author = db.relationship('User', lazy='joined', innerjoin=True,
        backref=db.backref('comments'))
    post = db.relationship('Post',
        backref=db.backref('comments', lazy='joined',
            order_by='Comment.timestamp.desc()',
            cascade='all, delete-orphan', passive_deletes=True))

    def __init__(self, author, text, post):
        self.author = author
        self.text = text.replace('\r', '').strip()
        self.post = post

    def __repr__(self):
        return '<Comment %r>' % self.text

    def __unicode__(self):
        return self.text

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.Unicode(32), nullable=False)
    uploaded = db.Column(db.DateTime, nullable=False)
    file_name = db.Column(db.Unicode(255), nullable=False)

    @cached_property
    def _path(self):
        path = self.uploaded.utctimetuple()[:3]
        return '/'.join((str(i) for i in path))

    @cached_property
    def _directory(self):
        directory = '/'.join([app.config['UPLOAD_FOLDER'], self._path])
        if not isdir(directory):
            makedirs(directory)
        return directory

    @cached_property
    def file_url(self):
        path = '/'.join([self._path, self.file_name])
        return url_for('uploads', path=path)

    @cached_property
    def file_path(self):
        return '/'.join([self._directory, self.file_name])

    def process_upload(self, file):
        if isinstance(file, basestring):
            stream = open(file, 'rb')
        else:
            stream = file
        buff_size = 32 * 1024
        buff = True
        m = hashlib.md5()
        while buff:
            buff = stream.read(buff_size)
            m.update(buff)
        self.md5 = unicode(m.hexdigest())
        instance = type(self).query.filter_by(md5=self.md5).first()
        if instance is None:
            self.uploaded = datetime.utcnow()
            stream.seek(0)
            stream.save(self.file_path)
        else:
            self.file_name = instance.file_name
            self.uploaded = instance.uploaded
        if isinstance(file, basestring):
            stream.close()

    def __init__(self, file):
        self.file_name = secure_filename(file.filename)
        self.process_upload(file)


def get_tags(data):
    get_tag = lambda x: Tag.query.filter(Tag.name.ilike(x)).first() or Tag(x)
    return [get_tag(tag) for tag in data.split()]


def update_tags():
    tags = Tag.query.all()
    for tag in tags:
        tag.count = tag.posts.count()
        if not tag.count:
            db.session.delete(tag)
    db.session.commit()


def on_post_change(id=None):
    update_tags()
    cache.delete('context')
    cache.delete('rss')
    if id is not None:
        cache.delete('tags_%s' % id)
        cache.delete('post_%s_similar' % id)
        cache.delete('post_%s_rendered' % id)
        cache.delete('post_%s_comment_count' % id)

