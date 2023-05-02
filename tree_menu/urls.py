from django.urls import path
from tree_menu.views import IndexPageView

app_name = 'tree_menu'

urlpatterns = [
    path('tree_menu/', IndexPageView.as_view(), name='index')
]
