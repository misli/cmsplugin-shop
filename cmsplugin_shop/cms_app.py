# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from .urls import catalog, cart, order, my_orders


@apphook_pool.register
class CatalogApp(CMSApp):
    name     = _('Catalog')
    urls     = [catalog]
    app_name = 'Catalog'


@apphook_pool.register
class CartApp(CMSApp):
    name     = _('Cart')
    urls     = [cart]
    app_name = 'Cart'


@apphook_pool.register
class OrderApp(CMSApp):
    name     = _('Order')
    urls     = [order]
    app_name = 'Order'


@apphook_pool.register
class MyOrdersApp(CMSApp):
    name     = _('My orders')
    urls     = [my_orders]
    app_name = 'MyOrders'


