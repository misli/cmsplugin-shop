# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cmsplugin_shop.models
import django.db.models.deletion
import djangocms_text_ckeditor.fields
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('cmsplugin_shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='name')),
                ('slug', models.SlugField(max_length=250, verbose_name='slug')),
                ('summary', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='summary', blank=True)),
                ('valid_from', models.DateTimeField(verbose_name='valid_from')),
                ('valid_to', models.DateTimeField(verbose_name='valid_to')),
                ('relative_discount', models.DecimalField(null=True, verbose_name='relative discount', max_digits=8, decimal_places=4, blank=True)),
                ('nominal_discount', cmsplugin_shop.models.PriceField(null=True, verbose_name='nominal discount', max_digits=9, decimal_places=2, blank=True)),
                ('one_time', models.BooleanField(default=False, verbose_name='one time')),
                ('min_price', cmsplugin_shop.models.PriceField(null=True, verbose_name='minimal price', max_digits=9, decimal_places=2, blank=True)),
                ('categories', models.ManyToManyField(db_constraint='categories', to='cmsplugin_shop.Category', blank=True)),
                ('delivery_methods', models.ManyToManyField(to='cmsplugin_shop.DeliveryMethod', verbose_name='delivery methods', blank=True)),
                ('payment_methods', models.ManyToManyField(to='cmsplugin_shop.PaymentMethod', verbose_name='payment methods', blank=True)),
                ('photo', filer.fields.image.FilerImageField(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Fotka', blank=True, to='filer.Image', null=True)),
            ],
            options={
                'verbose_name': 'voucher',
                'verbose_name_plural': 'vouchers',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='voucher_exclude',
            field=models.BooleanField(default=False, verbose_name='excluded from vouchers'),
        ),
        migrations.AlterField(
            model_name='order',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='productpackage',
            name='relative_discount',
            field=models.DecimalField(null=True, verbose_name='relative discount', max_digits=8, decimal_places=4, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='voucher',
            field=models.ForeignKey(related_name='orders', verbose_name='voucher', blank=True, to='cmsplugin_shop.Voucher', null=True),
        ),
    ]
