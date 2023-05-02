from django.db import models


class Menu(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name='Menu title')
    slug = models.SlugField(max_length=255, verbose_name="Menu slug")

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, verbose_name='MenuItem title')
    slug = models.SlugField(max_length=255, verbose_name="MenuItem slug")
    menu = models.ForeignKey(Menu, blank=True, related_name='items', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='childrens', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'MenuItem'
        verbose_name_plural = 'MenuItems'

    def __str__(self):
        return self.title
