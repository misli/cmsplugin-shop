# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import tagging

from cms.models import CMSPlugin
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModelBase

from . import settings
from .price import Price
from .utils import get_rand_hash, get_html_field


# allow different implementation of HTMLField
HTMLField = get_html_field()



class PriceField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('decimal_places', settings.DECIMAL_PLACES)
        kwargs.setdefault('max_digits',     settings.MAX_DIGITS)
        super(PriceField, self).__init__(*args, **kwargs)



class TaxRateField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('decimal_places', 4)
        kwargs.setdefault('max_digits',     9)
        kwargs.setdefault('choices',        settings.TAX_RATES.items())
        kwargs.setdefault('default',        settings.DEFAULT_TAX_RATE)
        super(TaxRateField, self).__init__(*args, **kwargs)



@MPTTModelBase.register
@python_2_unicode_compatible
class Node(models.Model):
    parent      = TreeForeignKey('self', verbose_name=_('category'), blank=True, null=True,
                    related_name='children', limit_choices_to={'product':None})
    name        = models.CharField(_('name'), max_length=250)
    slug        = models.SlugField(_('slug'), max_length=250, db_index=True, unique=False)
    summary     = HTMLField(_('summary'), blank=True, default='')
    description = HTMLField(_('description'), blank=True, default='')
    photo       = FilerImageField(verbose_name='Fotka', null=True, blank=True, on_delete=models.SET_NULL)
    page_title  = models.CharField(_('page title'), max_length=250, blank=True, null=True,
                    help_text=_('overwrite the title (html title tag)'))
    menu_title  = models.CharField(_('menu title'), max_length=250, blank=True, null=True,
                    help_text=_('overwrite the title in the menu'))
    meta_desc   = models.TextField(_('meta description'), blank=True, default='',
                    help_text=_('the text displayed in search engines'))
    active      = models.BooleanField(default=False, verbose_name=_('active'))

    class Meta:
        ordering            = ('tree_id', 'lft')
        unique_together     = [('parent', 'slug')]
        verbose_name        = _('tree node')
        verbose_name_plural = _('tree nodes')

    def __str__(self):
        return self.name

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

    def save(self, *args, **kwargs):
        errors = self._perform_unique_checks([(Node, ('parent', 'slug'))])
        if errors:
            raise ValidationError(errors)
        super(Node, self).save(*args, **kwargs)


class Category(Node):
    class Meta:
        ordering            = ('tree_id', 'lft')
        verbose_name        = _('category')
        verbose_name_plural = _('categories')

tagging.register(Category)



class Product(Node):
    date_added      = models.DateTimeField(_('date added'), auto_now_add=True)
    last_modified   = models.DateTimeField(_('last modified'), auto_now=True)
    multiple        = models.IntegerField(_('multiple'), default=1, null=False)
    unit            = models.CharField(_('unit'), max_length=30, blank=True, null=True)
    price           = PriceField(_('price'))
    tax_rate        = TaxRateField(_('tax rate'))
    related         = models.ManyToManyField('self', _('related products'), blank=True)
    voucher_exclude = models.BooleanField(_('excluded from vouchers'), default=False)

    class Meta:
        ordering            = ('tree_id', 'lft')
        verbose_name        = _('product')
        verbose_name_plural = _('products')

    @property
    def unit_price(self):
        return self.price / self.multiple

    def get_price(self):
        return Price(self.price, self.tax_rate)
    get_price.short_description = _('price')

    @cached_property
    def all_packages(self):
        return list(self.packages.all())


tagging.register(Product)



@python_2_unicode_compatible
class ProductPackage(models.Model):
    product             = models.ForeignKey(Product,
                            verbose_name=_('product'), related_name='packages')
    multiple            = models.IntegerField(_('multiple'))
    name                = models.CharField(_('name'), max_length=250, blank=True, null=True)
    price               = PriceField(_('price'), blank=True, null=True)
    relative_discount   = models.DecimalField(_('relative discount'),
                            decimal_places=4, max_digits=8, blank=True, null=True)
    nominal_discount    = PriceField(_('nominal discount'), blank=True, null=True)

    class Meta:
        ordering            = ('multiple',)
        verbose_name        = _('product package')
        verbose_name_plural = _('product packages')

    def get_price(self):
        if self.price:
            return Price(self.price, self.product.tax_rate)
        else:
            price = self.product.unit_price * self.multiple
            if self.relative_discount:
                price -= (price * self.relative_discount / 100)
            if self.nominal_discount:
                price -= self.nominal_discount
            return Price(price, self.product.tax_rate)
    get_price.short_description = _('price')

    def get_name(self):
        return self.name or '{} {}'.format(
            self.multiple,
            self.product.unit,
        )
    get_name.short_description = _('name')

    def __str__(self):
        return '{}, {}'.format(self.get_name(), self.get_price())


