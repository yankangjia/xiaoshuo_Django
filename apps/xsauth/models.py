from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField
from django.db import models

class UserManager(BaseUserManager):
    def _create_user(self,telephone,username,password,**kwargs):
        if not telephone:
            raise ValueError('手机号码不能为空')
        if not username:
            raise ValueError('用户名不能为空')
        if not password:
            raise ValueError('密码不能为空')
        user = self.model(telephone=telephone,username=username,**kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_user(self,telephone,username,password,**kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(telephone=telephone,username=username,password=password,**kwargs)

    def create_superuser(self,telephone,username,password,**kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(telephone=telephone,username=username,password=password,**kwargs)

class User(AbstractBaseUser,PermissionsMixin):
    id = ShortUUIDField(primary_key=True)
    telephone = models.CharField(max_length=11,unique=True)
    username = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True,null=True)
    pen_name = models.CharField(max_length=100,null=True)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)      # 是否可用
    is_author = models.BooleanField(default=False)      # 是否是作者
    is_staff = models.BooleanField(default=False)      # 是否是员工
    collect = models.ManyToManyField('novel.Novel',related_name='collectors',related_query_name='collectors')
    read = models.ManyToManyField('novel.Novel',related_name='readers',related_query_name='readers')

    USERNAME_FIELD = 'telephone'
    # telephone，username，password
    REQUIRED_FIELDS = ['username','email']
    EMAIL_FIELD = 'email'

    objects = UserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username
