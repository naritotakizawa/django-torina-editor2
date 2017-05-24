from django.conf.urls import url
from . import views

app_name = 'dteditor2'
urlpatterns = [
    url(r'^$', views.home, name='home'),
]