@python_2_unicode_compatible
class Cart(models.Model):
    last_updated = models.DateTimeField(_('last updated'), auto_now=True)

    class Meta:
        verbose_name        = _('cart')
        verbose_name_plural = _('carts')

    def __str__(self):
        return ', '.join(map(smart_text, self.all_items))

    def get_absolute_url(self):
        return reverse('Cart:cart')

    @cached_property
    def all_items(self):
        return list(self.items.order_by('product__name', 'package__multiple'))

    def get_price(self):
        if len(self.all_items):
            return sum(item.get_price() for item in self.all_items)
        else:
            return Price(0)
    get_price.short_description = _('price')



@python_2_unicode_compatible
class CartItem(models.Model):
    cart        = models.ForeignKey(Cart,           verbose_name=_('cart'),             related_name='items')
    product     = models.ForeignKey(Product,        verbose_name=_('product'),          related_name='+')
    package     = models.ForeignKey(ProductPackage, verbose_name=_('product package'),  related_name='+',
                    blank=False, null=True)
    quantity    = models.PositiveIntegerField(_('quantity'), default=1)
    price       = PriceField(_('price'))
    tax_rate    = TaxRateField(_('tax rate'))

    class Meta:
        unique_together     = [('cart', 'product', 'package')]
        verbose_name        = _('cart item')
        verbose_name_plural = _('cart items')

    def __str__(self):
        return '{}x {}{}'.format(self.quantity, self.product, self.package and ' {}'.format(self.package) or '')

    def get_unit_price(self):
        return Price(self.price, self.tax_rate)
    get_unit_price.short_description = _('unit price')

    def get_price(self):
        return Price(self.price * self.quantity, self.tax_rate)
    get_price.short_description = _('price')

    def save(self):
        if self.quantity:
            super(CartItem, self).save()
        elif self.id:
            super(CartItem, self).delete()



@python_2_unicode_compatible
class Method(models.Model):
    code        = models.SlugField(_('code'))
    name        = models.CharField(_('name'), max_length=150)
    description = HTMLField(_('description'), blank=True, default='')
    price       = PriceField(_('price'))
    tax_rate    = TaxRateField(_('tax rate'))
    ordering    = models.PositiveIntegerField(_('ordering'), default=1)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}, {}'.format(self.name, self.get_price())

    def get_price(self):
        return Price(self.price, self.tax_rate)


class DeliveryMethod(Method):
    class Meta:
        ordering            = ('ordering', 'name')
        verbose_name        = _('delivery method')
        verbose_name_plural = _('delivery methods')



class PaymentMethod(Method):
    class Meta:
        ordering            = ('ordering', 'name')
        verbose_name        = _('payment method')
        verbose_name_plural = _('payment methods')



@python_2_unicode_compatible
class Voucher(models.Model):
    name        = models.CharField(_('name'), max_length=250)
    slug        = models.SlugField(_('slug'), max_length=250, db_index=True, unique=False)
    summary     = HTMLField(_('summary'), blank=True, default='')
    photo       = FilerImageField(verbose_name='Fotka', null=True, blank=True, on_delete=models.SET_NULL)
    valid_from  = models.DateTimeField(_('valid_from'))
    valid_to    = models.DateTimeField(_('valid_to'))
    relative_discount   = models.DecimalField(_('relative discount'),
                            decimal_places=4, max_digits=8, blank=True, null=True)
    nominal_discount    = PriceField(_('nominal discount'), blank=True, null=True)
    categories  = models.ManyToManyField(Category, _('categories'), blank=True)
    delivery_methods = models.ManyToManyField(DeliveryMethod, verbose_name=_('delivery methods'), blank=True)
    payment_methods  = models.ManyToManyField(PaymentMethod, verbose_name=_('payment methods'), blank=True)
    one_time    = models.BooleanField(_('one time'), default=False)
    min_price   = PriceField(_('minimal price'), blank=True, null=True)

    class Meta:
        verbose_name        = _('voucher')
        verbose_name_plural = _('vouchers')

    def __str__(self):
        return self.name

    @cached_property
    def all_categories(self):
        return list(self.categories.all())

    @cached_property
    def all_delivery_methods(self):
        return list(self.delivery_methods.all())

    @cached_property
    def all_payment_methods(self):
        return list(self.payment_methods.all())



@python_2_unicode_compatible
class OrderState(models.Model):
    code        = models.SlugField(_('code'))
    name        = models.CharField(_('name'), max_length=150)
    description = HTMLField(_('description'), blank=True, default='')

    class Meta:
        verbose_name        = _('order state')
        verbose_name_plural = _('order states')

    def __str__(self):
        return self.name




