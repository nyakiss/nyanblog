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

from flask.ext.wtf import Form, TextField, TextAreaField
from flask.ext.wtf import Required, Length, ValidationError
from flask.ext.babel import gettext as _
from parsers import rstDocument


class PostForm(Form):
    text = TextAreaField(_("Text"), validators=[Required()])
    tags = TextField(_("Tags"), validators=[Required()])
    
    def validate_text(form, field):
        rendered = rstDocument(field.data)
        if not rendered.title:
            raise ValidationError(_("Title is not set"))


class CommentForm(Form):
    text = TextAreaField(_("Text"), validators=[
        Length(5, 256, _("Field must be between 5 and 256 characters long."))
    ])
