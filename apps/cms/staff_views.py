from django.shortcuts import render,redirect,reverse
from django.views.generic import View
from django.contrib.auth.models import Group
from apps.xsauth.decorators import xs_superuser_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from utils import restful

User = get_user_model()

# 员工管理
@xs_superuser_required
def staffs_view(request):
    staffs = User.objects.filter(is_staff=True)
    context = {
        'staffs': staffs
    }
    return render(request,'cms/staffs.html',context=context)

# 添加员工
@method_decorator(xs_superuser_required,name='dispatch')
class AddStaff(View):
    def get(self,request):
        groups = Group.objects.filter(name__in=['广告','管理'])
        context = {
            'groups': groups
        }
        return render(request,'cms/add_staff.html',context)

    def post(self,request):
        telephone = request.POST.get('telephone')
        group_ids = request.POST.getlist('groups')
        groups = Group.objects.filter(pk__in=group_ids)

        user = User.objects.filter(telephone=telephone).first()
        if user:
            user.is_staff = True
            user.groups.set(groups)
            user.save()
            return redirect(reverse("cms:staffs"))
        else:
            messages.info(request, '手机号不存在!')
            return redirect(reverse("cms:add_staff"))

# 编辑员工
@method_decorator(xs_superuser_required,name='dispatch')
class EditStaff(View):
    def get(self, request, staff_id):
        user = User.objects.prefetch_related('groups').get(pk=staff_id)
        groups = Group.objects.all()
        if user.is_staff:
            context = {
                'staff': user,
                'groups': groups
            }
            return render(request,'cms/edit_staff.html',context=context)
        else:
            return redirect(reverse('cms:staffs'))
    def post(self, request, staff_id):
        # staff_id = request.POST.get('staff_id')
        group_ids = request.POST.getlist('groups')
        try:
            user = User.objects.get(pk=staff_id)
            if user.is_staff:
                groups = Group.objects.filter(id__in=group_ids)
                user.groups.set(groups)
                user.save()
        except:
            return redirect(reverse('cms:staffs'))
        else:
            return redirect(reverse('cms:staffs'))

# 移除员工
@require_POST
@xs_superuser_required
def delete_staff(request):
    staff_id = request.POST.get('staff_id')
    try:
        staff = User.objects.get(pk=staff_id)
        staff.groups.clear()
        staff.is_staff = False
        staff.save()
        return restful.ok()
    except:
        return restful.params_error(message='参数错误')