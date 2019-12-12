from django.shortcuts import render,reverse,redirect
from utils import restful
from apps.novel.models import Novel, NovelCategory, NovelTag
from .forms import EditNovelCategoryForm
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from apps.xsauth.decorators import xs_permission_required
from django.views.decorators.http import require_POST
import os


# 分类列表
@permission_required(perm='novel.change_novelcategory',login_url='/')
def category_list(request):
    categories = NovelCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request,'cms/category_list.html',context=context)

# 添加分类
@require_POST
@permission_required(perm='novel.add_novelcategory')
def add_novel_category(request):
    name = request.POST.get('name')
    exists = NovelCategory.objects.filter(name=name).exists()
    if not exists:
        NovelCategory.objects.create(name=name)
        return restful.ok()
    else:
        return restful.params_error(message="该标签名已存在")

# 编辑分类
@require_POST
@permission_required(perm='novel.change_novelcategory')
def edit_novel_category(request):
    form = EditNovelCategoryForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data.get('id')
        name = form.cleaned_data.get('name')
        try:
            NovelCategory.objects.filter(id=id).update(name=name)
            return restful.ok()
        except:
            return restful.params_error(message="分类不存在！")
    else:
        return restful.params_error(message=form.get_errors())

# 删除分类
@require_POST
@permission_required(perm='novel.delete_novelcategory')
def delete_novel_category(request):
    id = request.POST.get('id')
    try:
        NovelCategory.objects.filter(id=id).delete()
        return restful.ok()
    except:
        return restful.params_error(message="该分类不存在")

# 标签列表
@permission_required(perm='novel.change_noveltag',login_url='/')
def tag_list(request):
    cate_tags = NovelCategory.objects.prefetch_related('tags')
    common_tags = NovelTag.objects.filter(category__isnull=True)
    context = {
        'cate_tags': cate_tags,
        'common_tags': common_tags,
    }
    return render(request,'cms/tag_list.html',context=context)

# 标签详情
@require_POST
@permission_required(perm='novel.change_noveltag',login_url='/')
def tag_detail(request):
    category_id = request.GET.get('category_id')
    context = {}
    if category_id:
        category = NovelCategory.objects.get(pk=category_id)
        # tags = NovelTag.objects.filter(category=category)
        context['category'] = category
    # else:
        # tags = NovelTag.objects.filter(category__isnull=True)
    # context['tags'] = tags
    return render(request, 'cms/tag_detail.html',context=context)

# 异步加载标签
@require_POST
@permission_required(perm='novel.change_noveltag')
def get_tags(request):
    category_id = request.GET.get('category_id')
    if category_id:
        category = NovelCategory.objects.get(pk=category_id)
        tags = NovelTag.objects.filter(category=category).values()
    else:
        tags = NovelTag.objects.filter(category__isnull=True).values()
    data = {
        'tags': list(tags)
    }
    return restful.result(data=data)

# 添加标签
@require_POST
@permission_required(perm='novel.add_noveltag')
def add_tag(request):
    category_id = request.POST.get('category_id')
    name = request.POST.get('name')
    if category_id:
        try:
            category = NovelCategory.objects.get(id=category_id)
            tag = NovelTag.objects.create(name=name,category=category)
        except:
            return restful.params_error(message='参数错误')
    else:
        tag = NovelTag.objects.create(name=name)
    data = {
        'tag': model_to_dict(tag)
    }
    return restful.result(data=data)

# 获取标签
@require_POST
@permission_required(perm='novel.change_noveltag')
def get_tag(request):
    tag_id = request.POST.get('tag_id')
    tag = NovelTag.objects.get(id=tag_id)
    return restful.result(data={'tag':model_to_dict(tag)})

# 删除标签
@require_POST
@permission_required(perm='novel.delete_noveltag')
def delete_tag(request):
    tag_id = request.POST.get('tag_id')
    try:
        tag = NovelTag.objects.get(pk=tag_id)
        tag.delete()
        return restful.ok()
    except:
        return restful.params_error(message='参数错误')

# 编辑标签
@require_POST
@permission_required(perm='novel.change_noveltag')
def edit_tag(request):
    tag_id = request.POST.get('tag_id')
    name = request.POST.get('name')
    try:
        tag = NovelTag.objects.get(pk=tag_id)
        tag.name = name
        tag.save()
        data = {
            'tag': model_to_dict(tag)
        }
        return restful.result(data=data)
    except:
        return restful.params_error(message='参数错误')