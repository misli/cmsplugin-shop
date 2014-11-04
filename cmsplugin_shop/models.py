# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import tagging

from cms.models import CMSPlugin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from .utils import currency, get_rand_hash, get_html_field


# allow different implementation of HTMLField
HTMLField = get_html_field()

DECIMAL_PLACES  = getattr(settings, 'CMSPLUGIN_SHOP_PRICE_DECIMAL_PLACES', 2)
MAX_DIGITS      = getattr(settings, 'CMSPLUGIN_SHOP_PRICE_MAX_DIGITS', 9)



class PriceField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('decimal_places', DECIMAL_PLACES)
        kwargs.setdefault('max_digits',     MAX_DIGITS)
        kwargs.setdefault('blank',          True)
        kwargs.setdefault('null',           True)
        super(PriceField, self).__init__(*args, **kwargs)



@python_2_unicode_compatible
class Node(MPTTModel):
    parent      = TreeForeignKey('self', verbose_name=_('Category'), blank=True, null=True,
                    related_name='children', limit_choices_to={'is_category':True})
    name        = models.CharField(_('Name'), max_length=250)
    slug        = models.SlugField(_('Slug'), max_length=250, db_index=True, unique=False)
    summary     = HTMLField(_('Summary'), blank=True, default='')
    description = HTMLField(_('Description'), blank=True, default='')
    page_title  = models.CharField(_('Page title'), max_length=250, blank=True, null=True,
                    help_text=_('Overwrite the title (html title tag)'))
    menu_title  = models.CharField(_('Menu title'), max_length=250, blank=True, null=True,
                    help_text=_('Overwrite the title in the menu'))
    meta_desc   = models.TextField(_('Meta description'), blank=True, default='',
                    help_text=_('The text displayed in search engines.'))
    active      = models.BooleanField(default=False, verbose_name=_('Active'))
    is_category = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name        = _('Tree node')
        verbose_name_plural = _('Tree')
        unique_together = [('parent', 'slug')]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        errors = self._perform_unique_checks([(Node, ('parent', 'slug'))])
        if errors:
            raise ValidationError(errors)
        super(Node, self).save(*args, **kwargs)

    def get_absolute_url(self):
        path = '/'.join([n.slug for n in self.get_ancestors()]+[self.slug])
        return reverse('Catalog:catalog', args=(path,))

    def get_edit_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.id,))

    def get_name(self):
        return self.name

    def get_page_title(self):
        return self.page_title or self.name

    def get_menu_title(self):
        return self.menu_title or self.name

tagging.register(Node)



class Category(Node):

    class Meta:
        verbose_name        = _('Category')
        verbose_name_plural = _('Categories')

    def get_descendants_all(self, *args, **kwargs):
        return super(Category, self).get_descendants(*args, **kwargs)

    def get_descendants(self, *args, **kwargs):
        return super(Category, self).get_descendants(*args, **kwargs).filter(is_category=True)

    def get_descendant_products(self, *args, **kwargs):
        return super(Category, self).get_descendants(*args, **kwargs).filter(is_category=False)

    def save(self, *args, **kwargs):
        self.is_category = True
        super(Category, self).save(*args, **kwargs)



class Product(Node):
    date_added = models.DateTimeField(auto_now_add=True,
        verbose_name=_('Date added'))
    last_modified = models.DateTimeField(auto_now=True,
        verbose_name=_('Last modified'))
    unit_price = PriceField(_('Unit price'))
    related = models.ManyToManyField('self', _('Related products'), blank=True)

    class Meta:
        verbose_name        = _('Product')
        verbose_name_plural = _('Products')

    def get_price(self):
        return self.unit_price

    @cached_property
    def all_variants(self):
        return list(self.variants.all())



@python_2_unicode_compatible
class ProductVariant(models.Model):
    product     = models.ForeignKey(Product, verbose_name=_('Product'), related_name='variants')
    name        = models.CharField(_('Name'), max_length=50)
    unit_price  = PriceField(_('Unit price'))
    ordering    = models.PositiveIntegerField(_('Ordering'), default=1)

    class Meta:
        ordering            = ('ordering', 'name')
        verbose_name        = _('Product variant')
        verbose_name_plural = _('Product variants')

    def __str__(self):
        return '{} ({})'.format(self.name, currency(self.get_price()))

    def get_price(self):
        return self.unit_price or self.product.unit_price



@python_2_unicode_compatible
class Cart(models.Model):
    last_updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __str__(self):
        return ', '.join(map(unicode, self.all_items))

    def get_absolute_url(self):
        return reverse('Cart:cart')

    @cached_property
    def all_items(self):
        return list(self.items.order_by('product__name', 'variant__name'))

    def get_price(self):
        return sum(item.get_price() for item in self.all_items)



