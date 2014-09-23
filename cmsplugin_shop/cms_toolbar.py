from __future__ import unicode_literals

from cms.toolbar_pool import toolbar_pool

from .utils import get_toolbar

toolbar_pool.register(get_toolbar('Shop'))
