from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
import dgs.views

admin.autodiscover()

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', dgs.views.home, name='home'),
]
