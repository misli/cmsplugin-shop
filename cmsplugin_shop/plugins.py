from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from cms.plugin_base import CMSPluginBase
from django.utils.translation import ugettext as _

from .utils import get_model



class ProductPlugin(CMSPluginBase):
    model = get_model('ProductPlugin')
    name = _('Product')
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'plugin': instance,
            'product': instance.product,
            'placeholder': placeholder,
        })
        return context

    def icon_src(self, instance):
        return instance.product.get_photo_url()



class CategoryPlugin(CMSPluginBase):
    model = get_model('CategoryPlugin')
    name = _('Category')
    text_enabled = True

    def render(self, context, instance, placeholder):
        context.update({
            'plugin': instance,
            'category': instance.category,
            'placeholder': placeholder,
        })
        return context

    def icon_src(self, instance):
        return instance.category.get_photo_url()

