from django.shortcuts import render,reverse,redirect
from django.conf import settings
import os
from utils import restful
from django.views.generic import View
from apps.novel.models import Novel, NovelCategory,NovelChapter,NovelTag
from .forms import NovelForm,ChapterForm
from django.db.models import F
from django.utils.timezone import make_aware
from datetime import datetime
from urllib import parse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from apps.xsauth.decorators import xs_permission_required,xs_login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Permission,ContentType,Group


# 小说列表
@method_decorator(permission_required(perm='novel.change_novel'),name='dispatch')
class NovelList(View):
    def get(self,request):
        novels = request.user.novels.prefetch_related('category')
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
            start_date = datetime.strptime(start,'%Y/%m/%d')
        else:
            start_date = datetime(year=2019,month=11,day=1)
        if end:
            end_date = datetime.strptime(end,'%Y/%m/%d')
        else:
            end_date = datetime.today()
        start_date = make_aware(start_date)
        end_date = make_aware(end_date)
        novels = novels.filter(pub_date__range=(start_date,end_date))
        # 标题过滤
        if name:
            novels = novels.filter(name__icontains=name)

        # 获取页码 没有默认为1
        p = int(request.GET.get('p',1))
        paginator = Paginator(novels,10)
        page_pbj = paginator.page(p)

        context_data = self.get_pagination_data(paginator,page_pbj)
        context = {
            'categories': NovelCategory.objects.all(),
            'novels': page_pbj.object_list,
            'paginator': paginator,
            'page_obj': page_pbj,

            'start': start or '',
            'end': end or '',
            'name': name or '',
            'category_id': category_id or '',

            'url_query': '&' + parse.urlencode({        # 字典转化为查询字符串
                'start': start or '',
                'end': end or '',
                'name': name or '',
                'category_id': category_id or '',
            })
        }
        context.update(context_data)
        return render(request, 'account/novel_list.html', context=context)

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

# 发布小说
@method_decorator(permission_required(perm='novel.add_novel'),name='dispatch')
class PubNovel(View):
    def get(self,request):
        return render(request, 'account/pub_novel.html')
    def post(self,request):
        form = NovelForm(request.POST)
        if form.is_valid():
            novel = form.save(commit=False)
            category_id = form.cleaned_data.get('category')
            tag_id = form.cleaned_data.get('tag')
            novel.category = NovelCategory.objects.get(pk=category_id)
            novel.tag = NovelTag.objects.get(pk=tag_id)
            novel.author = self.request.user
            novel.save()
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())

# 编辑小说
@method_decorator(permission_required(perm='novel.change_novel'),name='dispatch')
class EditNovel(View):
    def get(self,request):
        novel_id = request.GET.get('novel_id')
        context = {}
        try:
            novel = Novel.objects.get(pk=novel_id)
            context['novel'] = novel
        except:
            return redirect('account:index')
        categories = NovelCategory.objects.all()
        context['categories'] = categories
        return render(request, 'account/pub_novel.html', context=context)

    def post(self,request):
        novel_id = request.POST.get('novel_id')
        form = NovelForm(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data.get('category')
            novel = Novel.objects.get(pk=novel_id)
            if not novel.author == self.request.user:
                return restful.unauth(message='这不是您的文章')
            novel.name = form.cleaned_data.get('name')
            novel.category = NovelCategory.objects.get(pk=category_id)
            novel.profile = form.cleaned_data.get('profile')
            novel.price = form.cleaned_data.get('price')
            novel.cover_url = form.cleaned_data.get('cover_url')
            novel.save()
            return restful.ok()
        else:
            return restful.params_error(form.get_errors())

# 删除小说
@permission_required(perm='novel.delete_novel')
def delete_novel(request):
    novel_id = request.POST.get('novel_id')
    novel = Novel.objects.get(pk=novel_id)
    novel.delete()
    return restful.ok()

# 更新小说
@method_decorator(permission_required(perm='novel.add_novelchapter'),name='dispatch')
class WriteChapter(View):
    def get(self,request):
        novel_id = request.GET.get('novel_id')
        novel = Novel.objects.get(pk=novel_id)
        context = {
            'novel': novel,
        }
        return render(request, 'account/write_chapter.html', context=context)

    def post(self,request):
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            novel_id = form.cleaned_data.get('novel_id')
            # 获取小说
            novel = Novel.objects.get(pk=novel_id)
            if self.request.user.uid != novel.author.uid:
                return restful.unauth(message='您不是原作者，无法更新小说')
            chapter.novel = novel
            chapter.save()

            return restful.ok()
        else:
            return restful.params_error(form.get_errors())

# 获取分类和标签
@permission_required(perm='novel.add_novelchapter')
def get_cate_list(request):
    categories = NovelCategory.objects.prefetch_related('tags')
    tags_list = []
    for category in categories:
        tags_queryset = category.tags.all()
        tags = []
        for tag in tags_queryset:
            tags.append(model_to_dict(tag))
        tags_list.append(tags)
    cate_list = []
    for i in range(categories.count()):
        tags_dist = {
            'tags': tags_list[i]
        }
        category = {**model_to_dict(categories[i]), **tags_dist}
        cate_list.append(category)
    data = {
        'cate_list': cate_list
    }
    return restful.result(data=data)

# 编辑章节
@method_decorator(permission_required(perm='novel.change_novelchapter'),name='dispatch')
class EditChapter(View):
    def get(self,request):
        chapter_id = request.GET.get('chapter_id')
        chapter = NovelChapter.objects.select_related('novel').get(pk=chapter_id)
        context = {
            'chapter': chapter,
            'novel': chapter.novel,
        }
        return render(request, 'account/write_chapter.html', context=context)

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
@permission_required(perm='novel.delete_novelchapter')
def delete_chapter(request):
    chapter_id = request.POST.get('chapter_id')
    chapter = NovelChapter.objects.get(pk=chapter_id)
    chapter.delete()
    return restful.ok()

# 选择小说
@permission_required(perm='novel.change_novel')
def choose_novel(request):
    operate = request.GET.get('operate')
    operate = int(operate)
    novels = request.user.novels.prefetch_related('category').order_by('is_complete','-pub_date')
    context = {
        'operate': operate,
        'novels':novels,
    }
    return render(request, 'account/choose_novel.html', context=context)

# 查看章节
@method_decorator(permission_required(perm='novel.change_novelchapter'),name='dispatch')
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
        return render(request, 'account/chapter_list.html', context=context)


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

# 上传图片
@require_POST
@xs_login_required
def upload_file(request):
    file = request.FILES.get('file')
    name = file.name
    with open(os.path.join(settings.MEDIA_ROOT,name),'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    # 拼接url     127.0.0.1:8000/media/1.jpg
    url = request.build_absolute_uri(settings.MEDIA_URL + name)
    return restful.result(data={'url':url})


@require_POST
@permission_required(perm='novel.add_novel')
def set_finish(request):
    novel_id = request.POST.get('novel_id')
    try:
        novel = Novel.objects.get(pk=novel_id)
        if novel.is_complete:
            return restful.params_error(message='该小说已完结，请勿重复设置！')
        else:
            novel.is_complete = True
            novel.save()
            return restful.ok()
    except:
        return restful.params_error(message='参数错误，小说不存在！')

@require_POST
@permission_required(perm='novel.add_novel')
def set_serialize(request):
    novel_id = request.POST.get('novel_id')
    try:
        novel = Novel.objects.get(pk=novel_id)
        if novel.is_complete:
            novel.is_complete = False
            novel.save()
            return restful.ok()
        else:
            return restful.ok()
    except:
        return restful.params_error(message='参数错误，小说不存在！')