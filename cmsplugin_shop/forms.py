# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from datetime import date
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from tagging.forms import TagField
from tagging.utils import edit_string_for_tags

from . import models



class TaggingFormMixin(forms.ModelForm):
    tags = TagField(required=False, help_text=_(
        'Enter space separated list of single word tags ' \
        'or comma separated list of tags containing spaces. ' \
        'Use doublequotes to enter name containing comma.'
    ))

    def __init__(self, *args, **kwargs):
        super(TaggingFormMixin, self).__init__(*args, **kwargs)
        self.initial['tags'] = edit_string_for_tags(self.instance.tags.all())

    def save(self, commit=True):
        super(TaggingFormMixin, self).save(commit)
        self.instance.tags = self.cleaned_data['tags']
        return self.instance



class CategoryForm(TaggingFormMixin):
    class Meta:
        model   = models.Category



class ProductForm(TaggingFormMixin):
    class Meta:
        model   = models.Product



class CartItemForm(forms.ModelForm):

    def __init__(self, product, *args, **kwargs):
        self.product = product
        super(CartItemForm, self).__init__(*args, **kwargs)
        if self.product.all_packages:
            self.fields['package'].widget.choices = tuple(
                (package.id, str(package))
                for package in self.product.all_packages
            )
        else:
            del(self.fields['package'])

    class Meta:
        model   = models.CartItem
        exclude = ['cart', 'product', 'price', 'tax_rate']



CartForm = inlineformset_factory(
    parent_model= models.Cart,
    model       = models.CartItem,
    fields      = None,
    exclude     = ['product', 'package', 'price', 'tax_rate'],
    extra       = 0,
)



class OrderForm(forms.ModelForm):
    agreement = forms.BooleanField(label=_('I agree with terms and conditions'))

    class Meta:
        model   = models.Order
        exclude = ['user', 'state', 'comment']

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['delivery_method'].empty_label = None
        self.fields['payment_method'].empty_label = None



class OrderConfirmForm(forms.Form):
    pass


