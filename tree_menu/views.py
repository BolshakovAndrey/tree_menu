from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

from tree_menu.models import Menu


class IndexPageView(TemplateView):
    """
    Index page view that displays the tree menu.
    """
    template_name = "tree_menu/index.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Get the context data for the view.

        :return: context data dictionary
        """
        context = super().get_context_data(**kwargs)
        context['menu'] = Menu.objects.filter(slug='main_menu').first()
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Handle the GET request for the index page.

        :param request: HttpRequest object
        :return: HttpResponse object
        """
        response = super().get(request, *args, **kwargs)

        # Check the number of database queries executed for debugging purposes
        print("Number of database queries: ", len(connection.queries))

        return response
