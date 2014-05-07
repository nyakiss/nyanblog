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

from datetime import datetime
from flask import g, request, session
from flask import render_template, redirect, url_for, abort
from flask import jsonify, send_from_directory
from . import app, cache
from .models import db, User, Post, Comment, Tag, File
from .models import get_tags, on_post_change
from .forms import PostForm, CommentForm
from .decorators import login_required
from .ulogin import ulogin_url, ulogin_response


@app.before_request
def before_request():
    g.user = db.session.merge(session['user']) if 'user' in session else None


@app.route('/login', methods=['GET', 'POST'])
def login():
    url = request.args.get('next', '') or url_for('home')
    if g.user is not None:
        return redirect(url)
    if request.method == 'POST':
        if 'token' not in request.form:
            abort(403)
        u = ulogin_response()
        if 'error' in u:
            abort(403)
        if 'nickname' not in u or not u['nickname']:
            if 'first_name' in u and 'last_name' in u:
                u['nickname'] = u'%s %s' % (u['first_name'], u['last_name'])
            elif 'first_name' in u:
                u['nickname'] = u['first_name']
            else:
                u['nickname'] = u'Anonymous'
        user = User.query.filter_by(email=u['email']).first()
        if not user:
            access = u'comment' if User.query.count() > 0 else u'write'
            user = User(u['nickname'], u['email'], access)
            db.session.add(user)
            db.session.commit()
        elif not user.name:
            user.name = u['nickname']
            db.session.commit()
        session['user'] = user
        return redirect(url)
    return render_template('login.html', ulogin_url=ulogin_url)


@app.route('/logout')
def logout():
    if g.user is not None:
        session.pop('user')
    url = request.args.get('next', url_for('home'))
    return redirect(url)


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def home(page):
    query = Post.query.order_by(Post.id.desc())
    pagination = query.paginate(page, app.config['PAGINATION_PER_PAGE'])
    return render_template('list.html', posts=pagination.items,
        pagination=pagination)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(int(id))
    form = CommentForm()
    if form.validate_on_submit():
        if not g.user or not g.user.can_comment:
            abort(403)
        comment = Comment(g.user, form.text.data, post)
        db.session.add(comment)
        db.session.commit()
        form.text.data = None
    return render_template('post.html', post=post, form=form)


@app.route('/tag/<id>', defaults={'page': 1})
@app.route('/tag/<id>/page/<int:page>')
def tag(id, page):
    tag = Tag.query.filter(Tag.name.ilike(id)).first_or_404()
    query = tag.posts.order_by(Post.id.desc())
    pagination = query.paginate(page, app.config['PAGINATION_PER_PAGE'])
    return render_template('list.html', tag=tag, posts=pagination.items,
        pagination=pagination)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if not g.user or not g.user.can_write:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post = Post(g.user, form.text.data, get_tags(form.tags.data.strip()))
        db.session.add(post)
        db.session.commit()
        on_post_change()
        return redirect(url_for('post', id=post.id))
    else:
        if not form.text.data:
            form.text.data = app.config.get('POST_TEMPLATE', '')
    return render_template('new.html', form=form)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if not g.user or not g.user.can_write:
        abort(403)
    if 'file' in request.files:
        file = File(request.files['file'])
        db.session.add(file)
        db.session.commit()
        return jsonify(success=True, url=file.file_url)
    return jsonify(success=False)


@app.route('/uploads/<path:path>')
def uploads(path):
    return send_from_directory(app.config['UPLOAD_FOLDER'], path)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not g.user or not g.user.can_write:
        abort(403)
    post = Post.query.get(int(id))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        form.tags.data = get_tags(form.tags.data.strip())
        form.populate_obj(post)
        post.updated = datetime.utcnow()
        db.session.commit()
        on_post_change(id)
        return redirect(url_for('post', id=post.id))
    form.tags.data = u' '.join(unicode(tag) for tag in post.tags)
    return render_template('new.html', form=form)


@app.route('/delete/<type>/<int:id>')
@login_required
def delete(type, id):
    if not g.user or not g.user.can_write:
        abort(403)
    model = Comment if type == 'comment' else Post
    obj = model.query.get_or_404(int(id))
    if type == 'comment':
        id = obj.post.id
    db.session.delete(obj)
    db.session.commit()
    on_post_change(id)
    url = request.args.get('next', url_for('home'))
    return redirect(url)


@app.route('/rss.xml')
def rss():
    rss = cache.get('rss')
    if rss is None:
        now = datetime.utcnow()
        posts = Post.query.order_by(Post.id.desc()).limit(20)
        rss = render_template('rss.xml', posts=posts, now=now)
        cache.set('rss', rss)
    return rss


@app.route('/about')
def about():
    return render_template('about.html')
