from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
import dgs

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'dgs.views.home', name='home'),
)
