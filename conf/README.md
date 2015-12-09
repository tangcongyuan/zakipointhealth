Environment Configuration
=========================

Place these files in the directories as indicated below in the form of shell commands. But first set the server name using `sudo hostname whatever`

```
sed "s/HOSTNAME/$HOSTNAME/g" < conf/server.conf > /tmp/server.conf
sudo cp /tmp/server.conf /etc/nginx/conf.d/
sudo cp gunicorn.service /etc/systemd/system/
sudo cp nginx.conf /etc/nginx/
```
To restart the web server and django:
```
$ sudo systemctl restart nginx; sudo systemctl restart gunicorn
```

In the `static` directory, set up the link:
```
lrwxrwxrwx.  1 j userz   68 Oct 27 07:44 admin -> /usr/lib64/python2.7/site-packages/django/contrib/admin/static/admin
```

To start mongodb,
```
sudo -u mongod mongod &
```
It would be better to implement it as a service. 