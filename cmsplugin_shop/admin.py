from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.contrib import admin
from .utils import get_model, get_admin

admin.site.register(get_model('Node'),      get_admin('Node'))
admin.site.register(get_model('Category'),  get_admin('Category'))
admin.site.register(get_model('Product'),   get_admin('Product'))
admin.site.register(get_model('Shipping'),  get_admin('Shipping'))
admin.site.register(get_model('OrderState'),get_admin('OrderState'))
admin.site.register(get_model('Order'),     get_admin('Order'))

