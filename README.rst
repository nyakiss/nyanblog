nyanblog
#########

nyanblog is a blog engine written in Python using Flask

Example installation on mysql
--------------------
::

    cd /var/www
    git clone git://github.com/nyakiss/nyanblog.git
    cd nyanblog
    apt-get install python-dev uwsgi-plugin-python python-virtualenv mysql-server mysql-client libmysqlclient-dev
    virtualenv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
    python manage.py createinstance
    nano instance/settings.cfg
    mysql -u root -p
		CREATE DATABASE blogpy_db CHARACTER SET utf8;
		CREATE USER blogpy_user@localhost IDENTIFIED BY 'blogpy_passwd';
		GRANT ALL ON blogpy_user.* TO blogpy_user@localhost;
		GRANT ALL ON blogpy_db.* TO blogpy_user@localhost;
    python manage.py createdb
    python manage.py addadmin -e admin@example.com

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
