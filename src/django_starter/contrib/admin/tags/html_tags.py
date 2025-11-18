from typing import Optional
from django.utils.html import format_html


def image(url, alt_text='', width: Optional[int] = None, height: Optional[int] = None):
    size = ''
    if width:
        size += f'width={width} '
    if height:
        size += f'height={height} '
    return format_html('<img src="{}" {} alt="{}" />', url, size, alt_text)


def link(url, text, target='_self'):
    return format_html('<a href="{}" target="{}">{}</a>', url, target, text)


# todo 未测试
def script(src):
    return format_html('<script src="{}"></script>', src)


# todo 未测试
def style(css):
    return format_html('<style>{}</style>', css)


# todo 未测试
def div(content, class_name=None, id_name=None):
    class_attr = f' class="{class_name}"' if class_name else ''
    id_attr = f' id="{id_name}"' if id_name else ''
    return format_html('<div{}{}>{}</div>', class_attr, id_attr, content)


# todo 未测试
def span(content, class_name=None):
    class_attr = f' class="{class_name}"' if class_name else ''
    return format_html('<span{}>{}</span>', class_attr, content)


def input_tag(date_value,type='text',format_str='%Y-%m-%d', ):
    try:
        if type == 'date':
            date_value = date_value.strftime(format_str) if date_value else ''
        return format_html('<input type="{}" value="{}">',type, date_value)
    except (AttributeError, ValueError):
        return format_html('<span>-</span>')

def select_tag(value, options=None, default_text='-'):
    """格式化选择标签，使用 select 元素"""
    if not options or not isinstance(options, (list, dict)):
        return format_html('<span>{}</span>', value if value else default_text)

    option_html = ''
    if isinstance(options, list):
        for option in options:
            selected = ' selected' if option == value else ''
            option_html += f'<option value="{option}"{selected}>{option}</option>'
    elif isinstance(options, dict):
        for option_value, option_text in options.items():
            selected = ' selected' if option_value == value else ''
            option_html += f'<option value="{option_value}"{selected}>{option_text}</option>'
    
    from django.utils.safestring import mark_safe
    return mark_safe(f'<select >{option_html}</select>')


def colored_tag(text, color):
    """带颜色的标签"""
    if not text:
        return format_html('<span>-</span>')
    
    return format_html('<span style="color: {}; background: #f9f9f9; padding: 2px 6px; border-radius: 3px; display: inline-block;">{}</span>', color, text)