@python_2_unicode_compatible
class Order(models.Model):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                        on_delete=models.SET_NULL)
    slug            = models.SlugField(editable=False)
    date            = models.DateTimeField(auto_now_add=True, editable=False)
    cart            = models.OneToOneField(Cart, verbose_name=_('cart'), editable=False)
    state           = models.ForeignKey(OrderState, verbose_name=_('state'))
    first_name      = models.CharField(_('first name'), max_length=30)
    last_name       = models.CharField(_('last name'), max_length=30)
    email           = models.EmailField(_('email'))
    phone           = models.CharField(_('phone'), max_length=150, validators=[
                        RegexValidator(r'^\+?[0-9 ]+$')])
    address         = models.TextField(_('address'))
    note            = models.TextField(_('note'), blank=True)
    comment         = models.TextField(_('internal comment'), blank=True)
    delivery_method = models.ForeignKey(DeliveryMethod, verbose_name=_('delivery method'))
    payment_method  = models.ForeignKey(PaymentMethod, verbose_name=_('payment method'))
    voucher         = models.ForeignKey(Voucher, verbose_name=_('voucher'), related_name='orders',
                        blank=True, null=True)

    class Meta:
        ordering            = ('-date',)
        verbose_name        = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return '{} {} {}'.format(self.date, self.first_name, self.last_name)

    def get_confirm_url(self):
        return reverse('Order:confirm', kwargs={'slug':self.slug})

    def get_edit_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.id,))

    def get_absolute_url(self):
        return self.user \
           and reverse('MyOrders:detail', kwargs={'pk':self.pk}) \
            or reverse('Order:detail', kwargs={'slug':self.slug})

    @cached_property
    def cart_price(self):
        return self.cart.get_price()

    @cached_property
    def delivery_method_price(self):
        return self.delivery_method.get_price()

    @cached_property
    def payment_method_price(self):
        return self.payment_method.get_price()

    @cached_property
    def voucher_price(self):
        # check voucher
        if not self.voucher:
            return Price(0)

        # check categories
        if self.voucher.all_categories:
            items = [
                item for item in self.cart.all_items
                if (
                    not item.product.voucher_exclude and
                    any(item.product.is_descendant_of(cat) for cat in self.voucher.all_categories)
                )
            ]
            if not items:
                return Price(0)
        else:
            items = [
                item for item in self.cart.all_items
                if not item.product.voucher_exclude
            ]

        # check minimal price
        if self.voucher.min_price:
            items_price = sum(item.get_price() for item in items)
            if items_price < Price(self.voucher.min_price):
                return Price(0)

        # check delivery method
        if self.voucher.all_delivery_methods and self.delivery_method not in delivery_methods:
            return Price(0)

        # check payment method
        if self.voucher.all_payment_methods and self.payment_method not in payment_methods:
            return Price(0)

        # return nominal discount
        if self.voucher.nominal_discount:
            return Price(-self.voucher.nominal_discount)

        # return relative discount
        return sum(item.get_price() * (self.voucher.relative_discount / -100) for item in items)

    @cached_property
    def price(self):
        return self.cart_price \
             + self.delivery_method_price \
             +  self.payment_method_price \
             + self.voucher_price
    price.short_description = _('price')

    def send_customer_mail(self):
        send_mail(
            _('Order accepted'),
            get_template('cmsplugin_shop/order_customer_mail.txt').render(Context({
                'site':  Site.objects.get_current(),
                'order': self,
            })),
            settings.SHOP_EMAIL,
            [self.email],
            **settings.SEND_MAIL_KWARGS
        )

    def send_manager_mail(self):
        send_mail(
            _('New order received'),
            get_template('cmsplugin_shop/order_manager_mail.txt').render(Context({
                'site':  Site.objects.get_current(),
                'order': self,
            })),
            settings.SHOP_EMAIL,
            map(lambda m: u'"{}" <{}>'.format(m[0], m[1]), settings.settings.MANAGERS),
            **settings.SEND_MAIL_KWARGS
        )

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



@python_2_unicode_compatible
class ProductPlugin(CMSPlugin):
    product     = models.ForeignKey(Product, verbose_name=_('product'))
    template    = models.CharField(_('template'), max_length=100, choices=settings.PRODUCT_TEMPLATES,
                                default=settings.PRODUCT_TEMPLATES[0][0],
                                help_text=_('the template used to render plugin'))

    def __str__(self):
        return self.product.name

    @cached_property
    def render_template(self):
        return 'cmsplugin_shop/product/%s.html' % self.template



@python_2_unicode_compatible
class CategoryPlugin(CMSPlugin):
    category    = models.ForeignKey(Category, verbose_name=_('category'))
    template    = models.CharField(_('template'), max_length=100, choices=settings.CATEGORY_TEMPLATES,
                                default=settings.CATEGORY_TEMPLATES[0][0],
                                help_text=_('the template used to render plugin'))

    def __str__(self):
        return self.category.name

    @cached_property
    def render_template(self):
        return 'cmsplugin_shop/category/%s.html' % self.template


