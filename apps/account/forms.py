from django import forms
from apps.novel.models import Novel,NovelChapter
from apps.forms import FormMixin
from django.template.defaultfilters import escape
from django.core import validators
import bleach
from bleach.sanitizer import ALLOWED_TAGS,ALLOWED_ATTRIBUTES


class NovelForm(forms.ModelForm, FormMixin):
    category = forms.IntegerField()
    tag = forms.IntegerField()
    class Meta:
        model = Novel
        fields = ['name','profile','price','cover_url']
        exclude = ['tag','category','author','chapters_num','words_num','pub_date','views']
    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        profile = bleach.clean(profile, tags=['p','br'])
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