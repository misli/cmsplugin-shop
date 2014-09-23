from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.toolbar_pool import toolbar_pool

from .utils import get_toolbar

toolbar_pool.register(get_toolbar('Shop'))
