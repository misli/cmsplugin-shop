from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.contrib import admin
from . import models
from .utils import get_admin

admin.site.register(models.Node,            get_admin('Node'))
admin.site.register(models.Category,        get_admin('Category'))
admin.site.register(models.Product,         get_admin('Product'))
admin.site.register(models.Cart,            get_admin('Cart'))
admin.site.register(models.DeliveryMethod,  get_admin('DeliveryMethod'))
admin.site.register(models.PaymentMethod,   get_admin('PaymentMethod'))
admin.site.register(models.OrderState,      get_admin('OrderState'))
admin.site.register(models.Order,           get_admin('Order'))

