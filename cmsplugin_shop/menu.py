# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from menus.menu_pool import menu_pool

from .utils import get_menu


menu_pool.register_menu(get_menu('Catalog'))
