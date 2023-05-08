# Django xiaoshuo
#### 这是一个django后端框架开发的小说网站（仿照起点中文网，参照了其前端布局）
#### [预览](http://www.ykjzone.com:7000)
## 主要功能
#### 首页
+ 小说 详情 章节 目录 排行榜
#### 个人中心 
+ 最近阅读 我的收藏 我的作品 发布 编辑 删除 连载/完本
#### CMS后台管理 /cms
+ 分类 标签 广告 推荐小说
#### 账号
+ 注册/登录

## 数据库表结构和数据
    下载链接: https://pan.baidu.com/s/1otQrEfmebaycbMS96Or7xg?pwd=amxe 提取码: amxe 直接点击下载即可

## 运行环境
### Ubuntu + uwsgi + nginx + supervisor
## 安装
#### 安装mysql
    sudo apt install mysql-server mysql-client
#### 安装redis
    sudo apt-get install redis-server
#### 安装virtualenvwrapper
    pip install virtualenvwrapper
#### 创建虚拟环境 django-env
    mkvirtualenv --python=/usr/bin/python3 django-env
#### 安装项目依赖的包
    pip install -r requirements.txt
#### 将模型映射到数据库中
    python manage.py makemigrations/migrate
#### 收集静态文件
    python manage.py collectstatic
#### 安装uwsgi
    pip3 install uwsgi
#### 安装和配置nginx
    apt install nginx
#### 安装supervisor
    pip3 install supervisor
## 运行
进入到项目所在目录，运行

    service nginx start
    supervisord -c supervisor
    
# 预览
[点击此处查看网页](http://www.ykjzone.com:7000)

## 首页
![首页](https://github.com/yankangjia/xiaoshuo/raw/master/preview/index.png)

