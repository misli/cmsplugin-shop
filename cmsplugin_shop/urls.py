from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, url

from .utils import get_view


catalog = patterns('',
    url('^(?P<path>.*)$', get_view('catalog'), name='catalog'),
)

cart = patterns('',
    url('^$',       get_view('cart'),       name='cart'),
)

order = patterns('',
    url('^$',                       get_view('order_form'),     name='form'),
    url(r'^(?P<slug>[^/]+)/$',      get_view('order_confirm'),  name='confirm'),
    url(r'^(?P<slug>[^.]+).pdf$',   get_view('order_pdf'),      name='pdf'),
)

