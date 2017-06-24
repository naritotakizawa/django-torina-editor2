"""エディタで使用するフィルタ・タグ."""
from django import template
from dteditor2 import utils

register = template.Library()


@register.simple_tag
def change_bytes(size):
    """ファイルサイズを見やすい形に変換する."""
    human_size = utils.change_bytes(size)
    return human_size
