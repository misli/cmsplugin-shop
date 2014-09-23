# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.menu_bases import CMSAttachMenu
from django.utils.translation import ugettext_lazy as _
from menus.base import NavigationNode

from .models import Node


class CatalogMenu(CMSAttachMenu):
    name = _('Catalog')

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        if request.user.is_staff:
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


