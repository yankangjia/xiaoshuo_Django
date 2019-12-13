from utils import restful
from django.shortcuts import redirect, reverse
from functools import wraps
from django.http import Http404
from django.core.exceptions import PermissionDenied

def xs_permission_required(perm=None, login_url='/', need_login=True):
    def check_perms(user):
        if perm is None:
            return True
        elif isinstance(perm, str):
            perms = (perm,)
        else:
            perms = perm
        # First check if the user has the permission (even anon users)
        if user.has_perms(perms):
            return True
        else:
            return False
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.is_ajax():
                if need_login:
                    if not request.user.is_authenticated:
                        return restful.unauth(message='请先登录！')
                if check_perms(request.user):
                    return func(request,*args,**kwargs)
                else:
                    return restful.unauth(message='您没有改权限！')
            else:
                if need_login:
                    if not request.user.is_authenticated:
                        # 如果没有登录
                        return redirect(login_url)
                if check_perms(request.user):
                    return func(request, *args, **kwargs)
                else:
                    return redirect('/')
        return wrapper
    return decorator

def xs_login_required(func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return func(request,*args,**kwargs)
        else:
            if request.is_ajax():
                return restful.unauth(message="请先登录！")
            else:
                previous = request.META['HTTP_REFERER']
                current = request.path
                current_query_string = request.META['QUERY_STRING']
                redirect_url = '%s?next=%s?%s' % (previous,current,current_query_string)
                return redirect(redirect_url)
    return wrapper

def xs_superuser_required(viewfunc):
    @wraps(viewfunc)
    def decorator(request,*args,**kwargs):
        if request.user.is_superuser:
            return viewfunc(request,*args,**kwargs)
        else:
            raise Http404()
    return decorator