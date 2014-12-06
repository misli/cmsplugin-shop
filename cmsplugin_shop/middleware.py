from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import datetime
from django.utils.functional import cached_property

from . import settings
from .models import Cart



def cart(self):
    try:
        c = Cart.objects.get(id=self.session[settings.SESSION_KEY_CART], order=None)
    except (KeyError, Cart.DoesNotExist):
        # delete expired carts
        Cart.objects.filter(
            last_updated__lt = datetime.date.today() - datetime.timedelta(settings.CART_EXPIRY_DAYS),
            order=None
        ).delete()
        # create new one
        c = Cart()
    self.session[settings.SESSION_KEY_CART] = c.id
    return c



def save_cart(self):
    self.cart.save()
    self.session[settings.SESSION_KEY_CART] = self.cart.id



class CartMiddleware(object):
    def process_request(self, request):
        type(request).cart = cached_property(cart)
        type(request).save_cart = save_cart

