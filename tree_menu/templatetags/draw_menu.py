from typing import Dict, Any, List

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context

from ..models import MenuItem

register = template.Library()


@register.inclusion_tag('tree_menu/tree_menu.html', takes_context=True)
def draw_menu(context: Context, menu: str) -> Dict[str, Any]:
    """
    Пользовательский тег шаблона для отображения древовидного меню
    :param context: запрос пользователя и другая информация
    :param menu: название меню
    :return: словарь, который будет использоваться для рендеринга шаблона tree_menu/tree_menu.html
    """

    try:
        # Получаем все пункты меню для данного menu
        items = MenuItem.objects.filter(menu__title=menu)
        items_values = items.values()

        # Получаем корневые пункты меню (без родителя)
        root_item = [item for item in items_values.filter(parent=None)]

        # Определяем ID выбранного пункта меню из параметров запроса
        selected_item_id = int(context['request'].GET[menu])
        selected_item = items.get(id=selected_item_id)

        # Получаем список ID выбранных пунктов меню
        selected_item_id_list = get_selected_item_id_list(selected_item, root_item, selected_item_id)

        # Добавляем дочерние элементы для каждого выбранного пункта меню
        for item in root_item:
            if item['id'] in selected_item_id_list:
                item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)

        result_dict = {'items': root_item}

    except (KeyError, ObjectDoesNotExist):
        # В случае ошибки возвращаем список пунктов меню без родительских элементов
        result_dict = {
            'items': [
                item for item in MenuItem.objects.filter(menu__title=menu, parent=None).values()
            ]
        }

    # Добавляем название меню и дополнительную строку запроса в словарь result_dict
    result_dict['menu'] = menu
    result_dict['other_querystring'] = build_querystring(context, menu)

    return result_dict


def build_querystring(context: Context, menu: str) -> str:
    """
    Cоздает строку запроса (querystring) на основе текущего контекста запроса
    :param context: текущий контекст
    :param menu: менюшка
    :return: собранную строку запроса
    """

    # Инициализация списка для хранения аргументов строки запроса
    querystring_args = []

    # Обход всех параметров текущего запроса
    for key in context['request'].GET:
        # Если ключ текущего параметра не совпадает с переданным параметром 'menu'
        if key != menu:
            # Добавление пары "ключ=значение" в список аргументов строки запроса
            querystring_args.append(key + '=' + context['request'].GET[key])

    # Соединение аргументов из списка в одну строку запроса, разделенную символом '&'
    querystring = ('&').join(querystring_args)

    # Возвращаю сформированные строки запроса
    return querystring


def get_child_items(items_values, current_item_id, selected_item_id_list):
    """
    Возвращает список дочерних элементов для заданного идентификатора элемента меню.

    :param items: список всех элементов меню
    :param current_item_id: идентификатор элемента меню, для которого нужно получить дочерние элементы
    :param selected_item_id_list: список идентификаторов выбранных элементов меню
    :return: список дочерних элементов для заданного идентификатора элемента меню
    """
    item_list = [item for item in items_values.filter(parent_id=current_item_id)]
    for item in item_list:
        if item['id'] in selected_item_id_list:
            item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)
    return item_list


def get_selected_item_id_list(parent: MenuItem, primary_item: List[MenuItem], selected_item_id: int) -> List[int]:
    """
    Возвращает список идентификаторов выбранных элементов меню, начиная от родительского элемента до текущего.

    :param parent: Родительский элемент меню
    :param primary_item: список корневых элементов меню
    :param selected_item_id: идентификатор выбранного элемента меню
    :return: список идентификаторов выбранных элементов меню
    """
    selected_item_id_list = []

    while parent:
        selected_item_id_list.append(parent.id)
        parent = parent.parent
    if not selected_item_id_list:
        for item in primary_item:
            if item.id == selected_item_id:
                selected_item_id_list.append(selected_item_id)
    return selected_item_id_list
