# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from datetime import date
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe

from .utils import get_model



class CartItemForm(forms.ModelForm):

    def __init__(self, product, *args, **kwargs):
        self.product = product
        super(CartItemForm, self).__init__(*args, **kwargs)
        if self.product.all_variants:
            self.fields['variant'].widget.choices = tuple(
                (variant.id, str(variant))
                for variant in self.product.all_variants
            )
        else:
            del(self.fields['variant'])

    class Meta:
        model   = get_model('CartItem')
        exclude = ['cart', 'product']



CartForm = inlineformset_factory(
    parent_model= get_model('Cart'),
    model       = get_model('CartItem'),
    fields      = None,
    exclude     = ['product', 'variant'],
    extra       = 0,
)



class OrderForm(forms.ModelForm):

    class Meta:
        model   = get_model('Order')
        exclude = ['state', 'slug']



