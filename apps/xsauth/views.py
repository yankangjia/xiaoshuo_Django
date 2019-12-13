from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from .forms import LoginForm,RegisterForm
from utils import restful
from django.shortcuts import render,redirect,reverse
from io import BytesIO
from utils.captcha.xfzcaptcha import Captcha
from django.http import HttpResponse
from utils.smssend import send
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()

@require_POST
def login_view(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        password = form.cleaned_data.get('password')
        remember = form.cleaned_data.get('remember')

        # 判断用户是否存在
        user = authenticate(request,telephone=telephone,password=password)
        if user:
            if user.is_active:
                login(request,user)
                if remember:
                    # 使用默认过期时间，默认为两周
                    request.session.set_expiry(None)
                else:
                    # 浏览器关闭时过期
                    request.session.set_expiry(0)
                return restful.ok()
            else:
                return restful.unauth(message="您的账号被冻结了")
        else:
            return restful.params_error(message='账号或密码错误')
    else:
        errors = form.get_errors()
        return restful.unauth(message=errors)

def logout_view(request):
    logout(request)     # 此操作会清除session和cookie
    return redirect(reverse('index'))

# 图片验证码
def img_captcha(request):
    text,image = Captcha.gene_code()
    # BytesIO：相当于一个管道，用来存储图片的流数据
    out = BytesIO()
    # 调用image的save方法，将这个image对象保存到BytesIO中
    image.save(out,'png')
    # 将BytesIO的文件指针移动到最开始的位置
    out.seek(0)

    response = HttpResponse()

    response['Content-type'] = 'image/png'
    response.write(out.read())
    response['Content-length'] = out.tell()
    cache.set(text.lower(),text.lower(),5*60)

    return response

# 短信验证码
def sms_captcha(request):
    telephone = request.GET.get('telephone')
    code = Captcha.gene_text()
    cache.set(telephone,code,5*60)
    result = send(telephone,code)
    print("短信验证码：",code)
    if result:
        return restful.result(data={'code':code})
    else:
        return restful.params_error(message="短信验证码发送失败！")

@require_POST
def register_view(request):
    form = RegisterForm(request.POST)
    if form.is_valid():
        telephone = form.cleaned_data.get('telephone')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = User.objects.create_user(telephone=telephone,username=username,password=password)
        login(request,user)
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())