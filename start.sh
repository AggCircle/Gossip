#!/bin/bash
# 从第一行到最后一行分别表示：
# 1. 收集静态文件到根目录，
# 2. 生成数据库可执行文件，
# 3. 根据数据库可执行文件来修改数据库
# 4. 用 uwsgi启动 django 服务
# python manage.py collectstatic --noinput&&
# python manage.py makemigrations&&
# python manage.py migrate&&
#apt-get install openssl&&
#mkdir -p /data/ssl/;cd /data/ssl&&
#openssl genrsa -out foobar.key 2048&&
#openssl req -new -key foobar.key -out foobar.csr&&
#openssl x509 -req -days 365 -in foobar.csr -signkey foobar.key -out foobar.crt&&
python manage.py makemigrations&&
python manage.py migrate&&
cd /home/Gossip
uwsgi --ini uwsgi.ini

tail -f /dev/null
#python manage.py runserver 0.0.0.0:8088