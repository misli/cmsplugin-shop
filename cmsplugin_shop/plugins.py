from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext as _

from .models import ProductPlugin, CategoryPlugin



class ProductPlugin(CMSPluginBase):
    model = ProductPlugin
    name = _('Product')
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'plugin': instance,
            'product': instance.product,
            'placeholder': placeholder,
        })
        return context



class CategoryPlugin(CMSPluginBase):
    model = CategoryPlugin
    name = _('Category')
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'plugin': instance,
            'category': instance.category,
            'placeholder': placeholder,
        })
        return context


