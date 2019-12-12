from django.urls import path,include,re_path
from . import views, author_views

app_name = 'account'

# 个人中心
urlpatterns = [
    path('index/',views.index, name='index'),
    path('recently_read/',views.recently_read, name='recently_read'),
    path('my_collect/',views.my_collect, name='my_collect'),
    path('become_writer', views.BecomeWriter.as_view(), name='become_writer'),
]

# 作家专区
urlpatterns += [
    path('novel_list/',author_views.NovelList.as_view(), name='novel_list'),
    path('pub_novel/',author_views.PubNovel.as_view(), name='pub_novel'),
    path('edit_novel/',author_views.EditNovel.as_view(), name='edit_novel'),
    path('delete_novel/',author_views.delete_novel, name='delete_novel'),
    path('get_cate_list/',author_views.get_cate_list, name='get_cate_list'),
    path('upload_file/',author_views.upload_file, name='upload_file'),
    path('choose_novel/',author_views.choose_novel, name='choose_novel'),
    path('chapter_list/',author_views.ChapterList.as_view(), name='chapter_list'),
    path('write_chapter/',author_views.WriteChapter.as_view(), name='write_chapter'),
    path('edit_chapter/',author_views.EditChapter.as_view(), name='edit_chapter'),
    path('delete_chapter/',author_views.delete_chapter, name='delete_chapter'),
    path('set_finish/', author_views.set_finish, name='set_finish'),
    path('set_serialize/', author_views.set_serialize, name='set_serialize')
]