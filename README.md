# Django xiaoshuo
#### 这是一个django后端框架开发的小说网站（仿照起点中文网，参照了其前端布局）

## 主要功能
#### 首页
+ 小说 详情 章节 目录 排行榜
#### 个人中心
+ 最近阅读 我的收藏 我的作品 发布 编辑 删除 连载/完本
#### CMS后台管理
+ 分类 标签 广告 推荐小说
#### 账号
+ 注册/登录

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
[点击此处查看网页](119.3.225.205)

## 首页
![首页](https://github.com/yankangjia/xiaoshuo/raw/master/preview/index.png)

### 全部作品
![全部作品](http://119.3.225.205/media/preview/whole_novel.png)
### 小说详情
![全部作品](http://119.3.225.205/media/preview/whole_novel.png)
![全部作品](http://119.3.225.205/media/preview/whole_novel.png)
### 阅读章节
![全部作品](http://119.3.225.205/media/preview/whole_novel.png)
![全部作品](http://119.3.225.205/media/preview/whole_novel.png)

## 个人中心
### 个人首页
![个人首页](http://119.3.225.205/media/preview/account_index.png)
### 我的作品
![我的作品](http://119.3.225.205/media/preview/works_list.png)
### 发布小说
![发布小说](http://119.3.225.205/media/preview/pub_novel.png)
### 选择小说
![选择小说](http://119.3.225.205/media/preview/whole_novel.png)
### 章节列表
![章节列表](http://119.3.225.205/media/preview/chapter_list.png)

## CMS后台管理
### 管理首页
![管理首页](http://119.3.225.205/media/preview/cms_index.png)
### 所有小说
![所有小说](http://119.3.225.205/media/preview/cms_novel_list_.png)
### 广告位
![广告位](http://119.3.225.205/media/preview/cms_ad_set.png)
### 轮播图
![轮播图](http://119.3.225.205/media/preview/cms_banners.png)
### 优秀作品展示
![优秀作品展示](http://119.3.225.205/media/preview/cms_excellent.png)
### 分类
![分类](http://119.3.225.205/media/preview/cms_category_list.png)
### 标签
![标签](http://119.3.225.205/media/preview/cms_tag_list.png)

## 员工管理
### 员工管理
![员工管理](http://119.3.225.205/media/preview/cms_staffs.png)

