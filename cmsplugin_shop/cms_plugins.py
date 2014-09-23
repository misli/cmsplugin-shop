from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.plugin_pool import plugin_pool

from .utils import get_plugin

plugin_pool.register_plugin(get_plugin('Product'))
plugin_pool.register_plugin(get_plugin('Category'))

