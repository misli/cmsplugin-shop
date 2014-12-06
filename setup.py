# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name         = "cmsplugin_shop",
    version      = '0.2',
    description  = "Extensible E-Shop plugin for djangoCMS",
    author       = "Jakub Dorňák",
    author_email = "jdornak@redhat.com",
    url          = "https://github.com/misli/cmsplugin-shop",
    packages     = find_packages(),
    include_package_data = True,
)

