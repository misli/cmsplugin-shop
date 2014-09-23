# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from .urls import catalog, cart, order


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


