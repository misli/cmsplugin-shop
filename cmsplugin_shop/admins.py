from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.util import get_model_from_relation
from django.utils.encoding import smart_text, force_text
from django.utils.translation import ugettext_lazy as _
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.models import TreeForeignKey

from cms.utils import get_language_from_request

from .models import *


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
        self.lookup_choices      = Category.objects.order_by('tree_id', 'lft')
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



class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {'slug': ('name',)}
    trigger_save_after_move = True



class ProductVariantInlineAdmin(admin.TabularInline):
    model = ProductVariant
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    ordering        = ['tree_id', 'lft']
    list_display    = ['name', 'parent']
    list_filter     = [('parent', CategoryTreeListFilter)]
    inlines         = (ProductVariantInlineAdmin,)

    def lookup_allowed(self, key, value):
        return key in ['parent__lft__gte', 'parent__rght__lte', 'parent__tree_id'] \
           and value.isdigit() and True or super(ProductAdmin, self).lookup_allowed(key, value)



class OrderStateAdmin(admin.ModelAdmin):
    pass



class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['cart']
    list_filter     = ['state']
    list_display    = ['first_name', 'last_name', 'email', 'phone', 'address', 'shipping', 'state', 'cart']



class ShippingAdmin(admin.ModelAdmin):
    pass



