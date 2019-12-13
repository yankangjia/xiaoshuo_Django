from django.shortcuts import render
from .models import Novel, NovelChapter, NovelCategory, Banner, Advertisement, NovelTag, ExcellentWorks
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from urllib import parse
from utils import restful
from apps.xsauth.decorators import xs_login_required
import time
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.views.generic import View

# 首页
def index(request):
    all_category_name = settings.CATEGORY_NAME
    base_novels = Novel.objects.select_related('category', 'tag', 'author')
    cate_hot_novels = []
    # 分类排行  每两个为一组，获取每个组的热门图书
    for i in range(0,6):
        id1, id2 = i*2+1, i*2+2
        name1, name2 = all_category_name[id1-1][1], all_category_name[id2-1][1]
        novels = base_novels.filter(Q(category_id=id1)|Q(category_id=id2))[0:5]
        cate_hot_novels.append((name1,name2,novels))

    context = {
        'ads': Advertisement.objects.all()[0:4],
        'banners': Banner.objects.all(),
        'excellent_workses': ExcellentWorks.objects.all(),
        'all_category_name': all_category_name,
        'new_novels': base_novels,
        'recommend_novels': base_novels.filter(is_recommend=True),
        'cate_hot_novels': cate_hot_novels,
        'rank_novels': base_novels.order_by('-views'),
    }
    return render(request,'novel/index.html', context=context)

# 小说详情
def detail(request, novel_id):
    novel = Novel.objects.select_related('category', 'tag', 'author').get(pk=novel_id)
    category_name = settings.CATEGORY_NAME
    # 当前分类推荐
    recommend_novels = Novel.objects.select_related('category', 'tag', 'author').filter(Q(is_recommend=True)&Q(category=novel.category))[0:12]
    works_num = novel.author.novels.count()      # 作者作品数
    chapters = novel.chapters.defer('content').order_by('number')     # 目录
    context = {
        'category_name': category_name,
        'novel': novel,
        'recommend_novels': recommend_novels,
        'works_num': works_num,
        'chapters':chapters
    }
    return render(request,'novel/detail.html',context)

# 章节
def chapter_view(request, chapter_id):
    chapter = NovelChapter.objects.select_related('novel','novel__category','novel__author').get(pk=chapter_id)
    chapter.novel.viewed()  # 记录+1
    if request.user.is_authenticated:
        request.user.read.add(chapter.novel)    # 看过
    if request.user in list(chapter.novel.collectors.all()):
        collected = True
    else:
        collected = False
    context = {
        'chapter': chapter,
        'collected': collected,
        'category_en_name': settings.CATEGORY_NAME[chapter.novel.category_id-1][0],
        'category_name': settings.CATEGORY_NAME
    }
    base_chapters = NovelChapter.objects.filter(novel=chapter.novel)
    if chapter.number > 1:
        previous_id = base_chapters.filter(number=chapter.number-1).first().pk
        context['previous_id'] = previous_id
    if chapter.number < chapter.novel.chapters_num:
        next_id = base_chapters.filter(number=chapter.number+1).first().pk
        context['next_id'] = next_id
    return render(request,'novel/chapter.html',context=context)

# 每个分类首页
def index_category(request, category_name):
    # 获取中文名称
    category_cn_name = ''
    counter = 0
    for category in settings.CATEGORY_NAME:
        counter += 1
        if category[0] == category_name:
            category_cn_name = category[1]
            break
    if not category_cn_name:
        raise Http404()
    category = NovelCategory.objects.get(id=counter)
    tags = category.tags.all()
    novels = category.novels.select_related('category','tag','author')
    recommend_novels = novels.filter(is_recommend=True)
    rank_novels = novels.order_by('-views')
    new_novels = novels.all()
    context = {
        'tags': tags,
        'category_name': settings.CATEGORY_NAME,
        'category_en_name': category_name,
        'category_cn_name': category_cn_name,
        'category': category,
        'recommend_novels': recommend_novels,
        'rank_novels': rank_novels,
        'new_novels': new_novels
    }

    return render(request,'novel/index_category.html', context=context)

