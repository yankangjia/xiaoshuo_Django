from django.shortcuts import render,reverse,redirect
from django.conf import settings
from utils import restful
from django.views.generic import View
from apps.novel.models import Novel, NovelCategory, NovelChapter
from .forms import NovelForm,ChapterForm
from django.utils.timezone import make_aware
from datetime import datetime
from urllib import parse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from apps.xsauth.decorators import xs_permission_required,xs_login_required
from django.views.decorators.http import require_POST
import os,time


# 首页
@staff_member_required(login_url='/')
def index(request):
    context = {
        'range10':range(10)
    }
    return render(request,'cms/index.html',context=context)

# 小说列表
@method_decorator(permission_required(perm='novel.change_novel',login_url='/'), name='dispatch')
class NovelList(View):
    def get(self, request):
        novels = Novel.objects.select_related('category','author')

        # 过滤条件
        start = request.GET.get('start')
        end = request.GET.get('end')
        name = request.GET.get('name')
        category_id = int(request.GET.get('category_id',0) or 0)

        # 分类过滤
        if category_id:
            novels = novels.filter(category__id=category_id)
        # 时间过滤
        if start:
            start_date = datetime.strptime(start, '%Y/%m/%d')
        else:
            start_date = datetime(year=2019, month=11, day=1)
        if end:
            end_date = datetime.strptime(end, '%Y/%m/%d')
        else:
            end_date = datetime.today()
        start_date = make_aware(start_date)
        end_date = make_aware(end_date)
        novels = novels.filter(pub_date__range=(start_date, end_date))
        # 标题过滤
        if name:
            novels = novels.filter(name__icontains=name)

        # 获取页码 没有默认为1
        p = int(request.GET.get('p', 1))
        paginator = Paginator(novels, 10)
        page_pbj = paginator.page(p)

        context_data = self.get_pagination_data(paginator, page_pbj)
        context = {
            'categories': NovelCategory.objects.all(),
            'novels': page_pbj.object_list,
            'paginator': paginator,
            'page_obj': page_pbj,

            'start': start or '',
            'end': end or '',
            'name': name or '',
            'category_id': category_id or '',

            'url_query': '&' + parse.urlencode({  # 字典转化为查询字符串
                'start': start or '',
                'end': end or '',
                'name': name or '',
                'category_id': category_id or '',
            })
        }
        context.update(context_data)
        return render(request, 'cms/novel_list.html', context=context)

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        num_pages = paginator.num_pages

        left_has_more = False
        right_has_more = False

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
        else:
            left_has_more = True
            left_pages = range(current_page - around_count, current_page)

        if current_page >= num_pages - around_count - 1:
            right_pages = range(current_page + 1, num_pages + 1)
        else:
            right_has_more = True
            right_pages = range(current_page + 1, current_page + around_count + 1)

        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'num_pages': num_pages
        }

# 编辑小说  已登录 是作者
@method_decorator(permission_required(perm='novel.change_novel',login_url='/'), name='dispatch')
class EditNovel(View):
    def get(self,request):
        novel_id = request.GET.get('novel_id')
        context = {}
        try:
            novel = Novel.objects.get(pk=novel_id)
            context['novel'] = novel
        except:
            return redirect('cms/index')
        context['categories'] = NovelCategory.objects.all()
        return render(request, 'cms/edit_novel.html', context=context)
    def post(self,request):
        form = NovelForm(request.POST)
        if form.is_valid():
            novel = form.save(commit=False)
            category_id = form.cleaned_data.get('category')
            novel.category = NovelCategory.objects.get(pk=category_id)
            novel.author = self.request.user
            novel.save()
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())

# 选择小说
@method_decorator(permission_required(perm='novel.change_novel',login_url='/'), name='dispatch')
def choose_novel(request):
    operate = request.GET.get('operate')
    operate = int(operate)
    if operate == 1:
        header_text = '写小说'
        btn_text = '更新小说'
        to_url = reverse('cms:write_chapter')
    elif operate == 2:
        header_text = '查看章节'
        btn_text = '查看章节'
        to_url = reverse('cms:chapter_list')
    else:
        header_text = '查看章节'
        btn_text = '查看章节'
        to_url = reverse('cms:chapter_list')

    novels = Novel.objects.filter(author=request.user)

    context = {
        'novels':novels,
        'header_text': header_text,
        'btn_text': btn_text,
        'to_url': to_url,
    }
    return render(request,'cms/choose_novel.html', context=context)

