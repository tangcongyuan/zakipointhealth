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
    url(r'^pharm_cost$', 'home.views.pharm_cost', name='pharm_cost'),
    url(r'^signin$', 'home.session.signin', name='signin'),
    url(r'^sign-in-form$', 'home.session.sign_in_form', name='sign_in_form'),
    url(r'^signout$', 'home.session.signout', name='signout'),
    url(r'^strategies$', 'home.views.notyet', name='home'),
    url(r'^cost_drivers$', 'home.views.notyet', name='home'),
    url(r'^cohorts$', 'home.views.notyet', name='home'),
    # url(r'^cee1/', include('cee1.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # this is for ajax to get the data:
    url(r'ajax_pmpm_data/$','home.views.PMPM_DATA',name='pmpm_data'),
    url(r'ajax_strategy_data/','home.views.strategy_data',name='strategy_data')   
 #url(r'ajax_dict/$','home.views.ajax_dict',name='ajax_dict'),
)
