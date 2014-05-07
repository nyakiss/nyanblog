# -*- coding: utf-8 -*-
# Database:
#
# SQLite3:
# from os.path import join, dirname, abspath
# ROOT = abspath(dirname(__file__))
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(ROOT, 'blogpy.db')
#
# MySQL:
# CREATE DATABASE blogpy_db CHARACTER SET utf8;
# CREATE USER blogpy_user@localhost IDENTIFIED BY 'blogpy_passwd';
# GRANT ALL ON blogpy_user.* TO blogpy_user@localhost;
#
# SQLALCHEMY_DATABASE_URI = 'mysql://blogpy_user:blogpy_passwd@localhost:3306/blogpy_db'
#
# PostgreSQL
# SQLALCHEMY_DATABASE_URI = 'postgresql://blogpy_user:blogpy_passwd@localhost:5432/blogpy_db'
#
# Cache:
#
# Memcached:
# CACHE_TYPE = 'memcached'
# CACHE_MEMCACHED_SERVERS = ['localhost:11211', ]
# CACHE_KEY_PREFIX = 'blogpy'
#
# FileSystemCache
# CACHE_TYPE = 'filesystem'
# CACHE_DIR = '/tmp/blogpy'

DEBUG = False

PAGINATION_PER_PAGE = 10

ULOGIN_WIDGET_URL = 'http://ulogin.ru/js/widget.js'
ULOGIN_TOKEN_URL = 'http://ulogin.ru/token.php'
ULOGIN_DISPLAY = 'panel'
ULOGIN_OPTIONAL = ('first_name', 'last_name', 'nickname')
ULOGIN_FIELDS = (
    'email',
)
ULOGIN_PROVIDERS = (
    'google', 'yandex',
    'vkontakte', 'facebook',
    'livejournal', 'twitter',
    'openid',
)
ULOGIN_HIDDEN = (
    'odnoklassniki', 'mailru',
)

# SITE_TITLE = "Blog"

POST_TEMPLATE = """Post title
===========

:summary: "Post description"

Dear friends...
"""

ABOUT = """
<h1>Hello!</h1>
<p>My name is %username% and i'm awesome!</p>
"""



