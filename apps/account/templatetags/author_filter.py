from django import template
from datetime import datetime
from django.utils.timezone import now as now_func,localtime   # 获取当前的清醒的时间

register = template.Library()

@register.filter(name='time_since')
def time_since(value):
    """
    time距离现在的时间间隔
    1. 如果时间间隔小于1分钟以内，那么就显示“刚刚”
    2. 如果是大于1分钟小于1小时，那么就显示“xx分钟前”
    3. 如果是大于1小时小于24小时，那么就显示“xx小时前”
    4. 如果是大于24小时小于30天以内，那么就显示“xx天前”
    5. 否则就是显示具体的时间 2017/10/20 16:15
    """
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
            return value.strftime("%Y/%m/%d %H:%M:%s")
    else:
        return value

# register.filter("time_since",time_since)

@register.filter
def time_format(value):
    if not isinstance(value, datetime):
        return value

    return localtime(value).strftime('%Y/%m/%d %H:%M:%S')

@register.filter
def get_module(value):
    return value.split('/')[1]

@register.filter
def complete_to_string(value):
    if value:
        return '完本'
    else:
        return '连载'

@register.filter
def recommend_to_string(value):
    if value:
        return '是'
    else:
        return '否'