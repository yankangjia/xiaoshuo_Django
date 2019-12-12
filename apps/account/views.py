from django.shortcuts import render
from apps.novel.models import Novel
from django.contrib.auth.decorators import login_required
from apps.xsauth.decorators import xs_login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib.auth.models import Permission,ContentType,Group
from django.shortcuts import render,reverse,redirect
from django.contrib import messages


# 首页
@xs_login_required
def index(request):
    readed_novels = request.user.read.select_related('category','author')
    collected_novels = request.user.collect.select_related('category','author')
    my_works = request.user.novels.select_related('category','author')
    context = {
        'readed_novels': readed_novels,
        'collected_novels': collected_novels,
        'my_works': my_works
    }
    return render(request,'author/index.html',context=context)

# 最近阅读
@xs_login_required
def recently_read(request):
    novels = request.user.read.select_related('category','author')
    collect_novels = request.user.collect.filter(id__in=novels)
    context = {
        'novels': novels,
        'collect_novels': collect_novels
    }
    return render(request,'author/recently_read.html',context=context)

# 我的书架
@xs_login_required
def my_collect(request):
    collected_novels = request.user.collect.all()
    context = {
        'collected_novels': collected_novels,
    }
    return render(request,'author/my_collect.html',context=context)

# 成为作家
@method_decorator(xs_login_required,name='dispatch')
class BecomeWriter(View):
    def get(self,request):
        if request.user.is_author:
            return redirect(reverse('account:index'))
        else:
            return render(request,'author/become_writer.html')

    def post(self,request):
        user = request.user
        if user.is_author:
            messages.info(request,message='您已是作家')
            return redirect(reverse('account:become_writer'))
        else:
            group = Group.objects.get(name='作家')
            user.groups.add(group)
            pen_name = request.POST.get('pen_name')
            user.pen_name = pen_name
            user.is_author = True
            user.save()
            return redirect(reverse('account:index'))