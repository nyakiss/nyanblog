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

import sys

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

from os.path import join, dirname
from jinja2 import FileSystemLoader
from flask import Flask, request
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy

__all__ = [
    'app',
    'cache',
    'db',
]

sys.path.append(dirname(__file__))

app = Flask(__name__)

babel = Babel()
cache = Cache()
db = SQLAlchemy(app)

def configure(**kwargs):
    app.config['UPLOAD_FOLDER'] = join(app.instance_path, 'uploads')
    app.config.from_pyfile(join(app.root_path, 'settings.py'), silent=True)
    app.config.from_pyfile(join(app.instance_path, 'settings.cfg'), silent=True)
    app.config.update(kwargs)

    if not app.config.get('SQLALCHEMY_DATABASE_URI', None):
        print("SQLALCHEMY_DATABASE_URI is not in settings.cfg")
        exit(1)

    babel.init_app(app)
    localeselector = lambda: request.accept_languages.best_match(['ru', 'en'])
    babel.localeselector(localeselector)
    cache.init_app(app)
    db.init_app(app)

    templates_paths = [app.instance_path, app.root_path]
    templates_paths = [join(path, 'templates') for path in templates_paths]
    app.jinja_env.loader = FileSystemLoader(templates_paths)
    app.jinja_env.trim_blocks = True
    app.jinja_env.add_extension('jinja2.ext.do')
    
    app.static_folder = join(app.instance_path, 'static')

    if not app.debug:
        from logging import WARNING, FileHandler
        try:
            file_handler = FileHandler(join(app.instance_path, 'blogpy.log'))
            file_handler.setLevel(WARNING)
            app.logger.addHandler(file_handler)
        except IOError:
            print("Can't open log file for writing")
    
    from blogpy.parsers import setup
    
    setup(app, app.config)
    
    import blogpy.context
    import blogpy.views

app.configure = configure
