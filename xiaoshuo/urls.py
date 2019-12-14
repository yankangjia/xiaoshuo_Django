"""xiaoshuo URL Configuration"""


from django.contrib import admin
from django.urls import path,include,re_path
from apps.novel import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.cache import cache_page

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', cache_page(15)(views.index), name='index'),
    path('', views.index, name='index'),
    path('novel/', include('apps.novel.urls')),
    path('account/', include('apps.account.urls')),
    path('ueditor/', include('apps.ueditor.urls')),
    path('xsauth/', include('apps.xsauth.urls')),
    path('cms/', include('apps.cms.urls')),
    # path('search/', include('haystack.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('__debug__/',include(debug_toolbar.urls)))
