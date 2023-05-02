from django.db import connection
from django.views.generic import TemplateView

from tree_menu.models import Menu


class IndexPageView(TemplateView):
    template_name = "tree_menu/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = Menu.objects.filter(slug='main_menu').first()
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        #  Проверка количества запросов к БД
        print("Количества запросов к БД: ", len(connection.queries))
        return response
