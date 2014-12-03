from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import cStringIO

from cms.views import details as cms_page
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DetailView, FormView, ListView,
    TemplateView, UpdateView, View,
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
            item = form.instance.__class__.objects.get(
                cart    = form.instance.cart,
                product = form.instance.product,
                variant = form.instance.variant,
            )
            item.quantity += form.instance.quantity
            item.save()
        except form.instance.__class__.DoesNotExist:
            form.instance.save()
        messages.add_message(self.request, messages.INFO,
            mark_safe(_('Product has been added to <a href="{}">shopping cart</a>').format(reverse('Cart:cart')))
        )
        return super(ProductView, self).form_valid(form)

    def get_success_url(self):
        if 'add-and-cart' in self.request.POST:
            return reverse('Cart:cart')
        else:
            return self.kwargs['product'].get_absolute_url()



# catalog views
root        = TemplateView.as_view(template_name='cmsplugin_shop/root.html')
category    = TemplateView.as_view(template_name='cmsplugin_shop/category.html')
product     = ProductView.as_view(template_name='cmsplugin_shop/product.html')



class CatalogView(View):
    root_view       = staticmethod(get_view('root'))
    category_view   = staticmethod(get_view('category'))
    product_view    = staticmethod(get_view('product'))

    category_model  = get_model('Category')
    product_model   = get_model('Product')

    def dispatch(self, request, path):
        slug_list = [slug for slug in path.split('/') if slug]

        # do not allow disabled nodes if user is not staff
        if request.user.is_staff:
            active = {}
        else:
            active = {'active':True}

        # display root view, if the path is empty
        if not slug_list:
            return self.root_view(request,
                categories  = self.category_model.objects.filter(parent=None, **active),
                products    = self.product_model.objects.filter(parent=None, **active),
            )

        # handle cms subpages
        if request.current_page.application_namespace != 'Catalog':
            return cms_page(request, path)

        # lookup node by path
        node = None
        for slug in slug_list:
            node = get_object_or_404(Node, parent=node, slug=slug, **active)

        # display product view
        try:
            product = node.product
            return self.product_view(request,
                count_in_cart   = sum([ i.quantity for i in request.cart.all_items if i.product == product ]),
                node            = product,
                product         = product,
            )
        except self.product_model.DoesNotExist:
            # or category view
            category = node.category
            return self.category_view(request,
                node        = category,
                category    = category,
                categories  = self.category_model.objects.filter(parent=node, **active),
                products    = self.product_model.objects.filter(parent=node, **active),
            )

catalog = CatalogView.as_view()



class CartView(UpdateView):
    form_class      = get_form('Cart')
    model           = get_model('Cart')
    template_name   = 'cmsplugin_shop/cart.html'

    def get_object(self, queryset=None):
        return self.request.cart

    def get_success_url(self):
        if 'update-and-order' in self.request.POST:
            return reverse('Order:form')
        else:
            return reverse('Cart:cart')

cart = CartView.as_view()



class OrderFormView(SessionWizardView):
    order_model         = get_model('Order')
    order_state_model   = get_model('OrderState')
    template_name       = 'cmsplugin_shop/order_form.html'
    form_list           = [
        get_form('Order'),
        get_form('OrderConfirm')
    ]
    initial_state_code = getattr(
        settings, 'CMSPLUGIN_SHOP_INITIAL_ORDER_STATE', 'new'
    )
    profile_attr = getattr(
        settings, 'AUTH_USER_PROFILE_ATTRIBUTE', 'profile'
    )

    def get_form_initial(self, step):
        initial = {}
        if step == '0' and self.request.user.is_authenticated():
            for attr in 'first_name', 'last_name', 'email':
                if hasattr(self.request.user, attr):
                    initial[attr] = getattr(self.request.user, attr)
            if hasattr(self.request.user, self.profile_attr):
                profile = getattr(self.request.user, self.profile_attr)
                for attr in 'phone', 'address':
                    if hasattr(profile, attr):
                        initial[attr] = getattr(profile, attr)
        return initial

    def get_order(self):
        # create order using data from first form
        order = self.order_model(**self.get_cleaned_data_for_step('0'))

        # find get initial order_state
        try:
            state = self.order_state_model.objects.get(code=self.initial_state_code)
        except self.order_state_model.DoesNotExist:
            state = self.order_state_model(code=self.initial_state_code, name='New')
            state.save()

        # set order.state and cart
        order.state = state
        order.cart  = self.request.cart
        if self.request.user.is_authenticated():
            order.user = self.request.user
        return order

    def get_context_data(self, form, **kwargs):
        context = super(OrderFormView, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            context.update({'order': self.get_order()})
        return context

    def done(self, form_list, **kwargs):
        # get order
        order = self.get_order()

        # save order
        order.save()

        # confirm url
        confirm_url = reverse('Order:confirm', kwargs={'slug':order.slug})

        # site
        site = Site.objects.get_current()

        # send mail
        mail_managers(
            _('New Order'),
            _('New order has been submitted in Your e-shop.\n{}').format(
                'https://{}{}'.format(site.domain, confirm_url)
            ),
        )

        # redirect to order detail
        return HttpResponseRedirect(confirm_url)

order_form = OrderFormView.as_view()



class OrderConfirmView(DetailView):
    model = get_model('Order')
    template_name_suffix = '_confirm'

order_confirm = OrderConfirmView.as_view()



class OrderPdfView(PdfViewMixin, DetailView):
    model = get_model('Order')
    template_name_suffix = '_pdf'

order_pdf = OrderPdfView.as_view()



class MyOrdersView(ListView):
    model = get_model('Order')
    template_name = 'cmsplugin_shop/my_orders.html'

    def get_queryset(self):
        user = self.request.user
        return self.model._default_manager.filter(user=user)

    def get_context_data(self):
        context = super(MyOrdersView, self).get_context_data()
        context['orders'] = context['object_list']
        return context

my_orders = login_required(MyOrdersView.as_view())


