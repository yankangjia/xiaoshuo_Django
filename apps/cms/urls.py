from django.urls import path, re_path
from . import views, cate_views, ad_views, staff_views

app_name = 'cms'


urlpatterns = [
    path('index/',views.index, name='index'),
    # 小说
    path('novel_list/',views.NovelList.as_view(), name='novel_list'),
    path('edit_novel/',views.EditNovel.as_view(), name='edit_novel'),
    path('choose_novel/',views.choose_novel, name='choose_novel'),
    path('chapter_list/',views.ChapterList.as_view(), name='chapter_list'),
    path('edit_chapter/',views.EditChapter.as_view(), name='edit_chapter'),
    path('delete_chapter/', views.delete_chapter, name='delete_chapter'),
    path('edit_chapter/', views.EditChapter.as_view(), name='delete_chapter'),
    path('set_recommend/', views.set_recommend, name='set_recommend'),
    path('cancel_recommend/', views.cancel_recommend, name='cancel_recommend'),

    # 上传图片
    path('upload_file/', views.upload_file, name='upload_file'),
]


urlpatterns += [
    # 分类
    path('category_list/', cate_views.category_list, name='category_list'),
    path('add_novel_category/', cate_views.add_novel_category, name='add_novel_category'),
    path('edit_novel_category/', cate_views.edit_novel_category, name='edit_novel_category'),
    path('delete_novel_category/', cate_views.delete_novel_category, name='delete_novel_category'),
    # 标签
    path('tag_list/', cate_views.tag_list, name='tag_list'),
    path('tag_detail/', cate_views.tag_detail, name='tag_detail'),
    path('delete_tag/', cate_views.delete_tag, name='delete_tag'),
    path('get_tags/', cate_views.get_tags, name='get_tags'),
    path('add_tag/', cate_views.add_tag, name='add_tag'),
    path('get_tag/', cate_views.get_tag, name='get_tag'),
    path('edit_tag/', cate_views.edit_tag, name='edit_tag'),
]


urlpatterns += [
    # 轮播图
    path('banners/', ad_views.banners_view, name='banners'),
    path('add_banner/', ad_views.add_banner, name='add_banner'),
    path('banner_list/', ad_views.banner_list, name='banner_list'),  # 异步获取
    path('delete_banner/', ad_views.delete_banner, name='delete_banner'),
    path('edit_banner/', ad_views.edit_banner, name='edit_banner'),
    # 广告位
    path('ad_set/', ad_views.ad_set, name='ad_set'),
    path('ad_add/', ad_views.ad_add, name='ad_add'),
    path('ad_edit/', ad_views.ad_edit, name='ad_edit'),
    path('get_ads/', ad_views.get_ads, name='get_ads'),
    # 优秀作品展示
    path('excellent/', ad_views.excellent_works, name='excellent'),
    path('edit_excellent_works/', ad_views.edit_excellent_works, name='edit_excellent_works')
]

# 权限管理
urlpatterns += [
    path('staffs/', staff_views.staffs_view, name='staffs'),
    path('add_staff/', staff_views.AddStaff.as_view(), name='add_staff'),
    re_path(r'edit_staff/(?P<staff_id>[0-9a-zA-Z]{22})/', staff_views.EditStaff.as_view(), name='edit_staff'),
    path('delete_staff/', staff_views.delete_staff, name='delete_staff'),
]