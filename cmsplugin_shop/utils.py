from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import locale
import os
import string
from decimal import Decimal
from django.db.models import Model
from django.utils.encoding import smart_text
from django.utils.translation import get_language

from . import settings

try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string


class EmptyMixin(Model):
    class Meta:
        abstract = True

def get_admin(name):
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_ADMIN'.format(name.upper()),
        'cmsplugin_shop.admins.{}Admin'.format(name),
    ))

def get_form(name):
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_FORM'.format(name.upper()),
        'cmsplugin_shop.forms.{}Form'.format(name),
    ))

def get_html_field():
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_HTML_FIELD',
        'djangocms_text_ckeditor.fields.HTMLField',
    ))

def get_menu(name):
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_MENU'.format(name.upper()),
        'cmsplugin_shop.cms_menus.{}Menu'.format(name),
    ))

def get_mixin(name):
    mixin = getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_MIXIN'.format(name.upper()), None)
    return mixin and import_string(mixin) or EmptyMixin

def get_plugin(name):
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_PLUGIN'.format(name.upper()),
        'cmsplugin_shop.plugins.{}Plugin'.format(name),
    ))

def get_toolbar(name):
    return import_string(getattr(settings.settings,
        'CMSPLUGIN_SHOP_{}_TOOLBAR'.format(name.upper()),
        'cmsplugin_shop.cms_toolbars.{}Toolbar'.format(name),
    ))

def get_view(name):
    view = import_string(getattr(
        settings.settings,
        'CMSPLUGIN_SHOP_{}_VIEW'.format(name.upper()),
        'cmsplugin_shop.views.{}'.format(name),
    ))
    return hasattr(view, 'as_view') and view.as_view() or view



QUANTIZE = Decimal((0,(1,),-settings.DECIMAL_PLACES))

def quantize(price):
    return price.quantize(QUANTIZE)



class LocaleConvCache(object):
    def __init__(self, languages):
        """
        This function loads localeconv for all languages during module load.
        It is necessary, because using locale.setlocale later may be dangerous
        (It is not thread-safe in most of the implementations.)
        """
        self._conv = {}
        original_locale_name = locale.setlocale(locale.LC_ALL)
        for code, name in languages:
            locale_name = locale.locale_alias[code].split('.')[0]+'.UTF-8'
            locale.setlocale(locale.LC_ALL, str(locale_name))
            self._conv[code] = locale.localeconv()
        locale.setlocale(locale.LC_ALL, original_locale_name)

    def getconv(self, language=None):
        return self._conv[language or get_language()].copy()

localeconv_cache = LocaleConvCache(settings.settings.LANGUAGES)



# This function is inspired by python's standard locale.currency().

def currency(val, localeconv=None, international=False):
    """Formats val according to the currency settings for current language."""
    val = Decimal(val)
    conv = localeconv_cache.getconv()
    conv.update(localeconv or settings.LOCALECONV)

    # split integer part and fraction
    parts = str(abs(val)).split('.')

    # grouping
    groups = []
    s = parts[0]
    for interval in locale._grouping_intervals(conv['mon_grouping']):
        if not s:
            break
        groups.append(s[-interval:])
        s = s[:-interval]
    if s:
        groups.append(s)
    groups.reverse()
    s = smart_text(conv['mon_thousands_sep']).join(groups)

    # display fraction for non integer values
    if len(parts) > 1:
        s += smart_text(conv['mon_decimal_point']) + parts[1]

    # '<' and '>' are markers if the sign must be inserted between symbol and value
    s = '<' + s + '>'

    smb = smart_text(conv[international and 'int_curr_symbol' or 'currency_symbol'])
    precedes = conv[val<0 and 'n_cs_precedes' or 'p_cs_precedes']
    separated = conv[val<0 and 'n_sep_by_space' or 'p_sep_by_space']

    if precedes:
        s = smb + (separated and ' ' or '') + s
    else:
        s = s + (separated and ' ' or '') + smb

    sign_pos = conv[val<0 and 'n_sign_posn' or 'p_sign_posn']
    sign = conv[val<0 and 'negative_sign' or 'positive_sign']

    if sign_pos == 0:
        s = '(' + s + ')'
    elif sign_pos == 1:
        s = sign + s
    elif sign_pos == 2:
        s = s + sign
    elif sign_pos == 3:
        s = s.replace('<', sign)
    elif sign_pos == 4:
        s = s.replace('>', sign)
    else:
        # the default if nothing specified;
        # this should be the most fitting sign position
        s = sign + s

    return s.replace('<', '').replace('>', '')



def get_rand_hash(length=32, stringset=string.ascii_letters+string.digits):
    return ''.join([stringset[i%len(stringset)] for i in [ord(x) for x in os.urandom(length)]])


