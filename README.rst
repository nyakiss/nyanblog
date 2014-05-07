nyanblog
#########

nyanblog is a blog engine written in Python using Flask

Example installation
--------------------
::

    cd /var/www
    git clone git://github.com/nyakiss/nyanblog.git
    cd nyanblog
    wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    python virtualenv.py pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
    python manage.py createinstance
    nano instance/settings.cfg
    python manage.py createdb
    python manage.py addadmin -e admin@example.com
    python manage.py runserver

nginx config
------------
::

    server {
        server_name example.com;

        location = /favicon.ico {
            root /var/www/nyanblog/instance/static;
        }
        location /static {
            root /var/www/nyanblog/instance;
        }
        location /uploads {
            root /var/www/nyanblog/instance;
        }
        location / {
            include uwsgi_params;
            uwsgi_pass 127.0.0.1:3030;
        }
    }

uWSGI config
------------
::

    [uwsgi]
    chdir = /var/www/nyanblog
    pythonpath = /var/www/nyanblog
    virtualenv = /var/www/nyanblog/pyenv
    module = application
    touch-reload = /var/www/nyanblog/instance/settings.cfg
    socket = 127.0.0.1:3030
    processes = 2
