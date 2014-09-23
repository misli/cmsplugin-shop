from __future__ import unicode_literals

from cms.toolbar_base import CMSToolbar
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from .utils import get_model

Product  = get_model('Product')
Category = get_model('Category')

class ShopToolbar(CMSToolbar):
    def populate(self):
        admin_menu = self.toolbar.get_or_create_menu('shop_menu', _('Shop'))
        admin_menu.add_modal_item(_('Add product'), url=reverse('admin:{}_{}_add'.format(Product._meta.app_label, Product._meta.model_name)))
        admin_menu.add_modal_item(_('Add category'), url=reverse('admin:{}_{}_add'.format(Category._meta.app_label, Category._meta.model_name)))
