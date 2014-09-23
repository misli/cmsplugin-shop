# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from menus.menu_pool import menu_pool

from .utils import get_menu


menu_pool.register_menu(get_menu('Catalog'))