# 排行榜
class RankView(View):
    def get(self,request):
        category_id = int(request.GET.get('category_id',0) or 0)
        page = int(request.GET.get('page',1))
        base_novels = Novel.objects.select_related('category','tag', 'author')
        novels = base_novels
        if category_id:
            category = NovelCategory.objects.get(pk=category_id)
            novels = novels.filter(category=category)

        paginator = Paginator(novels, 12)
        page_obj = paginator.page(page)
        context_pagination = self.get_pagination_data(paginator, page_obj)

        context = {
            'paginator': paginator,
            'page_obj': page_obj,
            'novels': page_obj.object_list,
            'category_id': category_id,
            'categories': NovelCategory.objects.all(),
            'page_query': 'category_id=%d' % category_id,
            'recommend_novels': base_novels.filter(is_recommend=True)
        }
        context.update(context_pagination)
        return render(request,'novel/rank.html', context=context)

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

# 全部
class WholeView(View):
    def get(self,request):
        category_name = settings.CATEGORY_NAME
        page = int(request.GET.get('page',1))
        category_id = int(request.GET.get('category_id',0)) or 0
        is_free = int(request.GET.get('is_free',0)) or 0            # 1:免费 2:付费
        is_complete = int(request.GET.get('is_complete',0)) or 0    # 1:完本 2:未完本
        sort = int(request.GET.get('sort',1)) or 1                  # 0:最新 1:最热
        base_novels = Novel.objects.select_related('category', 'tag', 'author')
        novels = base_novels
        if category_id:
            category = NovelCategory.objects.get(pk=category_id)
            novels = novels.filter(category=category)
        if is_free == 1:
            novels = novels.filter(price=0)
        elif is_free == 2:
            novels = novels.filter(price__gt=0)
        if is_complete == 1:
            novels = novels.filter(is_complete=True)
        elif is_complete == 2:
            novels = novels.filter(is_complete=False)
        if sort == 1:
            novels = novels.order_by('-pub_date')
        elif sort == 2:
            novels = novels.order_by('-views')

        params = {
            'category_id': category_id,
            'is_free': is_free,
            'is_complete': is_complete,
            'sort': sort,
        }
        query_strings = {}
        for key,value in params.items():
            new_params = params.copy()
            del new_params[key]
            query_strings[key + '_query'] = parse.urlencode(new_params)

        paginator = Paginator(novels,12)
        page_obj = paginator.page(page)
        context_pagination = self.get_pagination_data(paginator,page_obj)
        context = {
            'paginator': paginator,
            'page_obj': page_obj,
            'category_name': category_name,
            'novels': page_obj.object_list,
            'recommend_novels': base_novels.filter(is_recommend=True),
            'page_query': parse.urlencode(params)
        }
        context.update(context_pagination)
        context.update(params)
        context.update(query_strings)
        return render(request,'novel/whole.html', context=context)

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

# 搜索
def search(request):
    novels = Novel.objects.all()
    context = {
        'novels': novels
    }
    return render(request,'novel/search.html',context=context)

# 收藏图书 ajax
@require_POST
@xs_login_required
def collect_novel(request):
    novel_id = request.POST.get('novel_id')
    novel = Novel.objects.get(pk=novel_id)
    request.user.collect.add(novel)
    return restful.ok()

# 取消收藏
@require_POST
@xs_login_required
def cancel_collect(request):
    novel_id = request.POST.get('novel_id')
    novel = Novel.objects.get(pk=novel_id)
    request.user.collect.remove(novel)
    return restful.ok()


# def novel_set(request):
    # novels = Novel.objects.all()
    # for novel in novels:
    #     novel.chapters_num = novel.chapters.count()
    #     count = 0
    #     for chapter in novel.chapters.all():
    #         count += chapter.words_num
    #     novel.words_num = count
    #     novel.save()

    # Novel.objects.filter(is_recommend=False).update(is_recommend=True)
    # return HttpResponse('success')
