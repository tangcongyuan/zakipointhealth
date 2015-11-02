Environment Configuration
=========================

Place these files in the directories as indicated below; in this directory, `conf`, set up links such that:
```
lrwxrwxrwx.  1 j userz   27 Nov  1 10:54 alfa.conf -> /etc/nginx/conf.d/alfa.conf
lrwxrwxrwx.  1 j userz   36 Nov  1 10:50 gunicorn.service -> /etc/systemd/system/gunicorn.service
lrwxrwxrwx.  1 j userz   21 Nov  1 10:50 nginx.conf -> /etc/nginx/nginx.conf
```
To restart the web server and django:
```
$ sudo systemctl restart nginx; sudo systemctl restart gunicorn
```

In the `static` directory, set up the link:
```
lrwxrwxrwx.  1 j userz   68 Oct 27 07:44 admin -> /usr/lib64/python2.7/site-packages/django/contrib/admin/static/admin
```
