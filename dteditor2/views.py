from django.shortcuts import render

from .utils import editor


def home(request):
    """/ アクセスで呼び出されるビュー."""
    editor.update(request)  # エディタの更新
    context = {
        'editor': editor,
    }
    return render(request, 'dteditor2/home.html', context)
