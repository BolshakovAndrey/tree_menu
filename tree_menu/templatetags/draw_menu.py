from typing import Dict, Any, List

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context

from ..models import MenuItem

register = template.Library()


@register.inclusion_tag('tree_menu/tree_menu.html', takes_context=True)
def draw_menu(context: Context, menu: str) -> Dict[str, Any]:
    """
    Custom template tag for rendering a tree menu.
    :param context: User request and other information.
    :param menu: The menu name.
    :return: A dictionary that will be used to render the tree_menu/tree_menu.html template.
    """

    try:
        # Get all menu items for the given menu
        items = MenuItem.objects.filter(menu__title=menu)
        items_values = items.values()

        # Get the root menu items (without parent)
        root_item = [item for item in items_values.filter(parent=None)]

        # Determine the ID of the selected menu item from the request parameters
        selected_item_id = int(context['request'].GET[menu])
        selected_item = items.get(id=selected_item_id)

        # Get a list of IDs for the selected menu items
        selected_item_id_list = get_selected_item_id_list(selected_item, root_item, selected_item_id)

        # Add child items for each selected menu item
        for item in root_item:
            if item['id'] in selected_item_id_list:
                item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)

        result_dict = {'items': root_item}

    except (KeyError, ObjectDoesNotExist):
        # In case of an error, return a list of menu items without parent items
        result_dict = {
            'items': [
                item for item in MenuItem.objects.filter(menu__title=menu, parent=None).values()
            ]
        }

    # Add the menu name and additional query string to the result_dict dictionary
    result_dict['menu'] = menu
    result_dict['other_querystring'] = build_querystring(context, menu)

    return result_dict


def build_querystring(context: Context, menu: str) -> str:
    """
    Builds a query string based on the current request context.
    :param context: The current context.
    :param menu: The menu.
    :return: The built query string.
    """

    # Initialize a list to store query string arguments
    querystring_args = []

    # Loop through all parameters of the current request
    for key in context['request'].GET:
        # If the key of the current parameter does not match the passed 'menu' parameter
        if key != menu:
            # Add the "key=value" pair to the query string arguments list
            querystring_args.append(f"{key}={context['request'].GET[key]}")

    # Join the arguments from the list into a single query string, separated by the '&' character
    querystring = '&'.join(querystring_args)

    # Return the built query strings
    return querystring


def get_child_items(items_values, current_item_id, selected_item_id_list):
    """
    Returns a list of child items for the given menu item ID.

    :param items_values: A list of all menu items.
    :param current_item_id: The ID of the menu item for which to get child items.
    :param selected_item_id_list: A list of IDs for the selected menu items.
    :return: A list of child items for the given menu item ID.
    """
    item_list = [item for item in items_values.filter(parent_id=current_item_id)]
    for item in item_list:
        if item['id'] in selected_item_id_list:
            item['child_items'] = get_child_items(items_values, item['id'], selected_item_id_list)
    return item_list


def get_selected_item_id_list(parent: MenuItem, primary_item: List[MenuItem], selected_item_id: int) -> List[int]:
    """
    Returns a list of IDs for the selected menu items, starting from the parent item to the current one.

    :param parent: The parent menu item.
    :param primary_item: A list of root menu items.
    :param selected_item_id: The ID of the selected menu item.
    :return: A list of IDs for the selected menu items.
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
