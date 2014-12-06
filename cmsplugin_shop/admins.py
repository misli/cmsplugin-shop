from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.util import get_model_from_relation
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text, force_text
from django.utils.translation import ugettext_lazy as _
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.models import TreeForeignKey

from cms.utils import get_language_from_request

from . import models
from .utils import get_form, get_admin


class CategoryTreeListFilter(admin.FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_tid    = '%s__tree_id' % (field_path)
        self.lookup_kwarg_lft    = '%s__lft__gte' % (field_path)
        self.lookup_kwarg_rght   = '%s__rght__lte' % (field_path)
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val_tid      = request.GET.get(self.lookup_kwarg_tid, None)
        self.lookup_val_lft      = request.GET.get(self.lookup_kwarg_lft, None)
        self.lookup_val_rght     = request.GET.get(self.lookup_kwarg_rght, None)
        self.lookup_val_isnull   = request.GET.get(self.lookup_kwarg_isnull, None)
        self.lookup_choices      = models.Category.objects.order_by('tree_id', 'lft')
        super(CategoryTreeListFilter, self).__init__(
            field, request, params, model, model_admin, field_path
        )
        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title

    def has_output(self):
        if hasattr(self.field, 'rel') and self.field.null:
            extra = 1
        else:
            extra = 0
        return len(self.lookup_choices) + extra > 1

    def expected_parameters(self):
        return [self.lookup_kwarg_lft, self.lookup_kwarg_rght, self.lookup_kwarg_isnull]

    def choices(self, cl):
        from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
        yield {
            'selected': self.lookup_val_tid is None
                    and self.lookup_val_lft is None
                    and self.lookup_val_rght is None
                    and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({}, [
                        self.lookup_kwarg_tid,
                        self.lookup_kwarg_lft,
                        self.lookup_kwarg_rght,
                        self.lookup_kwarg_isnull,
            ]),
            'display': _('All'),
        }
        for val in self.lookup_choices:
            yield {
                'selected': self.lookup_val_lft == val.lft and self.lookup_val_rght == val.rght,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg_tid:  val.tree_id,
                    self.lookup_kwarg_lft:  val.lft,
                    self.lookup_kwarg_rght: val.rght,
                }, [self.lookup_kwarg_isnull]),
                'display': '{}{}'.format(val.level*'- ', val),
            }
        if self.field.null:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': cl.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [
                    self.lookup_kwarg_tid,
                    self.lookup_kwarg_lft,
                    self.lookup_kwarg_rght,
                ]),
                'display': EMPTY_CHANGELIST_VALUE,
            }



class CategoryAdmin(admin.ModelAdmin):
    form            = get_form('Category')
    ordering        = ['tree_id', 'lft']
    list_display    = ['name', 'parent', 'active']
    list_filter     = [('parent', CategoryTreeListFilter)]
    search_fields   = ['name', 'summary', 'description']
    prepopulated_fields = {'slug': ('name',)}
    trigger_save_after_move = True

    def lookup_allowed(self, key, value):
        return key in ['parent__lft__gte', 'parent__rght__lte', 'parent__tree_id'] \
           and value.isdigit() and True or super(ProductAdmin, self).lookup_allowed(key, value)



class ProductPackageInlineAdmin(admin.TabularInline):
    model = models.ProductPackage
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    form            = get_form('Product')
    ordering        = ['tree_id', 'lft']
    list_display    = ['name', 'parent', 'active', 'multiple', 'unit', 'price', 'tax_rate']
    list_editable   = ['active', 'multiple', 'unit', 'price', 'tax_rate']
    list_filter     = ['active', ('parent', CategoryTreeListFilter)]
    search_fields   = ['name', 'summary', 'description']
    inlines         = [ProductPackageInlineAdmin]
    filter_horizontal   = ['related']
    prepopulated_fields = {'slug': ('name',)}

    def lookup_allowed(self, key, value):
        return key in ['parent__lft__gte', 'parent__rght__lte', 'parent__tree_id'] \
           and value.isdigit() and True or super(ProductAdmin, self).lookup_allowed(key, value)



class NodeAdmin(DjangoMpttAdmin):
    def has_add_permission(self, request):
        # Nodes must always be added as Product or Category
        return False



class OrderStateAdmin(admin.ModelAdmin):
    pass



class CartItemInlineAdmin(admin.TabularInline):
    model = models.CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    ordering        = ['-last_updated']
    inlines         = [CartItemInlineAdmin]
    readonly_fields = ['last_updated', 'get_price']



class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['slug', 'cart_link']
    list_filter     = ['state']
    list_display    = ['id', 'date', 'first_name', 'last_name', 'email',
                       'phone', 'address', 'delivery_method', 'payment_method',
                       'state', 'get_price', 'cart_link']
    search_fields   = ['first_name', 'last_name', 'email', 'phone', 'address']

    def cart_link(self, order):
        return '<a href="{}">{}</a>'.format(
            reverse('admin:cmsplugin_shop_cart_change', args=(order.cart_id,)),
            order.cart,
        )
    cart_link.short_description = _('cart')
    cart_link.allow_tags = True



class DeliveryMethodAdmin(admin.ModelAdmin):
    pass



class PaymentMethodAdmin(admin.ModelAdmin):
    pass



