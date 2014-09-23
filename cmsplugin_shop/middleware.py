from __future__ import unicode_literals

from django.conf import settings

from .utils import get_model


Cart = get_model('Cart')


def cart(self):
    try:
        return self._cart
    except AttributeError:
        try:
            self._cart  = Cart.objects.get(id=self.session['cart_id'])
        except (KeyError, Cart.DoesNotExist):
            self._cart  = Cart()
            self._cart.save()
            self.session['cart_id'] = self._cart.id
    return self._cart


class CartMiddleware(object):
    def process_request(self, request):
        type(request).cart = property(cart)

