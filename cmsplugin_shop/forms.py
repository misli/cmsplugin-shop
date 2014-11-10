# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from datetime import date
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from tagging.forms import TagField
from tagging.utils import edit_string_for_tags

from .utils import get_model



class ProductForm(forms.ModelForm):
    tags = TagField(required=False, help_text=_(
        'Enter space separated list of single word tags ' \
        'or comma separated list of tags containing spaces. ' \
        'Use doublequotes to enter name containing comma.'
    ))

    class Meta:
        model   = get_model('Product')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.initial['tags'] = edit_string_for_tags(self.instance.tags.all())

    def save(self, commit=True):
        product = super(ProductForm, self).save(commit)
        product.tags = self.cleaned_data['tags']
        return product


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
        exclude = ['user', 'state', 'comment']



class OrderConfirmForm(forms.Form):
    agreement = forms.BooleanField(label=_('I agree with terms and conditions'))
    pass


