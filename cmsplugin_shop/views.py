from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import cStringIO

from cms.views import details as cms_page
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DetailView, FormView, ListView,
    TemplateView, UpdateView, View,
)
from os.path import basename
from xhtml2pdf import pisa

from . import models, settings
from .utils import get_view, get_form



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
        self.request.save_cart()
        form.instance.cart      = self.request.cart
        form.instance.product   = self.kwargs['product']
        try:
            item = form.instance.__class__.objects.get(
                cart    = form.instance.cart,
                product = form.instance.product,
                package = form.instance.package,
            )
            item.quantity += form.instance.quantity
            item.save()
        except form.instance.__class__.DoesNotExist:
            form.instance.tax_rate = form.instance.product.tax_rate
            form.instance.price = form.instance.package \
                                and form.instance.package.price \
                                 or form.instance.product.price
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

    category_model  = models.Category
    product_model   = models.Product

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
            node = get_object_or_404(models.Node, parent=node, slug=slug, **active)

        # display product view
        try:
            product = node.product
            return self.product_view(request,
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
    model           = models.Cart
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
    template_name       = 'cmsplugin_shop/order_form.html'
    form_list           = [
        get_form('Order'),
        get_form('OrderConfirm')
    ]

    def get_form_initial(self, step):
        initial = {}
        if step == '0' and self.request.user.is_authenticated():
            for attr in 'first_name', 'last_name', 'email':
                if hasattr(self.request.user, attr):
                    initial[attr] = getattr(self.request.user, attr)
            if hasattr(self.request.user, settings.PROFILE_ATTRIBUTE):
                profile = getattr(self.request.user, settings.PROFILE_ATTRIBUTE)
                for attr in 'phone', 'address':
                    if hasattr(profile, attr):
                        initial[attr] = getattr(profile, attr)
        return initial

    def get_order(self):
        # create order using data from first form
        order = models.Order()
        for attr, value in self.get_cleaned_data_for_step('0').items():
            setattr(order, attr, value)

        # find get initial order_state
        try:
            state = models.OrderState.objects.get(code=settings.INITIAL_ORDER_STATE)
        except models.OrderState.DoesNotExist:
            state = models.OrderState(code=settings.INITIAL_ORDER_STATE, name='New')
            state.save()

        # set order.state and cart
        self.request.save_cart()
        order.cart  = self.request.cart
        order.state = state
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

        # context
        context = RequestContext(self.request, {
            'site':  Site.objects.get_current(),
            'order': order,
        })

        send_mass_mail(((
                _('Order accepted'),
                get_template('cmsplugin_shop/order_customer_mail.txt').render(context),
                settings.SHOP_EMAIL,
                [order.email]
            ), (
                _('New order received'),
                get_template('cmsplugin_shop/order_manager_mail.txt').render(context),
                settings.SHOP_EMAIL,
                map(lambda m: u'"{}" <{}>'.format(m[0], m[1]), settings.settings.MANAGERS),
            )),
            **settings.SEND_MAIL_KWARGS
        )

        messages.add_message(self.request, messages.INFO, mark_safe(_(
            'Your order has been accepted. The confirmation email has been sent to {}.'
        ).format(order.email)))

        # redirect to order detail
        return HttpResponseRedirect(order.get_absolute_url())

order_form = OrderFormView.as_view()



class OrderDetailView(DetailView):
    model = models.Order

    def get_queryset(self):
        return super(OrderDetailView, self).get_queryset().filter(user = None)


class MyOrderDetailView(DetailView):
    model = models.Order

    def get_queryset(self):
        return super(MyOrderDetailView, self).get_queryset().filter(user = self.request.user)


class OrderPdfView(PdfViewMixin, OrderDetailView):
    template_name_suffix = '_pdf'


class MyOrderPdfView(PdfViewMixin, MyOrderDetailView):
    template_name_suffix = '_pdf'


order_detail    = OrderDetailView.as_view()
order_pdf       = OrderPdfView.as_view()
my_order_detail = login_required(MyOrderDetailView.as_view())
my_order_pdf    = login_required(MyOrderPdfView.as_view())



class MyOrdersView(ListView):
    model = models.Order

    def get_queryset(self):
        user = self.request.user
        return self.model._default_manager.filter(user=user)

    def get_context_data(self):
        context = super(MyOrdersView, self).get_context_data()
        context['orders'] = context['object_list']
        return context

my_orders = login_required(MyOrdersView.as_view())


