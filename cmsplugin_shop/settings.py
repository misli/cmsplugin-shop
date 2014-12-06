from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

def S(name, default_value):
    return getattr(settings, 'CMSPLUGIN_SHOP_'+name, default_value)



AUTH_USER_MODEL     = settings.AUTH_USER_MODEL

LOCALECONV          = S('LOCALECONV', {
    'currency_symbol': '$',
    'int_curr_symbol': 'USD ',
})
DECIMAL_PLACES      = S('PRICE_DECIMAL_PLACES', 2)
MAX_DIGITS          = S('PRICE_MAX_DIGITS',     9)
TAX_RATES           = S('TAX_RATES', {0:_('no tax')})
DEFAULT_TAX_RATE    = S('DEFAULT_TAX_RATE', TAX_RATES.keys()[0])

PRICE_TYPE          = S('PRICE_TYPE', 'gross')

PRODUCT_TEMPLATES   = S('PRODUCT_TEMPLATES', (('default', _('default')),))
CATEGORY_TEMPLATES  = S('CATEGORY_TEMPLATES', (('default', _('default')),))

CART_EXPIRY_DAYS    = S('CART_EXPIRY_DAYS', 1)
SESSION_KEY_CART    = S('SESSION_KEY_CART', 'cmsplugin_shop_cart_id')

SHOP_EMAIL          = S('EMAIL', settings.SERVER_EMAIL)
SEND_MAIL_KWARGS    = S('SEND_MAIL_KWARGS', {})

INITIAL_ORDER_STATE = S('INITIAL_ORDER_STATE', 'new')

PROFILE_ATTRIBUTE   = getattr(settings, 'AUTH_USER_PROFILE_ATTRIBUTE', 'profile')


