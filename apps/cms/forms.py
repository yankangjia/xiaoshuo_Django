from django import forms
from apps.novel.models import Novel,NovelChapter,Banner,Advertisement,ExcellentWorks
from apps.forms import FormMixin
from django.template.defaultfilters import escape
from django.core import validators
import bleach
from bleach.sanitizer import ALLOWED_TAGS,ALLOWED_ATTRIBUTES


class NovelForm(forms.ModelForm, FormMixin):
    category = forms.IntegerField()
    class Meta:
        model = Novel
        exclude = ['category','author','chapters_num','words_num','pub_date','views']
    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        profile = bleach.clean(profile, tags=['p'])
        return profile

class ChapterForm(forms.ModelForm, FormMixin):
    # shortuuid 22
    novel_id = forms.CharField(validators=[validators.RegexValidator('[0-9a-zA-z]{22}',message='参数错误')])

    class Meta:
        model = NovelChapter
        fields = ['title', 'content', 'number']

    def clean_context(self):
        content = self.cleaned_data.get('content')
        content = bleach.clean(content, tags=['p'])
        return content

    def clean(self):
        cleaned_data = super().clean()
        number = cleaned_data.get('number')
        novel_id = cleaned_data.get('novel_id')
        try:
            novel = Novel.objects.get(pk=novel_id)
        except:
            raise forms.ValidationError('当前小说不存在')
        # 判断章节数
        if number != novel.chapters_num + 1:
            raise forms.ValidationError('章数错误，请刷新网页重试！')

        return cleaned_data

# 编辑新闻分类
class EditNovelCategoryForm(forms.Form,FormMixin):
    id = forms.IntegerField(error_messages={
        'required': '参数错误！'
    })
    name = forms.CharField(max_length=100)

# 添加轮播图
class AddBannerForm(forms.ModelForm,FormMixin):
    class Meta:
        model = Banner
        fields = ['priority','link_to','image_url']

# 编辑轮播图
class EditBannerForm(forms.ModelForm,FormMixin):
    pk = forms.IntegerField()
    class Meta:
        model = Banner
        fields = ['priority','link_to','image_url']

# 添加广告
class AddAdvertisementForm(forms.ModelForm,FormMixin):

    class Meta:
        model = Advertisement
        exclude = ['pub_time','id']

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location > 4:
            raise forms.ValidationError(message='广告个数达到上限')
        return location

# 编辑广告
class EditAdvertisementForm(forms.ModelForm,FormMixin):
    id = forms.IntegerField()
    class Meta:
        model = Advertisement
        exclude = ['pub_time']

# 优秀作品
class ExcellentWorksForm(forms.ModelForm,FormMixin):
    id = forms.IntegerField(required=False)
    location = forms.IntegerField()
    class Meta:
        model = ExcellentWorks
        fields = ('title','link_to')

    def clean(self):
        cleaned_data = super().clean()
        id = cleaned_data.get('id')
        location = cleaned_data.get('location')
        if not id:      # 新建
            excellent_works = ExcellentWorks.objects.filter(location=location).first()
            if excellent_works:
                raise forms.ValidationError('参数错误：location')
            else:
                return cleaned_data
        return cleaned_data