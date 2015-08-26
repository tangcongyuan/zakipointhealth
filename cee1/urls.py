from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'home.session.splash', name='splash'),
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
    url(r'^\S+/$', 'home.views.notfound', ),
    # url(r'^\S+/$', 'django.views.defaults.page_not_found', ),
    # url(r'^cee1/', include('cee1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
