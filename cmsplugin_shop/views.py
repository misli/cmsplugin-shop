from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import cStringIO

from cms.views import details as cms_page
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import (
    View, TemplateView, FormView, UpdateView, CreateView, DetailView
)
from os.path import basename
from xhtml2pdf import pisa

from .models import Node
from .utils import get_model, get_view, get_form


class PdfViewMixin(object):
    """
    A base view for displaying a Pdf
    """

    def get_attachment_filename(self):
        if hasattr(self, 'attachment_filename'):
            return self.attachment_filename
        filename = basename(self.request.path)
        return filename.endswith('.pdf') and filename or '{}.pdf'.format(filename)

    def get(self, request, *args, **kwargs):
        content = super(PdfViewMixin, self).get(request, *args, **kwargs).render().content

        result = cStringIO.StringIO()
        pdf = pisa.CreatePDF(cStringIO.StringIO(content), result, encoding='UTF-8')
        if pdf.err:
            raise Exception(pdf.err)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.get_attachment_filename())
        response.write(result.getvalue())
        result.close()
        return response



class CatalogView(View):
    root_view       = None
    category_view   = None
    product_view    = None

    category_model  = None
    product_model   = None

    def dispatch(self, request, path):
        slug_list = [slug for slug in path.split('/') if slug]

        # display root view, if the path is empty
        if not slug_list:
            kwargs = request.user.is_staff and {
                'categories': self.category_model.objects.filter(level=0).order_by('tree_id'),
                'products':   self.product_model.objects.filter(level=0).order_by('tree_id'),
            } or {
                'categories': self.category_model.objects.filter(level=0, active=True).order_by('tree_id'),
                'products':   self.product_model.objects.filter(level=0, active=True).order_by('tree_id'),
            }
            return self.root_view(request, **kwargs)

        # handle cms subpages
        if request.current_page.application_namespace != 'Catalog':
            return cms_page(request, path)

        # lookup node by path
        node = None
        for slug in slug_list:
            node = get_object_or_404(Node, parent=node, slug=slug)

        kwargs = {'node': node}

        # display category view
        if isinstance(node, self.category_model):
            kwargs['category'] = node
            if request.user.is_staff:
                kwargs['categories'] = node.get_children().instance_of(self.category_model)
                kwargs['products']   = node.get_children().instance_of(self.product_model)
            else:
                kwargs['categories'] = node.get_children().instance_of(self.category_model).filter(active=True)
                kwargs['products']   = node.get_children().instance_of(self.product_model).filter(active=True)
            return self.category_view(request, **kwargs)

        # or product view
        else:
            kwargs['count_in_cart'] = len([ i for i in request.cart.all_items if i.product == node ])
            kwargs['product'] = node
            return self.product_view(request, **kwargs)



class ProductView(FormView):
    form_class = get_form('CartItem')

    def get_context_data(self, **kwargs):
        self.kwargs.update(kwargs)
        return self.kwargs

    def get_form_kwargs(self):
        kwargs = super(ProductView, self).get_form_kwargs()
        kwargs['product'] = self.kwargs['product']
        return kwargs

    def form_valid(self, form):
        form.instance.cart      = self.request.cart
        form.instance.product   = self.kwargs['product']
        try:
            form.instance.save()
        except:
            item = form.instance.__class__.objects.get(
                cart    = form.instance.cart,
                product = form.instance.product,
                variant = form.instance.variant,
            )
            item.quantity += form.instance.quantity
            item.save()
        return super(ProductView, self).form_valid(form)

    def get_success_url(self):
        return self.kwargs['product'].get_absolute_url()



root        = TemplateView.as_view(template_name='cmsplugin_shop/root.html')
category    = TemplateView.as_view(template_name='cmsplugin_shop/category.html')
product     = ProductView.as_view(template_name='cmsplugin_shop/product.html')
catalog     = CatalogView.as_view(
    root_view       = get_view('root'),
    category_view   = get_view('category'),
    product_view    = get_view('product'),
    category_model  = get_model('Category'),
    product_model   = get_model('Product'),
)



class CartView(UpdateView):
    form_class = get_form('Cart')
    model = get_model('Cart')
    template_name='cmsplugin_shop/cart.html'

    def get_object(self, queryset=None):
        return self.request.cart

    def get_success_url(self):
        return self.request.cart.get_absolute_url()

cart = CartView.as_view()



class OrderFormView(CreateView):
    form_class = get_form('Order')
    model = get_model('Order')

    def form_valid(self, form):
        initial_state_code = getattr(
            settings, 'CMSPLUGIN_SHOP_INITIAL_ORDER_STATE', 'new'
        )
        OrderState = get_model('OrderState')
        try:
            state = OrderState.objects.get(code=initial_state_code)
        except OrderState.DoesNotExist:
            state = OrderState(code=initial_state_code, name='New')
            state.save()
        form.instance.state = state
        form.instance.cart  = self.request.cart
        response = super(OrderFormView, self).form_valid(form)
        del(self.request._cart)
        del(self.request.session['cart_id'])
        return response

    def get_success_url(self):
        return reverse('Order:confirm', kwargs={'slug':self.object.slug})

order_form = OrderFormView.as_view()



class OrderConfirmView(DetailView):
    model = get_model('Order')
    template_name_suffix = '_confirm'

order_confirm = OrderConfirmView.as_view()



class OrderPdfView(PdfViewMixin, DetailView):
    model = get_model('Order')
    template_name_suffix = '_pdf'

order_pdf = OrderPdfView.as_view()


