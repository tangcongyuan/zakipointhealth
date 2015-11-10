"""zphalfa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'home.session.splash', name='splash'),
    url(r'^rpc/1/healthmetrics/$', 'home.healthmetrics.RPCHandler', name='rpc'),
    #url(r'^$', 'home.views.home', name='home'),
    url(r'^home$', 'home.views.home', name='home'),
    url(r'^narrow_network$', 'home.views.narrow_network', name='narrow_network'),
    url(r'^cost_pharm$', 'home.views.cost_pharm', name='cost_pharm'),
    url(r'^pop_risk$', 'home.views.pop_risk', name='pop_risk'),
    url(r'^pop_biom$', 'home.views.pop_biom', name='pop_biom'),
    url(r'^signin$', 'home.session.signin', name='signin'),
    url(r'^sign-in-form$', 'home.session.sign_in_form', name='sign_in_form'),
    url(r'^signout$', 'home.session.signout', name='signout'),
    url(r'^strategies$', 'home.views.notyet', name='home'),
    url(r'^cost_drivers$', 'home.views.notyet', name='home'),
    url(r'^cohorts$', 'home.views.notyet', name='home'),
    # url(r'^\S+/$', 'django.views.defaults.page_not_found', ),
    # url(r'^cee1/', include('cee1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^\S+/$', 'home.views.notfound', ),
]
