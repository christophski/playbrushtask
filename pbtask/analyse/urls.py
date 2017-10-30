from django.conf.urls import url
from analyse import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
