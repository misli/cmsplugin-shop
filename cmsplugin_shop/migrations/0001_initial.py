# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Node'
        db.create_table(u'cmsplugin_shop_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.node_set', null=True, to=orm['contenttypes.ContentType'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('parent', self.gf('polymorphic_tree.models.PolymorphicTreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['cmsplugin_shop.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=250)),
            ('summary', self.gf('djangocms_text_ckeditor.fields.HTMLField')(default=u'', blank=True)),
            ('description', self.gf('djangocms_text_ckeditor.fields.HTMLField')(default=u'', blank=True)),
            ('page_title', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('menu_title', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('meta_desc', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Node'])

        # Adding unique constraint on 'Node', fields ['parent', 'slug']
        db.create_unique(u'cmsplugin_shop_node', ['parent_id', 'slug'])

        # Adding model 'Category'
        db.create_table(u'cmsplugin_shop_category', (
            (u'node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cmsplugin_shop.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Category'])

        # Adding model 'Product'
        db.create_table(u'cmsplugin_shop_product', (
            (u'node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cmsplugin_shop.Node'], unique=True, primary_key=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('unit_price', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Product'])

        # Adding model 'ProductVariant'
        db.create_table(u'cmsplugin_shop_productvariant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.productvariant_set', null=True, to=orm['contenttypes.ContentType'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'variants', to=orm['cmsplugin_shop.Product'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('unit_price', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['ProductVariant'])

        # Adding model 'Cart'
        db.create_table(u'cmsplugin_shop_cart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.cart_set', null=True, to=orm['contenttypes.ContentType'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Cart'])

        # Adding model 'CartItem'
        db.create_table(u'cmsplugin_shop_cartitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.cartitem_set', null=True, to=orm['contenttypes.ContentType'])),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'items', to=orm['cmsplugin_shop.Cart'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', to=orm['cmsplugin_shop.Product'])),
            ('variant', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['cmsplugin_shop.ProductVariant'])),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['CartItem'])

        # Adding unique constraint on 'CartItem', fields ['cart', 'product', 'variant']
        db.create_unique(u'cmsplugin_shop_cartitem', ['cart_id', 'product_id', 'variant_id'])

        # Adding model 'Shipping'
        db.create_table(u'cmsplugin_shop_shipping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.shipping_set', null=True, to=orm['contenttypes.ContentType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('djangocms_text_ckeditor.fields.HTMLField')(default=u'', blank=True)),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Shipping'])

        # Adding model 'OrderState'
        db.create_table(u'cmsplugin_shop_orderstate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.orderstate_set', null=True, to=orm['contenttypes.ContentType'])),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('djangocms_text_ckeditor.fields.HTMLField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['OrderState'])

        # Adding model 'Order'
        db.create_table(u'cmsplugin_shop_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cmsplugin_shop.order_set', null=True, to=orm['contenttypes.ContentType'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_shop.OrderState'])),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_shop.Cart'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=150)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('shipping', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_shop.Shipping'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['Order'])

        # Adding model 'ProductPlugin'
        db.create_table(u'cmsplugin_shop_productplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_shop.Product'])),
            ('template', self.gf('django.db.models.fields.CharField')(default=u'default', max_length=100)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['ProductPlugin'])

        # Adding model 'CategoryPlugin'
        db.create_table(u'cmsplugin_shop_categoryplugin', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_shop.Category'])),
            ('template', self.gf('django.db.models.fields.CharField')(default=u'default', max_length=100)),
        ))
        db.send_create_signal(u'cmsplugin_shop', ['CategoryPlugin'])


    def backwards(self, orm):
        # Removing unique constraint on 'CartItem', fields ['cart', 'product', 'variant']
        db.delete_unique(u'cmsplugin_shop_cartitem', ['cart_id', 'product_id', 'variant_id'])

        # Removing unique constraint on 'Node', fields ['parent', 'slug']
        db.delete_unique(u'cmsplugin_shop_node', ['parent_id', 'slug'])

        # Deleting model 'Node'
        db.delete_table(u'cmsplugin_shop_node')

        # Deleting model 'Category'
        db.delete_table(u'cmsplugin_shop_category')

        # Deleting model 'Product'
        db.delete_table(u'cmsplugin_shop_product')

        # Deleting model 'ProductVariant'
        db.delete_table(u'cmsplugin_shop_productvariant')

        # Deleting model 'Cart'
        db.delete_table(u'cmsplugin_shop_cart')

        # Deleting model 'CartItem'
        db.delete_table(u'cmsplugin_shop_cartitem')

        # Deleting model 'Shipping'
        db.delete_table(u'cmsplugin_shop_shipping')

        # Deleting model 'OrderState'
        db.delete_table(u'cmsplugin_shop_orderstate')

        # Deleting model 'Order'
        db.delete_table(u'cmsplugin_shop_order')

        # Deleting model 'ProductPlugin'
        db.delete_table(u'cmsplugin_shop_productplugin')

        # Deleting model 'CategoryPlugin'
        db.delete_table(u'cmsplugin_shop_categoryplugin')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'cmsplugin_shop.cart': {
            'Meta': {'object_name': 'Cart'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.cart_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'cmsplugin_shop.cartitem': {
            'Meta': {'unique_together': "[(u'cart', u'product', u'variant')]", 'object_name': 'CartItem'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'items'", 'to': u"orm['cmsplugin_shop.Cart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.cartitem_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'to': u"orm['cmsplugin_shop.Product']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'variant': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['cmsplugin_shop.ProductVariant']"})
        },
        u'cmsplugin_shop.category': {
            'Meta': {'object_name': 'Category', '_ormbases': [u'cmsplugin_shop.Node']},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cmsplugin_shop.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'cmsplugin_shop.categoryplugin': {
            'Meta': {'object_name': 'CategoryPlugin', '_ormbases': ['cms.CMSPlugin']},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_shop.Category']"}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "u'default'", 'max_length': '100'})
        },
        u'cmsplugin_shop.node': {
            'Meta': {'unique_together': "[(u'parent', u'slug')]", 'object_name': 'Node'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'menu_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'meta_desc': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'page_title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'parent': ('polymorphic_tree.models.PolymorphicTreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['cmsplugin_shop.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.node_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '250'}),
            'summary': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "u''", 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'cmsplugin_shop.order': {
            'Meta': {'object_name': 'Order'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_shop.Cart']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '150'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.order_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'shipping': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_shop.Shipping']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_shop.OrderState']"})
        },
        u'cmsplugin_shop.orderstate': {
            'Meta': {'object_name': 'OrderState'},
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'description': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.orderstate_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'cmsplugin_shop.product': {
            'Meta': {'object_name': 'Product', '_ormbases': [u'cmsplugin_shop.Node']},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cmsplugin_shop.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'unit_price': ('django.db.models.fields.IntegerField', [], {})
        },
        u'cmsplugin_shop.productplugin': {
            'Meta': {'object_name': 'ProductPlugin', '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_shop.Product']"}),
            'template': ('django.db.models.fields.CharField', [], {'default': "u'default'", 'max_length': '100'})
        },
        u'cmsplugin_shop.productvariant': {
            'Meta': {'object_name': 'ProductVariant'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.productvariant_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'variants'", 'to': u"orm['cmsplugin_shop.Product']"}),
            'unit_price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cmsplugin_shop.shipping': {
            'Meta': {'object_name': 'Shipping'},
            'description': ('djangocms_text_ckeditor.fields.HTMLField', [], {'default': "u''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cmsplugin_shop.shipping_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'price': ('django.db.models.fields.IntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cmsplugin_shop']