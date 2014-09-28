from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf import settings
from django.utils.functional import cached_property

from .utils import get_model


Cart = get_model('Cart')


def cart(self):
    try:
        c = Cart.objects.get(id=self.session['cart_id'], order=None)
    except (KeyError, Cart.DoesNotExist):
        # create new one
        c = Cart()
    c.save()
    self.session['cart_id'] = c.id
    return c


class CartMiddleware(object):
    def process_request(self, request):
        type(request).cart = cached_property(cart)

