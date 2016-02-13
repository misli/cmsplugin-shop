# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.menu_bases import CMSAttachMenu
from django.db.models.signals import post_delete, post_save
from django.utils.translation import ugettext_lazy as _
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Node, Category


class CatalogMenu(CMSAttachMenu):
    name = _('Catalog')

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        if request.toolbar.use_draft:
            qs = Node.objects.order_by('tree_id', 'lft')
        else:
            qs = Node.objects.filter(active=True).order_by('tree_id', 'lft')
        return [
            NavigationNode(
                node.get_menu_title(),
                node.get_absolute_url(),
                node.id,
                node.parent and node.parent.id or None,
            ) for node in qs
        ]


menu_pool.register_menu(CatalogMenu)

def invalidate_menu_cache(sender, **kwargs):
    menu_pool.clear()

post_save.connect(invalidate_menu_cache, sender=Category)
post_delete.connect(invalidate_menu_cache, sender=Category)

