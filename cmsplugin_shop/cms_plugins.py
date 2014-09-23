from cms.plugin_pool import plugin_pool

from .utils import get_plugin

plugin_pool.register_plugin(get_plugin('Product'))
plugin_pool.register_plugin(get_plugin('Category'))

