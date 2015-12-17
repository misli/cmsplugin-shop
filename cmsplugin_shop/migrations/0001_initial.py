# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cmsplugin_shop.models
import mptt.fields
import djangocms_text_ckeditor.fields
import django.db.models.deletion
from django.conf import settings
import django.core.validators
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0001_initial'),
        ('cms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
            ],
            options={
                'verbose_name': 'cart',
                'verbose_name_plural': 'carts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='quantity')),
                ('price', cmsplugin_shop.models.PriceField(verbose_name='price', max_digits=9, decimal_places=2)),
                ('tax_rate', cmsplugin_shop.models.TaxRateField(default=0, verbose_name='tax rate', max_digits=9, decimal_places=4, choices=[(0, 'no tax')])),
                ('cart', models.ForeignKey(related_name='items', verbose_name='cart', to='cmsplugin_shop.Cart')),
            ],
            options={
                'verbose_name': 'cart item',
                'verbose_name_plural': 'cart items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(default='default', help_text='the template used to render plugin', max_length=100, verbose_name='template', choices=[('default', 'default')])),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='DeliveryMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.SlugField(verbose_name='code')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='description', blank=True)),
                ('price', cmsplugin_shop.models.PriceField(verbose_name='price', max_digits=9, decimal_places=2)),
                ('tax_rate', cmsplugin_shop.models.TaxRateField(default=0, verbose_name='tax rate', max_digits=9, decimal_places=4, choices=[(0, 'no tax')])),
                ('ordering', models.PositiveIntegerField(default=1, verbose_name='ordering')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'verbose_name': 'delivery method',
                'verbose_name_plural': 'delivery methods',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='name')),
                ('slug', models.SlugField(max_length=250, verbose_name='slug')),
                ('summary', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='summary', blank=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='description', blank=True)),
                ('page_title', models.CharField(help_text='overwrite the title (html title tag)', max_length=250, null=True, verbose_name='page title', blank=True)),
                ('menu_title', models.CharField(help_text='overwrite the title in the menu', max_length=250, null=True, verbose_name='menu title', blank=True)),
                ('meta_desc', models.TextField(default='', help_text='the text displayed in search engines', verbose_name='meta description', blank=True)),
                ('active', models.BooleanField(default=False, verbose_name='active')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'tree node',
                'verbose_name_plural': 'tree nodes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cmsplugin_shop.Node')),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=('cmsplugin_shop.node',),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(editable=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('email', models.EmailField(max_length=75, verbose_name='email')),
                ('phone', models.CharField(max_length=150, verbose_name='phone', validators=[django.core.validators.RegexValidator('^\\+?[0-9 ]+$')])),
                ('address', models.TextField(verbose_name='address')),
                ('note', models.TextField(verbose_name='note', blank=True)),
                ('comment', models.TextField(verbose_name='internal comment', blank=True)),
                ('cart', models.OneToOneField(editable=False, to='cmsplugin_shop.Cart', verbose_name='cart')),
                ('delivery_method', models.ForeignKey(verbose_name='delivery method', to='cmsplugin_shop.DeliveryMethod')),
            ],
            options={
                'ordering': ('-date',),
                'verbose_name': 'order',
                'verbose_name_plural': 'orders',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.SlugField(verbose_name='code')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'order state',
                'verbose_name_plural': 'order states',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.SlugField(verbose_name='code')),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='description', blank=True)),
                ('price', cmsplugin_shop.models.PriceField(verbose_name='price', max_digits=9, decimal_places=2)),
                ('tax_rate', cmsplugin_shop.models.TaxRateField(default=0, verbose_name='tax rate', max_digits=9, decimal_places=4, choices=[(0, 'no tax')])),
                ('ordering', models.PositiveIntegerField(default=1, verbose_name='ordering')),
            ],
            options={
                'ordering': ('ordering', 'name'),
                'verbose_name': 'payment method',
                'verbose_name_plural': 'payment methods',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('node_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cmsplugin_shop.Node')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('multiple', models.IntegerField(default=1, verbose_name='multiple')),
                ('unit', models.CharField(max_length=30, null=True, verbose_name='unit', blank=True)),
                ('price', cmsplugin_shop.models.PriceField(verbose_name='price', max_digits=9, decimal_places=2)),
                ('tax_rate', cmsplugin_shop.models.TaxRateField(default=0, verbose_name='tax rate', max_digits=9, decimal_places=4, choices=[(0, 'no tax')])),
                ('related', models.ManyToManyField(related_name='related_rel_+', db_constraint='related products', to='cmsplugin_shop.Product', blank=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
            bases=('cmsplugin_shop.node',),
        ),
        migrations.CreateModel(
            name='ProductPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('multiple', models.IntegerField(verbose_name='multiple')),
                ('name', models.CharField(max_length=250, null=True, verbose_name='name', blank=True)),
                ('price', cmsplugin_shop.models.PriceField(null=True, verbose_name='price', max_digits=9, decimal_places=2, blank=True)),
                ('relative_discount', models.DecimalField(decimal_places=4, default=1, max_digits=8, blank=True, null=True, verbose_name='relative discount')),
                ('nominal_discount', cmsplugin_shop.models.PriceField(null=True, verbose_name='nominal discount', max_digits=9, decimal_places=2, blank=True)),
                ('product', models.ForeignKey(related_name='packages', verbose_name='product', to='cmsplugin_shop.Product')),
            ],
            options={
                'ordering': ('multiple',),
                'verbose_name': 'product package',
                'verbose_name_plural': 'product packages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('template', models.CharField(default='default', help_text='the template used to render plugin', max_length=100, verbose_name='template', choices=[('default', 'default')])),
                ('product', models.ForeignKey(verbose_name='product', to='cmsplugin_shop.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.ForeignKey(verbose_name='payment method', to='cmsplugin_shop.PaymentMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.ForeignKey(verbose_name='state', to='cmsplugin_shop.OrderState'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', verbose_name='category', blank=True, to='cmsplugin_shop.Node', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='photo',
            field=filer.fields.image.FilerImageField(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Fotka', blank=True, to='filer.Image', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together=set([('parent', 'slug')]),
        ),
        migrations.AddField(
            model_name='categoryplugin',
            name='category',
            field=models.ForeignKey(verbose_name='category', to='cmsplugin_shop.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartitem',
            name='package',
            field=models.ForeignKey(related_name='+', verbose_name='product package', to='cmsplugin_shop.ProductPackage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(related_name='+', verbose_name='product', to='cmsplugin_shop.Product'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together=set([('cart', 'product', 'package')]),
        ),
    ]
