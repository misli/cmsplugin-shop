from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from collections import namedtuple
from decimal import Decimal
from django.utils.encoding import python_2_unicode_compatible
from itertools import groupby

from .settings import PRICE_TYPE
from .utils import quantize, currency



@python_2_unicode_compatible
class BasePrice(object):

    def __lt__(self, other):
        try:
            if PRICE_TYPE == 'gross':
                return self.gross < other.gross
            else:
                return self.net   < other.net
        except:
            return NotImplemented

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        try:
            if PRICE_TYPE == 'gross':
                return self.gross == other.gross
            else:
                return self.net   == other.net
        except:
            return False

    def __ne__(self, other):
        return not self == other

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    @property
    def tax(self):
        return self.gross - self.net

    def __str__(self):
        if PRICE_TYPE == 'gross':
            return currency(self.gross)
        else:
            return currency(self.net)



class Price(BasePrice, namedtuple('Price', 'net gross rate')):

    def __new__(cls, price, rate=0):
        price = Decimal(price)
        rate  = Decimal(rate)
        if rate:
            if PRICE_TYPE == 'gross':
                gross   = quantize(price)
                net     = quantize(gross / rate)
            else:
                net     = quantize(price)
                gross   = quantize(net * rate)
        else:
            gross = net = quantize(price)
        return super(Price, cls).__new__(cls, net, gross, rate)

    def __mul__(self, other):
        try:
            other = Decimal(other)
            if PRICE_TYPE == 'gross':
                return Price(self.gross * other, self.rate)
            else:
                return Price(self.net   * other, self.rate)
        except TypeError:
            return NotImplemented

    def __add__(self, other):
        if isinstance(other, Price):
            return ComplexPrice((self, other))
        elif isinstance(other, ComplexPrice):
            return ComplexPrice((self,) + other.prices)
        else:
            try:
                return self + Price(other, self.rate)
            except TypeError:
                return NotImplemented



class ComplexPrice(BasePrice, namedtuple('ComplexPrice', 'net gross prices')):

    def __new__(cls, prices):
        prices  = tuple(prices)
        net     = Decimal(0)
        gross   = Decimal(0)
        for price in prices:
            net   += price.net
            gross += price.gross
        return super(ComplexPrice, cls).__new__(cls, net, gross, prices)

    def __add__(self, other):
        if isinstance(other, Price):
            return ComplexPrice(self.prices + (other,))
        elif isinstance(other, ComplexPrice):
            return ComplexPrice(self.prices + other.prices)
        else:
            return NotImplemented

    @property
    def rates(self):
        return map(
            lambda (rate, prices): (rate, ComplexPrice(prices)),
            groupby(self.prices, lambda price: price.rate),
        )

