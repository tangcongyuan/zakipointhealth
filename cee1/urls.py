from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'home.session.splash', name='splash'),
    #url(r'^$', 'home.views.home', name='home'),
    url(r'^home$', 'home.views.home', name='home'),
    url(r'^signin$', 'home.session.signin', name='signin'),
    url(r'^sign-in-form$', 'home.session.sign_in_form', name='sign_in_form'),
    url(r'^signout$', 'home.session.signout', name='signout'),
    url(r'^costs$', 'home.views.notyet', name='home'),
    url(r'^progs$', 'home.views.notyet', name='home'),
    url(r'^eHlth$', 'home.views.notyet', name='home'),
    url(r'^qCare$', 'home.views.notyet', name='home'),
    # url(r'^cee1/', include('cee1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