@python_2_unicode_compatible
class CartItem(models.Model):
    cart        = models.ForeignKey(Cart,           verbose_name=_('Cart'),             related_name='items')
    product     = models.ForeignKey(Product,        verbose_name=_('Product'),          related_name='+')
    variant     = models.ForeignKey(ProductVariant, verbose_name=_('Product variant'),  related_name='+',
                    blank=False, null=True)
    quantity    = models.PositiveIntegerField(_('Quantity'), default=1)

    class Meta(object):
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')
        unique_together = [('cart', 'product', 'variant')]

    def __str__(self):
        return '{}x {}{}'.format(self.quantity, self.product, self.variant and ' {}'.format(self.variant) or '')

    def get_unit_price(self):
        return self.variant \
           and self.variant.get_price() \
            or self.product.get_price()

    def get_price(self):
        return self.variant \
           and (self.variant.get_price() * self.quantity) \
            or (self.product.get_price() * self.quantity)

    def save(self):
        if self.quantity == 0:
            if self.id:
                super(CartItem, self).delete()
        else:
            super(CartItem, self).save()



@python_2_unicode_compatible
class Shipping(models.Model):
    name        = models.CharField(_('Name'), max_length=150)
    description = HTMLField(_('Address'), blank=True, default='')
    price       = PriceField(_('Price'))
    ordering    = models.PositiveIntegerField(_('Ordering'), default=1)

    class Meta:
        ordering            = ('ordering', 'name')
        verbose_name        = _('Shipping')
        verbose_name_plural = _('Shippings')

    def __str__(self):
        return '{}, {}'.format(self.name, currency(self.get_price()))

    def get_price(self):
        return self.price



@python_2_unicode_compatible
class OrderState(models.Model):
    code        = models.SlugField(_('Code'))
    name        = models.CharField(_('Name'), max_length=150)
    description = HTMLField(_('Description'), blank=True, default='')

    class Meta:
        verbose_name        = _('Order state')
        verbose_name_plural = _('Order states')

    def __str__(self):
        return self.name



@python_2_unicode_compatible
class Order(models.Model):
    slug        = models.SlugField(editable=False)
    date        = models.DateTimeField(auto_now_add=True, editable=False)
    cart        = models.OneToOneField(Cart, verbose_name=_('Cart'), editable=False)
    state       = models.ForeignKey(OrderState, verbose_name=_('State'))
    first_name  = models.CharField(_('First name'), max_length=30)
    last_name   = models.CharField(_('Last name'), max_length=30)
    email       = models.EmailField(_('E-mail'))
    phone       = models.CharField(_('Phone'), max_length=150, validators=[
                    RegexValidator(r'^\+?[0-9 ]+$')])
    address     = models.TextField(_('Address'))
    note        = models.TextField(_('Note'), blank=True)
    comment     = models.TextField(_('Internal comment'), blank=True)
    shipping    = models.ForeignKey(Shipping, verbose_name=_('Shipping'))

    class Meta(object):
        ordering            = ('-date',)
        verbose_name        = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return '{} {} {}'.format(self.date, self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('Order:pdf', kwargs={'slug':self.slug})

    def get_price(self):
        return self.cart.get_price() + self.shipping.get_price()

    def save(self, *args, **kwargs):
        if self.slug:
            super(Order, self).save(*args, **kwargs)
        else:
            tries = 10
            while True:
                self.slug = get_rand_hash()
                try:
                    super(Order, self).save(*args, **kwargs)
                    break
                except:
                    if tries:
                        tries -= 1
                    else:
                        raise



PRODUCT_TEMPLATES = getattr(settings, 'CMSPLUGIN_SHOP_PRODUCT_TEMPLATES', (
    ('default', _('Default')),
))
CATEGORY_TEMPLATES = getattr(settings, 'CMSPLUGIN_SHOP_CATEGORY_TEMPLATES', (
    ('default', _('Default')),
))



@python_2_unicode_compatible
class ProductPlugin(CMSPlugin):
    product     = models.ForeignKey(Product, verbose_name=_('Product'))
    template    = models.CharField(_('Template'), max_length=100, choices=PRODUCT_TEMPLATES,
                                default=PRODUCT_TEMPLATES[0][0],
                                help_text=_('The template used to render plugin.'))

    def __str__(self):
        return self.product.name

    @cached_property
    def render_template(self):
        return 'cmsplugin_shop/product/%s.html' % self.template



@python_2_unicode_compatible
class CategoryPlugin(CMSPlugin):
    category    = models.ForeignKey(Category, verbose_name=_('Category'))
    template    = models.CharField(_('Template'), max_length=100, choices=CATEGORY_TEMPLATES,
                                default=CATEGORY_TEMPLATES[0][0],
                                help_text=_('The template used to render plugin.'))

    def __str__(self):
        return self.category.name

    @cached_property
    def render_template(self):
        return 'cmsplugin_shop/category/%s.html' % self.template

