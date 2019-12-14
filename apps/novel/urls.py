from django.urls import path,re_path,include
from . import views
from django.views.decorators.cache import cache_page

app_name = 'novel'
urlpatterns = [
    # 小说详情
    re_path(r'detail/(?P<novel_id>[0-9a-zA-Z]{22})/', views.detail, name='detail'),
    # 章节
    re_path(r'chapter/(?P<chapter_id>[0-9a-zA-Z]{22})/', views.chapter_view, name='chapter'),
    # 排行榜
    path('rank/', views.RankView.as_view(), name='rank'),
    # 全部
    path('whole/', views.WholeView.as_view(), name='whole'),
    #     # 搜索
    path('search/', views.Search(), name='search'),
    # 收藏图书
    path('collect/',views.collect_novel,name='collect'),
    # 取消收藏
    path('cancel_collect/',views.cancel_collect,name='cancel_collect'),
    # 每个分类首页
    re_path(r'(?P<category_name>[a-z]*?)/',views.index_category, name='index_category'),
]