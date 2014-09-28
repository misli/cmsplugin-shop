from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import datetime
from django.conf import settings
from django.utils.functional import cached_property

from .utils import get_model


Cart = get_model('Cart')


CART_EXPIRY = getattr(settings, 'CMSPLUGIN_SHOP_CART_EXPIRY', 1)


def cart(self):
    try:
        c = Cart.objects.get(id=self.session['cart_id'], order=None)
    except (KeyError, Cart.DoesNotExist):
        # delete expired carts
        Cart.objects.filter(
            last_updated__lt = datetime.date.today() - datetime.timedelta(CART_EXPIRY),
            order=None
        ).delete()
        # create new one
        c = Cart()
    c.save()
    self.session['cart_id'] = c.id
    return c


class CartMiddleware(object):
    def process_request(self, request):
        type(request).cart = cached_property(cart)

