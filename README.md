1. 添加环境变量：PATH="$PATH":/usr/local/mysql/bin
2. 激活venv: source ./venv/bin/activate
3. 使用pip 安装相应的包

pip install Flask
pip install flask-sqlalchemy
pip install MySQL-python


==========
注意：安装MySQL-python


## 启动

`javacript`
$ cd /Users/ian/gmagon_projects/gmagon_all/api_gmagon_web/python/
$ source ./venv/bin/activate
$ python api/wsgi.py
`end`


#### 启动服务器 
rhc app-start -a apiserver -n gmagon

#### 停止服务器
rhc app-stop -a apiserver -n gmagon

#### 查询服务器上的日志
rhc tail -a apiserver -n gmagon