# 查看章节
@method_decorator(permission_required(perm='novel.change_novelchapter',login_url='/'), name='dispatch')
class ChapterList(View):
    def get(self,request):
        novel_id = request.GET.get('novel_id')
        novel = Novel.objects.get(pk=novel_id)
        chapters = novel.chapters.all()
        # 过滤条件
        start = request.GET.get('start')
        end = request.GET.get('end')
        title = request.GET.get('title')
        # 时间过滤
        if start:
            start_date = datetime.strptime(start,'%Y/%m/%d')
        else:
            start_date = datetime(year=2019,month=11,day=1)
        if end:
            end_date = datetime.strptime(end,'%Y/%m/%d')
        else:
            end_date = datetime.today()
        start_date = make_aware(start_date)
        end_date = make_aware(end_date)
        chapters = chapters.filter(pub_date__range=(start_date,end_date))
        # 标题过滤
        if title:
            chapters = chapters.filter(title__icontains=title)

        # 获取页码 没有默认为1
        p = int(request.GET.get('p',1))
        paginator = Paginator(chapters,10)
        page_pbj = paginator.page(p)

        context_data = self.get_pagination_data(paginator,page_pbj)
        context = {
            'novel': novel,
            'chapters': page_pbj.object_list,     # 在当前这页上的对象列表
            'paginator': paginator,
            'page_obj': page_pbj,

            'start': start or '',
            'end': end or '',
            'title': title or '',

            'url_query': '&' + parse.urlencode({        # 字典转化为查询字符串
                'novel_id': novel_id,
                'start': start or '',
                'end': end or '',
                'title': title or '',
            })
        }
        context.update(context_data)
        return render(request, 'cms/chapter_list.html', context=context)


    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        num_pages = paginator.num_pages

        left_has_more = False
        right_has_more = False

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
        else:
            left_has_more = True
            left_pages = range(current_page - around_count, current_page)

        if current_page >= num_pages - around_count - 1:
            right_pages = range(current_page + 1, num_pages + 1)
        else:
            right_has_more = True
            right_pages = range(current_page + 1, current_page + around_count + 1)

        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'num_pages': num_pages
        }

# 编辑章节
@method_decorator(permission_required(perm='novel.change_novelchapter',login_url='/'), name='dispatch')
class EditChapter(View):
    def get(self,request):
        chapter_id = request.GET.get('chapter_id')
        chapter = NovelChapter.objects.select_related('novel').get(pk=chapter_id)
        context = {
            'chapter': chapter,
        }
        return render(request, 'cms/edit_chapter.html', context=context)

    def post(self,request):
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter_id = form.cleaned_data.get('chapter_id')
            chapter = NovelChapter.objects.get(pk=chapter_id)
            chapter.title = form.cleaned_data.get('title')
            chapter.content = form.cleaned_data.get('content')
            chapter.save(update_fields=['title','content'])
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())

# 删除章节
@require_POST
@permission_required(perm='novel.change_novelchapter',login_url='/')
def delete_chapter(request):
    chapter_id = request.POST.get('chapter_id')
    chapter = NovelChapter.objects.get(pk=chapter_id)
    chapter.delete()
    return restful.ok()

# 上传图片
@require_POST
@xs_login_required
def upload_file(request):
    file = request.FILES.get('file')
    time = datetime.now()
    extension = file.name.split('.')[-1]
    dir = time.strftime('%Y\%m\%d')
    name = time.strftime('%H%M%S%f') + '.' + extension
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT,dir)):
        os.makedirs(os.path.join(settings.MEDIA_ROOT,dir))
    with open(os.path.join(settings.MEDIA_ROOT,dir,name),'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    # 拼接url     127.0.0.1:8000/media/1.jpg
    url = request.build_absolute_uri(settings.MEDIA_URL + os.path.join(dir,name))
    return restful.result(data={'url':url})

# 设置推荐
@require_POST
@permission_required(perm='novel.recommand_novel')
def set_recommend(request):
    novel_id = request.POST.get('novel_id')
    try:
        novel = Novel.objects.get(pk=novel_id)
        if novel.is_recommend:
            return restful.params_error(message='该小说已推荐，请勿重复设置！')
        else:
            novel.is_recommend = True
            novel.save()
            return restful.ok()
    except:
        return restful.params_error(message='参数错误，小说不存在！')

# 取消推荐
@require_POST
@permission_required(perm='novel.recommand_novel')
def cancel_recommend(request):
    novel_id = request.POST.get('novel_id')
    try:
        novel = Novel.objects.get(pk=novel_id)
        if novel.is_recommend:
            novel.is_recommend = False
            novel.save()
            return restful.ok()
        else:
            return restful.params_error(message='该小说未推荐，请勿重复设置！')
    except:
        return restful.params_error(message='参数错误，该小说不存在！')
