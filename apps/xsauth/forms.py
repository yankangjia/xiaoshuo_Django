from django import forms
from apps.forms import FormMixin
from django.core import validators
from .models import User
from django.core.cache import cache


class LoginForm(forms.Form,FormMixin):
    telephone = forms.CharField(max_length=11,min_length=11,validators=[validators.RegexValidator(r'1[345678]\d{9}',message="请输入正确的手机号")],error_messages={
        "required":"请输入手机号码"
    })
    password = forms.CharField(max_length=16,min_length=6,error_messages={
        'max_length': '密码最多不能超过16位',
        'min_length': '密码最少不能少于6位',
        'required': '请输入密码',
    })
    remember = forms.IntegerField(required=False)

class RegisterForm(forms.Form,FormMixin):
    telephone = forms.CharField(max_length=11, min_length=11,
        validators=[validators.RegexValidator(r'1[345678]\d{9}', message="请输入正确的手机号")],
        error_messages={
            "required": "请输入手机号码"
        })
    username = forms.CharField(max_length=20,min_length=2,error_messages={
        'max_length': '用户名不能超过20位','min_length': '用户名不能少于2位','required': '请输入用户名'})
    password1 = forms.CharField(max_length=16, min_length=6, error_messages={
        'max_length': '密码最多不能超过16位','min_length': '密码最少不能少于6位','required': '请输入密码'})
    password2 = forms.CharField(max_length=16, min_length=6, error_messages={
        'max_length': '密码最多不能超过16位','min_length': '密码最少不能少于6位','required': '请输入密码'})
    img_captcha = forms.CharField(max_length=4,min_length=4,error_messages={
        'max_length': '验证码位数不对','min_length': '验证码位数不对','required': '请输入验证码'})
    sms_captcha = forms.CharField(max_length=4,min_length=4,error_messages={
        'max_length': '验证码位数不对','min_length': '验证码位数不对','required': '请输入验证码'})

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        # 判断手机号是否已注册
        telephone = cleaned_data.get('telephone')
        exists = User.objects.filter(telephone=telephone).exists()
        if exists:
            raise forms.ValidationError('该手机号码已注册！')

        # 判断两次密码输入是否一致
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('两次密码输入不一致！')

        # 判断图形验证码输入是否正确
        img_captcha = cleaned_data.get('img_captcha')
        cache_img_captcha = cache.get(img_captcha.lower())
        if not cache_img_captcha or img_captcha.lower() != cache_img_captcha.lower():
            raise forms.ValidationError('图形验证码输入有误！')

        # 判断短信验证码输入是否正确
        sms_captcha = cleaned_data.get('sms_captcha')
        print(sms_captcha)
        cache_sms_captcha = cache.get(telephone)
        print(cache_sms_captcha)
        if not cache_sms_captcha or sms_captcha.lower() != cache_sms_captcha.lower():
            raise forms.ValidationError('短信验证码输入有误！')


        return cleaned_data

