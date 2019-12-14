from django.db import models
from django.conf import settings
from shortuuidfield import ShortUUIDField
from django.template.defaultfilters import escape

class Novel(models.Model):
    id = ShortUUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    chapters_num = models.IntegerField(default=0)   # 章节数
    words_num = models.IntegerField(default=0)      # 字数
    profile = models.TextField()                    # 简介
    pub_date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    cover_url = models.URLField()           # 封面图
    is_recommend = models.BooleanField(default=False)   # 是否推荐
    views = models.IntegerField(default=0)              # 阅读数
    is_complete = models.BooleanField(default=False)    # 是否完本
    category = models.ForeignKey('NovelCategory', null=True, on_delete=models.SET_NULL, related_name='novels', related_query_name='novels')
    tag = models.ForeignKey('NovelTag', on_delete=models.DO_NOTHING)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='novels',related_query_name='novels')


    class Meta:
        db_table = 'novel'
        ordering = ['-pub_date']
        permissions = (
            ('recommend_novel','can recommend novel'),
        )

    # 阅读数+1
    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])


class NovelChapter(models.Model):
    id = ShortUUIDField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    number = models.IntegerField()          # 第几章
    words_num = models.IntegerField(default=0)      # 字数
    novel = models.ForeignKey('Novel', on_delete=models.CASCADE, related_name='chapters',related_query_name='chapters')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'novel_chapter'
        ordering = ['-pub_date']

    # 统计字数
    def set_words_num(self):
        content_filt = escape(self.content)  # 剔除<p>
        for punc in "~!@#$%^&*()_-+=<>?/,.，。？！￥……（）—《》：【】、·“”‘’:;{}[]|\'\"\n\\":
            if punc in content_filt:
                content_filt = content_filt.replace(punc, '')
        content_filt = content_filt.replace('&nbsp;','')
        content_filt = content_filt.replace(' ','')
        self.words_num = len(content_filt)

    def save(self,*args,**kwargs):
        if self.words_num == 0: # 添加
            self.set_words_num()
        else:                   # 更新
            self.novel.words_num -= self.words_num
            self.set_words_num()
        self.novel.words_num += self.words_num
        self.novel.chapters_num += 1
        self.novel.save(update_fields=['words_num','chapters_num'])
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.novel.words_num -= self.words_num
        self.novel.chapters_num -= 1
        self.novel.save(update_fields=['words_num','chapters_num'])
        super(NovelChapter, self).delete(using=None, keep_parents=False)

class NovelCategory(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        db_table = 'novel_category'

class NovelTag(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey('NovelCategory', null=True, on_delete=models.CASCADE,related_name='tags',related_query_name='tags')
    class Meta:
        db_table = 'novel_tag'

# 轮播图
class Banner(models.Model):
    priority = models.IntegerField()
    image_url = models.URLField()
    link_to = models.URLField()
    pub_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-priority']

# 广告
class Advertisement(models.Model):
    image_url = models.URLField()
    link_to = models.URLField()
    hint = models.CharField(max_length=200)
    pub_time = models.DateTimeField(auto_now_add=True)
    location = models.IntegerField()

# 优秀作品
class ExcellentWorks(models.Model):
    title = models.CharField(max_length=100)
    link_to = models.URLField()
    pub_time = models.DateTimeField(auto_now_add=True)
    location = models.IntegerField(unique=True)