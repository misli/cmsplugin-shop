from __future__ import unicode_literals

import locale
import os
import string
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import get_language

try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string



def get_admin(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_ADMIN'.format(name.upper()),
        'cmsplugin_shop.admins.{}Admin'.format(name),
    ))

def get_form(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_FORM'.format(name.upper()),
        'cmsplugin_shop.forms.{}Form'.format(name),
    ))

def get_html_field():
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_HTML_FIELD',
        'djangocms_text_ckeditor.fields.HTMLField',
    ))

def get_menu(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_MENU'.format(name.upper()),
        'cmsplugin_shop.cms_menus.{}Menu'.format(name),
    ))

def get_model(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_MODEL'.format(name.upper()),
        'cmsplugin_shop.models.{}'.format(name),
    ))

def get_plugin(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_PLUGIN'.format(name.upper()),
        'cmsplugin_shop.plugins.{}Plugin'.format(name),
    ))

def get_toolbar(name):
    return import_string(getattr(settings,
        'CMSPLUGIN_SHOP_{}_TOOLBAR'.format(name.upper()),
        'cmsplugin_shop.cms_toolbars.{}Toolbar'.format(name),
    ))

def get_view(name):
    view = import_string(getattr(
        settings,
        'CMSPLUGIN_SHOP_{}_VIEW'.format(name.upper()),
        'cmsplugin_shop.views.{}'.format(name),
    ))
    return hasattr(view, 'as_view') and view.as_view() or view



class LocaleConv:
    def __init__(self, languages):
        """
        This function loads localeconv for all languages during module load.
        It is necessary, because using locale.setlocale later may be dangerous
        (It is not thread-safe in most of the implementations.)
        """
        original_locale_name = locale.setlocale(locale.LC_ALL)
        self.localeconv = {}
        for code, name in languages:
            locale_name = locale.locale_alias[code].split('.')[0]+'.UTF-8'
            locale.setlocale(locale.LC_ALL, str(locale_name))
            self.localeconv[code] = locale.localeconv()
        locale.setlocale(locale.LC_ALL, original_locale_name)

    def __call__(self, language=None):
        return self.localeconv[language or get_language()]


localeconv = LocaleConv(settings.LANGUAGES)



# This function is inspired by python's standard locale.currency().

def currency(val, international=False):
    """Formats val according to the currency settings for current language."""
    conv = localeconv()

    digits = conv[international and 'int_frac_digits' or 'frac_digits']

    # check for illegal values
    if digits == 127:
        raise ValueError("Currency formatting is not possible using the 'C' locale.")

    # grouping
    groups = []
    s = str(abs(int(val)))
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
    if digits and not isinstance(val, int):
        s += smart_text(conv['mon_decimal_point']) + '{{:.{}f}}'.format(digits).format(val).split('.')[1]

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


