from django.shortcuts import render,reverse,redirect
from utils import restful
from apps.novel.models import Banner,Advertisement,ExcellentWorks
from apps.novel.serializers import BannerSerializer
from .forms import AddBannerForm,EditBannerForm,AddAdvertisementForm,EditAdvertisementForm,ExcellentWorksForm
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from apps.xsauth.decorators import xs_permission_required
from django.views.decorators.http import require_POST


# 轮播图管理页面
@permission_required(perm='novel.change_banner',login_url='/')
def banners_view(request):
    return render(request, 'cms/banners.html')

# 轮播图列表
# @require_POST
@permission_required(perm='novel.change_banner')
def banner_list(request):
    banners = Banner.objects.all()
    serializer = BannerSerializer(banners,many=True)
    return restful.result(data=serializer.data)

# 添加轮播图
@require_POST
@permission_required(perm='novel.change_banner')
def add_banner(request):
    form = AddBannerForm(request.POST)
    if form.is_valid():
        priority = form.cleaned_data.get('priority')
        link_to = form.cleaned_data.get('link_to')
        image_url = form.cleaned_data.get('image_url')
        banner = Banner.objects.create(priority=priority,link_to=link_to,image_url=image_url)
        return restful.result(data={'banner_id':banner.id})
    else:
        return restful.params_error(form.get_errors())

# 删除轮播图
@require_POST
@permission_required(perm='novel.delete_banner')
def delete_banner(request):
    banner_id = request.POST.get('banner_id')
    Banner.objects.filter(pk=banner_id).delete()
    return restful.ok()

# 编辑轮播图
@require_POST
@permission_required(perm='novel.change_banner')
def edit_banner(request):
    form = EditBannerForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        priority = form.cleaned_data.get('priority')
        link_to = form.cleaned_data.get('link_to')
        image_url = form.cleaned_data.get('image_url')
        Banner.objects.filter(pk=pk).update(priority=priority,link_to=link_to,image_url=image_url)
        return restful.ok()
    else:
        return restful.params_error(form.get_errors())

# 广告设置
@permission_required(perm='novel.change_advertisement',login_url='/')
def ad_set(request):
    ads = Advertisement.objects.all()
    context = {
        'ads':ads
    }
    return  render(request,'cms/ad_set.html',context=context)

@require_POST
@permission_required(perm='novel.add_advertisement')
def ad_add(request):
    form = AddAdvertisementForm(request.POST)
    if form.is_valid():
        ad = form.save()
        data = {
            'ad': model_to_dict(ad)
        }
        return restful.result(data=data)
    else:
        return restful.params_error(message=form.get_errors())

@require_POST
@permission_required(perm='novel.change_advertisement')
def ad_edit(request):
    form = EditAdvertisementForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data.get('id')
        image_url = form.cleaned_data.get('image_url')
        link_to = form.cleaned_data.get('link_to')
        hint = form.cleaned_data.get('hint')
        ad = Advertisement.objects.get(pk=id)
        ad.image_url = image_url
        ad.link_to=link_to
        ad.hint=hint
        ad.save()
        data = {
            'ad': model_to_dict(ad)
        }
        return restful.result(data=data)
    else:
        return restful.params_error(message=form.get_errors())

@permission_required(perm='novel.add_advertisement')
def get_ads(request):
    ads = Advertisement.objects.values()
    data = {
        'ads': list(ads)
    }
    return restful.result(data=data)

# 优秀作品展示
@permission_required(perm='novel.change_excellentworks')
def excellent_works(request):
    excellent_workses = ExcellentWorks.objects.all()
    context = {
        'excellent_workses': excellent_workses,
        'range4': range(4)
    }
    return render(request,'cms/excellent_works.html',context=context)

# 编辑优秀作品
@require_POST
@permission_required(perm='novel.change_excellentworks')
def edit_excellent_works(request):
    form = ExcellentWorksForm(request.POST)
    if form.is_valid():
        id = form.cleaned_data.get('id')
        title = form.cleaned_data.get('title')
        link_to = form.cleaned_data.get('link_to')
        location = form.cleaned_data.get('location')
        if id:
            try:
                excellent_works = ExcellentWorks.objects.get(location=location)
                excellent_works.title = title
                excellent_works.link_to = link_to
                excellent_works.save()
                return restful.ok()
            except:
                return restful.params_error(message='参数错误')
        else:
            ExcellentWorks.objects.create(title=title, link_to=link_to, location=location)
            return restful.ok()
    else:
        return restful.params_error(form.get_errors())