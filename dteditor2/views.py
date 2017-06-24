import base64

from django.http import Http404
from django.shortcuts import render
from django.views import generic

from .utils import editor


def home(request):
    """/ アクセスで呼び出されるビュー."""
    editor.update(request)  # エディタの更新
    context = {
        'editor': editor,
    }
    return render(request, 'dteditor2/home.html', context)


class ImgView(generic.TemplateView):
    """/img 画像ファイルクリックで呼び出されるビュー."""

    template_name = 'dteditor2/img.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        img_path = self.kwargs['path']
        try:
            src = open(img_path, 'rb').read()
        except FileNotFoundError:
            raise Http404('img Not Found')
        else:
            context['img_src'] = base64.b64encode(src)
            context['img_path'] = img_path
            return context
