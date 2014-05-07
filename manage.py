#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from os import makedirs, urandom
from os.path import join, dirname, abspath, isfile
from shutil import copy, copytree

sys.path.append(abspath(dirname(__file__)))

from flask.ext.script import Command, Option, Server, Shell, Manager
from flask.ext.script import prompt_bool
from blogpy import app, db


class CreateInstance(Command):

    description = "Make instance folder and copy example config to it."

    def run(self):
        try:
            makedirs(join(app.instance_path, 'templates'))
        except OSError:
            pass
        copytree(join(app.root_path, 'static'),
                 join(app.instance_path, 'static'))
        example_config = join(app.root_path, 'settings.py')
        config = join(app.instance_path, 'settings.cfg')
        if not isfile(config):
            copy(example_config, config)
            with open(config, 'r+') as f:
                f.seek(0, 2)
                f.write("\nSECRET_KEY=%r\n" % urandom(24))
            print("Please, edit %s and then run 'manage.py createdb'" % config)


class CreateDb(Command):

    description = "Create all tables in database."

    def run(self):
        app.configure(
            SQLALCHEMY_ECHO=True,
        )
        db.create_all()


class AddAdmin(Command):

    description = "Add blog admin"

    def get_options(self):
        return [
            Option('-e', '--email', dest='email', required=True),
        ]

    def run(self, email):
        app.configure(
            SQLALCHEMY_ECHO=True,
        )
        from blogpy.models import User
        email = email.decode('utf-8')
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(u'', email, u'write')
        else:
            user.access = u'write'
        db.session.add(user)
        db.session.commit()


class DropDb(Command):

    description = "Drop all tables in database."

    def run(self):
        if prompt_bool("Are you sure you want to lose all your data"):
            app.configure(
                SQLALCHEMY_ECHO=True,
            )
            db.drop_all()


class CustomServer(Server):

    def handle(*args, **kwargs):
        app.configure(DEBUG=True)
        Server.handle(*args, **kwargs)


class CustomShell(Shell):

    def run(*args, **kwargs):
        app.configure(
            SQLALCHEMY_ECHO=True,
        )
        Shell.run(*args, **kwargs)


if __name__ == "__main__":
    manager = Manager(app)
    manager.add_command('addadmin', AddAdmin())
    manager.add_command('createinstance', CreateInstance())
    manager.add_command('createdb', CreateDb())
    manager.add_command('dropdb', DropDb())
    manager.add_command('runserver', CustomServer())
    manager.add_command('shell', CustomShell())
    manager.run()
