from django import template
from django.conf import settings
from django.template.defaultfilters import escape
from datetime import datetime
from django.utils.timezone import now as now_func,localtime   # 获取当前的清醒的时间
import time

register = template.Library()

@register.filter(name='time_since')
def time_since(value):
    if isinstance(value,datetime):
        now = now_func()
        time_stamp = (now - value).total_seconds()
        if time_stamp>=0 and time_stamp<60:
            return '刚刚'
        elif time_stamp>=60 and time_stamp<60*60:
            return '%s分钟前' % int(time_stamp/60)
        elif time_stamp>=60*60 and time_stamp<60*60*24:
            return '%s小时前' % int(time_stamp/(60*60))
        elif time_stamp>=60*60*24 and time_stamp<60*60*24*30:
            return '%s天前' % int(time_stamp/(60*60*24))
        elif time_stamp>=60*60*24*30:
            return value.strftime("%Y-%m-%d %H:%M:%s")
    else:
        return value

# 根据分类id获取分类名
@register.filter
def get_category_name(value,language):
    category_name = settings.CATEGORY_NAME
    if language == 'en':
        return category_name[value-1][0]
    elif language == 'ch':
        return category_name[value-1][1]
    else:
        return value

@register.filter
def words_num_filter(value):
    if isinstance(value,int):
        return round(value/10000, 2)
    else:
        return value

@register.filter
def strip(value):
    if isinstance(value,str):
        return value.strip()
    else:
        return value

@register.filter
def len_str(value):
    return len(value)

@register.filter
def recent_title(novel):
    # 获取小说最后一章的标题
    chapter = novel.chapters.order_by('-pub_date').first()
    if chapter:
        return chapter.title
    else:
        return ' '

@register.filter
def recent_date(novel):
    # 获取小说最后一章的发布时间
    chapter = novel.chapters.order_by('-pub_date').first()
    if chapter:
        return time_since(chapter.pub_date)
        # return chapter.pub_date.strftime('%Y-%m-%d %H:%M')
    else:
        return time_since(novel.pub_date)
        # return novel.pub_date.strftime('%Y-%m-%d %H:%M')

@register.filter
def find_keyword(value, keyword):
    header = '<span class="keyword">'
    len_header = len(header)
    footer = '</span>'
    len_footer = len(footer)
    len_key = len(keyword)
    len_value = len(value)
    value_l = value.lower()
    keyword_l = keyword.lower()

    index_list = []
    start_index = 0

    while start_index < len_value:
        index = value_l.find(keyword_l,start_index)
        if index != -1:
            index_list.append(index)
            start_index = index + len_key + 1
        else:
            break

    list_v = list(value)
    offset = 0
    for index in index_list:
        list_v.insert(index + offset,header)
        offset += 1
        list_v.insert(index + offset + len_key,footer)
        offset += 1
    new_value = ''.join(list_v)
    return new_value

# 判断是汉字
def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

# 判断是数字
def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False

# 判断是字母
def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

# 判断是其他字符
def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

# 切割字符串，超出部分加入省略号
@register.filter
def truncate(value, num):
    # 判断字符长度： 汉: 1, num: 0.5, upper: 0.75, lower: 0.5, other: 1, .:0.5
    def char_length(char):
        if is_chinese(char):
            return 1
        elif is_number(char):
            return 0.5
        elif char.isupper():
            return 0.75
        elif char.islower():
            return 0.5
        else:
            return 1
    if not isinstance(num, int):
        try:
            num = int(num)
        except:
            return value

    length, counter = 0, 0
    new_value = ''
    for char in value:
        length += char_length(char)
        if length <= num - 1.5:
            new_value += char
            counter += 1
        else:
            break

    # 判断不加省略号是否可以全部显示
    length = 0
    for char in value[counter:]:
        length += char_length(char)
    if length <= 1.5:
        for char in value[counter:]:
            new_value += char
    else:
        new_value += '...'
    return new_value